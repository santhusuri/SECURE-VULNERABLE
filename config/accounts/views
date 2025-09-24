from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from .models import VulnUser  # Vulnerable user model for SQLi demo
from security_client import send_security_event  # << Project B integration

User = get_user_model()  # Use Django’s custom User model if overridden

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def register_view(request):
    user_ip = get_client_ip(request)
    mode = request.session.get('sim_mode', 'secure')  # Unified mode key here
    if mode == 'vulnerable' and settings.VULNERABLE_LABS.get('weak_password_hash'):
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            VulnUser.objects.create(username=username, password=password)
            messages.warning(request, "Registered with WEAK password storage (vulnerable mode).")
            event_msg = f"Vulnerable Registration: username='{username}', password='{password}'"
            send_security_event(event_msg, user_ip)
            return redirect('accounts:login')
        return render(request, 'accounts/vuln_register.html')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            username = form.cleaned_data.get("username")
            event_msg = f"Secure Registration: username='{username}'"
            send_security_event(event_msg, user_ip)
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    user_ip = get_client_ip(request)
    mode = request.session.get('sim_mode', 'secure')  # Unified mode key here
    if mode == 'vulnerable':
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            send_security_event(f"Vulnerable Login attempt: username='{username}', password='{password}'", user_ip)
            query = f"SELECT id FROM accounts_vulnuser WHERE username='{username}' AND password='{password}'"
            with connection.cursor() as cursor:
                cursor.execute(query)
                row = cursor.fetchone()
            if row:
                try:
                    secure_user = User.objects.get(username="secure_user")
                    login(request, secure_user)
                    messages.warning(request, "Logged in via Vulnerable Mode (SQLi bypass).")
                    return redirect('accounts:profile')
                except User.DoesNotExist:
                    messages.error(request, "Secure user not found. Cannot complete login.")
                    return redirect('accounts:login')
            else:
                messages.error(request, "Invalid credentials (or SQLi failed).")
        return render(request, 'accounts/vuln_login.html')
    else:
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

import os
import uuid
import random
from io import BytesIO
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone

from PIL import Image, UnidentifiedImageError

from .models import User
from .views import get_client_ip  # adjust import if needed
from security_client import send_security_event

# Secure-mode config
ALLOWED_IMAGE_EXTS = {"jpg", "jpeg", "png", "gif"}
MAX_UPLOAD_SIZE = 2 * 1024 * 1024  # 2 MB


@login_required
def profile_view(request):
    """
    Profile page. Behavior depends on session['sim_mode']:
    - secure: validate extension, size, and image integrity (Pillow). Pass allowed_exts to template.
    - vulnerable: intentionally skip validation and save with original filename (lab/demo only).
    """
    mode = request.session.get("sim_mode", "secure")
    user = request.user
    user_ip = get_client_ip(request)

    if request.method == "POST":
        # update address & phone in both modes
        if "address" in request.POST:
            user.address = request.POST.get("address", "").strip()
        if "phone" in request.POST:
            user.phone = request.POST.get("phone", "").strip()

        uploaded_file = request.FILES.get("photo")

        if mode == "secure":
            if uploaded_file:
                # size check (safe to use before reading the stream)
                if uploaded_file.size > MAX_UPLOAD_SIZE:
                    messages.error(request, f"File too large. Max {MAX_UPLOAD_SIZE // (1024*1024)} MB.")
                else:
                    # extension from original filename (used for saved filename)
                    ext = os.path.splitext(uploaded_file.name)[1].lstrip(".").lower() or "jpg"
                    if ext not in ALLOWED_IMAGE_EXTS:
                        messages.error(
                            request,
                            f"Extension '.{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_IMAGE_EXTS))}."
                        )
                    else:
                        # READ ONCE into memory
                        content = uploaded_file.read()
                        if not content:
                            messages.error(request, "Uploaded file is empty.")
                        else:
                            # validate image bytes using Pillow via BytesIO
                            try:
                                Image.open(BytesIO(content)).verify()
                            except (UnidentifiedImageError, Exception):
                                messages.error(request, "Uploaded file is not a valid image.")
                            else:
                                safe_filename = f"{uuid.uuid4().hex}.{ext}"
                                saved_path = default_storage.save(
                                    os.path.join("profile_photos", safe_filename),
                                    ContentFile(content)
                                )
                                user.photo = saved_path
                                user.save()
                                messages.success(request, "Profile photo uploaded securely.")
            else:
                # no file uploaded, just save other fields
                user.save()

            send_security_event(f"Secure Profile Update by user={user.username}", user_ip)

        elif mode == "vulnerable":
            # intentionally vulnerable: no validation, original filename preserved
            if uploaded_file:
                # Read bytes once and save with original name (vulnerable by design)
                content = uploaded_file.read()
                saved_path = default_storage.save(
                    os.path.join("profile_photos", uploaded_file.name),
                    ContentFile(content)
                )
                user.photo = saved_path
                messages.warning(request, "Profile photo uploaded (VULNERABLE MODE).")
            user.save()
            send_security_event(f"Vulnerable Profile Update RAW FILE UPLOAD by user={user.username}", user_ip)

        return redirect("accounts:profile")

    # GET -> render template; in secure mode provide allowed_exts to show on page
    context = {
        "mode": mode,
    }
    if mode == "secure":
        context["allowed_exts"] = sorted(ALLOWED_IMAGE_EXTS)

    return render(request, "accounts/profile.html", context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

import logging
logger = logging.getLogger(__name__)

def toggle_mode(request):
    current_mode = request.session.get('sim_mode', 'secure')
    new_mode = 'vulnerable' if current_mode == 'secure' else 'secure'
    request.session['sim_mode'] = new_mode
    request.session.save()
    logger.info(f"Toggled mode from {current_mode} to {new_mode}")
    return JsonResponse({"mode": new_mode})


