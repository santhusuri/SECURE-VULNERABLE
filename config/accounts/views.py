# accounts/views.py
# LAB ONLY: intentionally vulnerable pieces for testing SQLi, XSS and brute-force.
# DO NOT DEPLOY THIS FILE OR ITS ROUTES TO PRODUCTION.

import os
import uuid
import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.conf import settings
from django.db import connection
from django.http import JsonResponse, HttpResponseForbidden
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # <-- correct import location

from .forms import RegistrationForm, LoginForm, VulnRegistrationForm
from .models import VulnUser  # intentionally vulnerable user model for lab
from security_client import send_security_event  # integration to your logger/monitor

User = get_user_model()
logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


def is_vulnerable_mode(request):
    """
    Check if session is in vulnerable mode.
    """
    session_mode = request.session.get("sim_mode", getattr(settings, "SIMULATION_MODE", "secure"))
    return session_mode == "vulnerable"


# -------------------- Registration --------------------
def register_view(request):
    user_ip = get_client_ip(request)
    mode = "vulnerable" if is_vulnerable_mode(request) else "secure"

    if mode == "vulnerable" and getattr(settings, "VULNERABLE_LABS", {}).get("weak_password_hash", True):
        if request.method == "POST":
            form = VulnRegistrationForm(request.POST)
            if form.is_valid():
                VulnUser.objects.create(
                    username=form.cleaned_data["username"],
                    password=form.cleaned_data["password"],  # plaintext (lab only)
                    email=form.cleaned_data.get("email", ""),
                )
                messages.warning(request, "Registered (VULNERABLE): plaintext password stored.")
                send_security_event(f"Vulnerable Registration: username='{form.cleaned_data['username']}'", user_ip)
                return redirect("accounts:vuln_login")
        else:
            form = VulnRegistrationForm()
        return render(request, "accounts/vuln_register.html", {"form": form})

    # Secure flow
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful. Please log in.")
            username = form.cleaned_data.get("username")
            send_security_event(f"Secure Registration: username='{username}'", user_ip)
            return redirect("accounts:login")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


# -------------------- Login --------------------
def login_view(request):
    user_ip = get_client_ip(request)
    mode = "vulnerable" if is_vulnerable_mode(request) else "secure"

    if mode == "vulnerable":
        attempted_username = None
        if request.method == "POST":
            username = request.POST.get("username", "")
            password = request.POST.get("password", "")
            attempted_username = username

            send_security_event(f"VULN LOGIN ATTEMPT: username='{username}'", user_ip)

            if not getattr(settings, "VULNERABLE_LABS", {}).get("raw_sql_injection", True):
                messages.error(request, "Vulnerable SQL lab disabled.")
                return render(request, "accounts/vuln_login.html", {"attempted_username": attempted_username})

            query = f"SELECT id FROM accounts_vulnuser WHERE username = '{username}' AND password = '{password}'"
            with connection.cursor() as cursor:
                try:
                    cursor.execute(query)  # vulnerable to SQLi
                    row = cursor.fetchone()
                except Exception:
                    logger.exception("Error executing vulnerable SQL query")
                    row = None

            if row:
                try:
                    secure_user = User.objects.get(username="secure_user")
                    login(request, secure_user)
                except User.DoesNotExist:
                    pass
                messages.success(request, "Logged in (vulnerable flow).")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Invalid credentials (vulnerable login).")

        return render(request, "accounts/vuln_login.html", {"attempted_username": attempted_username})

    # Secure flow
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            send_security_event(f"Secure Login: username='{form.cleaned_data.get('username')}'", user_ip)
            return redirect("accounts:profile")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# -------------------- Profile --------------------
@login_required
def profile_view(request):
    mode = "vulnerable" if is_vulnerable_mode(request) else "secure"
    user = request.user
    user_ip = get_client_ip(request)

    if request.method == "POST":
        if "address" in request.POST:
            user.address = request.POST.get("address", "").strip()
        if "phone" in request.POST:
            user.phone = request.POST.get("phone", "").strip()

        uploaded_file = request.FILES.get("photo")

        if mode == "secure":
            MAX_UPLOAD_SIZE = 2 * 1024 * 1024
            ALLOWED_IMAGE_EXTS = {"jpg", "jpeg", "png", "gif"}
            if uploaded_file:
                if uploaded_file.size <= MAX_UPLOAD_SIZE:
                    ext = uploaded_file.name.rsplit(".", 1)[-1].lower() if "." in uploaded_file.name else ""
                    if ext in ALLOWED_IMAGE_EXTS:
                        from io import BytesIO
                        from PIL import Image, UnidentifiedImageError
                        content = uploaded_file.read()
                        try:
                            Image.open(BytesIO(content)).verify()
                        except (UnidentifiedImageError, Exception):
                            messages.error(request, "Uploaded file is not a valid image.")
                        else:
                            safe_filename = f"{uuid.uuid4().hex}.{ext}"
                            saved_path = default_storage.save(
                                os.path.join("profile_photos", safe_filename),
                                ContentFile(content),
                            )
                            user.photo = saved_path
                            user.save()
                            messages.success(request, "Profile updated (secure).")
                    else:
                        messages.error(request, "Extension not allowed.")
                else:
                    messages.error(request, "File too large.")
            else:
                user.save()
            send_security_event(f"Secure Profile Update by user={user.username}", user_ip)

        else:  # vulnerable mode
            if uploaded_file:
                content = uploaded_file.read()
                saved_path = default_storage.save(
                    os.path.join("profile_photos", uploaded_file.name),
                    ContentFile(content),
                )
                user.photo = saved_path
                messages.warning(request, "Profile photo uploaded (VULNERABLE MODE).")
            user.save()
            send_security_event(f"Vulnerable Profile Update by user={user.username}", user_ip)

        return redirect("accounts:profile")

    context = {"mode": mode}
    if mode == "secure":
        context["allowed_exts"] = sorted({"jpg", "jpeg", "png", "gif"})
    return render(request, "accounts/profile.html", context)


# -------------------- Toggle mode --------------------
@csrf_exempt
@require_POST
def toggle_mode(request):
    """
    Toggle sim_mode in the session.
    """
    current_mode = request.session.get("sim_mode", getattr(settings, "SIMULATION_MODE", "secure"))
    new_mode = "vulnerable" if current_mode != "vulnerable" else "secure"
    request.session["sim_mode"] = new_mode
    request.session.save()
    return JsonResponse({"mode": new_mode})
