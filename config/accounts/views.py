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

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

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


