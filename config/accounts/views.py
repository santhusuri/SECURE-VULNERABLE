# accounts/views_lab.py
# LAB ONLY: intentionally vulnerable pieces for testing SQLi, XSS and brute-force.
# DO NOT DEPLOY THIS FILE OR ITS ROUTES TO PRODUCTION.

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.conf import settings
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import logging

from .forms import RegistrationForm, LoginForm
from .models import VulnUser  # intentionally vulnerable user model for lab
from security_client import send_security_event  # integration to your logger/monitor

User = get_user_model()
logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def register_view(request):
    """
    Registration: in vulnerable mode we intentionally store plaintext to demonstrate weak storage.
    In secure mode we use the normal RegistrationForm which should create hashed passwords.
    """
    user_ip = get_client_ip(request)
    mode = request.session.get('sim_mode', 'secure')

    # VULNERABLE registration (plaintext storage) — lab only
    if mode == 'vulnerable' and getattr(settings, "VULNERABLE_LABS", {}).get("weak_password_hash", True):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            # intentionally insecure: storing plaintext password (lab demo only)
            VulnUser.objects.create(username=username, password=password, email=email)
            messages.warning(request, "Registered (VULNERABLE): plaintext password stored.")
            send_security_event(f"Vulnerable Registration: username='{username}'", user_ip)
            return redirect('accounts:vuln_login')
        return render(request, 'accounts/vuln_register.html')

    # Secure registration (normal flow)
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            username = form.cleaned_data.get("username")
            send_security_event(f"Secure Registration: username='{username}'", user_ip)
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Combined view: switches behavior based on session['sim_mode']:
      - vulnerable mode: intentionally unsafe (raw SQL concatenation, reflected username via template)
      - secure mode: use Django auth (authenticate + login)
    """
    user_ip = get_client_ip(request)
    mode = request.session.get('sim_mode', 'secure')

    # ---------- VULNERABLE MODE ----------
    if mode == 'vulnerable':
        attempted_username = None
        if request.method == 'POST':
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')

            # Log event (lab)
            send_security_event(f"VULN LOGIN ATTEMPT: username='{username}'", user_ip)

            # keep the raw username to reflect back into template unsafely (demonstrate XSS)
            attempted_username = username

            # INTENTIONALLY VULNERABLE: raw SQL string concatenation (SQLi demo)
            # WARNING: This is for lab/test only.
            query = f"SELECT id FROM accounts_vulnuser WHERE username = '{username}' AND password = '{password}'"
            with connection.cursor() as cursor:
                cursor.execute(query)   # vulnerable to SQL injection
                row = cursor.fetchone()

            if row:
                # For demo convenience: log in a placeholder secure user (if exists),
                # otherwise just show a success message.
                try:
                    secure_user = User.objects.get(username="secure_user")
                    login(request, secure_user)
                    messages.success(request, "Logged in (vulnerable flow).")
                    return redirect('accounts:profile')
                except User.DoesNotExist:
                    messages.success(request, "Login succeeded (vulnerable flow).")
                    return redirect('home')
            else:
                messages.error(request, "Invalid credentials (vulnerable login).")
        # Render the vulnerable login template which intentionally echoes attempted_username unsafely
        return render(request, 'accounts/vuln_login.html', {"attempted_username": attempted_username})

    # ---------- SECURE MODE ----------
    # Use Django auth forms and normal protections
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            username = form.cleaned_data.get("username")
            send_security_event(f"Secure Login: username='{username}'", user_ip)
            return redirect('accounts:profile')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def profile_view(request):
    """
    Profile view — keeps your existing secure/vulnerable upload logic.
    Kept mostly as-is for lab.
    """
    mode = request.session.get("sim_mode", "secure")
    user = request.user
    user_ip = get_client_ip(request)

    if request.method == "POST":
        # updating address & phone allowed in both modes
        if "address" in request.POST:
            user.address = request.POST.get("address", "").strip()
        if "phone" in request.POST:
            user.phone = request.POST.get("phone", "").strip()

        uploaded_file = request.FILES.get("photo")

        if mode == "secure":
            # secure handling (validate size, extension, and Pillow verification)
            MAX_UPLOAD_SIZE = 2 * 1024 * 1024
            ALLOWED_IMAGE_EXTS = {"jpg", "jpeg", "png", "gif"}
            if uploaded_file:
                if uploaded_file.size > MAX_UPLOAD_SIZE:
                    messages.error(request, "File too large.")
                else:
                    ext = uploaded_file.name.rsplit('.', 1)[-1].lower() if '.' in uploaded_file.name else ''
                    if ext not in ALLOWED_IMAGE_EXTS:
                        messages.error(request, "Extension not allowed.")
                    else:
                        from io import BytesIO
                        from PIL import Image, UnidentifiedImageError
                        from django.core.files.base import ContentFile
                        import uuid, os
                        content = uploaded_file.read()
                        try:
                            Image.open(BytesIO(content)).verify()
                        except (UnidentifiedImageError, Exception):
                            messages.error(request, "Uploaded file is not a valid image.")
                        else:
                            safe_filename = f"{uuid.uuid4().hex}.{ext}"
                            saved_path = default_storage.save(os.path.join("profile_photos", safe_filename), ContentFile(content))
                            user.photo = saved_path
                            user.save()
                            messages.success(request, "Profile updated (secure).")
            else:
                user.save()
            send_security_event(f"Secure Profile Update by user={user.username}", user_ip)

        else:
            # Vulnerable mode: intentionally skip validation and save with original filename
            if uploaded_file:
                content = uploaded_file.read()
                saved_path = default_storage.save(os.path.join("profile_photos", uploaded_file.name), ContentFile(content))
                user.photo = saved_path
                messages.warning(request, "Profile photo uploaded (VULNERABLE MODE).")
            user.save()
            send_security_event(f"Vulnerable Profile Update by user={user.username}", user_ip)

        return redirect("accounts:profile")

    context = {"mode": mode}
    if mode == "secure":
        context["allowed_exts"] = sorted({"jpg", "jpeg", "png", "gif"})
    return render(request, "accounts/profile.html", context)


# ---------- LAB HELPERS ----------

def create_lab_vuln_user(request):
    """
    Helper endpoint to create a lab vulnerable user (plaintext password) quickly.
    Usage: GET /accounts/lab/create_user/  (call from local browser)
    WARNING: only intended for dev/lab environments.
    """
    if not settings.DEBUG:
        return HttpResponse("Not allowed", status=403)

    username = "lab_test_user"
    password = "labpass123"
    email = "lab@example.local"
    # Create or update a VulnUser row
    obj, created = VulnUser.objects.update_or_create(
        username=username,
        defaults={"password": password, "email": email}
    )
    return JsonResponse({"created": created, "username": username, "password": password})


def toggle_mode(request):
    """
    Toggle sim_mode between 'secure' and 'vulnerable' (session-level).
    Use this to switch the app behavior at runtime from a browser.
    """
    current_mode = request.session.get('sim_mode', 'secure')
    new_mode = 'vulnerable' if current_mode == 'secure' else 'secure'
    request.session['sim_mode'] = new_mode
    request.session.save()
    logger.info(f"Toggled mode from {current_mode} to {new_mode}")
    return JsonResponse({"mode": new_mode})
