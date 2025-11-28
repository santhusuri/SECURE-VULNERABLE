# core/views.py
import re
import subprocess

from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.conf import settings
from django.contrib import messages
from django.core.files.storage import default_storage
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

# Optional integration
try:
    from security_client import send_security_event
except Exception:
    def send_security_event(*args, **kwargs):
        return None


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


def home(request):
    return render(request, "main.html")


# ---------------------- Command Injection demo ----------------------
def search_view(request):
    mode = request.session.get("sim_mode", getattr(settings, "SIMULATION_MODE", "secure"))
    search_result = ""
    user_ip = get_client_ip(request)

    if request.method == "POST":
        query = request.POST.get("query", "").strip()
        if mode == "vulnerable":
            try:
                result = subprocess.check_output(
                    f"ping -c 1 {query}",
                    shell=True, stderr=subprocess.STDOUT, universal_newlines=True,
                )
                search_result = result
            except subprocess.CalledProcessError as e:
                search_result = e.output
            send_security_event(f"Vulnerable Command Injection Search: query='{query}'", user_ip)
        else:
            if re.fullmatch(r"[a-zA-Z0-9\.\-]+", query):
                try:
                    result = subprocess.check_output(["ping", "-c", "1", query], universal_newlines=True)
                    search_result = result
                except subprocess.CalledProcessError as e:
                    search_result = e.output
                send_security_event(f"Secure Command Search: query='{query}'", user_ip)
            else:
                messages.error(request, "Invalid input provided.")

    return render(request, "search.html", {"search_result": search_result, "mode": mode})


# ---------------------- File Upload demo ----------------------
def upload_view(request):
    mode = request.session.get("sim_mode", getattr(settings, "SIMULATION_MODE", "secure"))
    upload_result = ""
    user_ip = get_client_ip(request)

    if request.method == "POST" and request.FILES.get("file"):
        uploaded_file = request.FILES["file"]
        filename = request.POST.get("filename", uploaded_file.name).strip()

        if mode == "vulnerable":
            save_path = default_storage.save(filename, uploaded_file)
            try:
                result = subprocess.check_output(f"ls -al {save_path}", shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
                upload_result = result
            except subprocess.CalledProcessError as e:
                upload_result = e.output
            send_security_event(f"Vulnerable File Upload: filename='{filename}'", user_ip)

        else:
            if re.fullmatch(r"[a-zA-Z0-9_.-]+", filename):
                safe_path = default_storage.save(filename, uploaded_file)
                try:
                    result = subprocess.check_output(["ls", "-al", safe_path], universal_newlines=True)
                    upload_result = result
                except subprocess.CalledProcessError as e:
                    upload_result = e.output
                send_security_event(f"Secure File Upload: filename='{filename}'", user_ip)
            else:
                messages.error(request, "Invalid filename provided.")

    return render(request, "upload.html", {"upload_result": upload_result, "mode": mode})


# ---------------------- Staff-only toggle (optional demo) ----------------------
@staff_member_required
@require_POST
def toggle_session_simulation_mode(request):
    if not settings.DEBUG:
        raise Http404()
    current = request.session.get("sim_mode", getattr(settings, "SIMULATION_MODE", "secure"))
    new = "vulnerable" if current != "vulnerable" else "secure"
    request.session["sim_mode"] = new
    request.session.modified = True
    return redirect(request.POST.get("next", "/"))


# ---------------------- Mode status ----------------------
def mode_status(request):
    session_mode = request.session.get("sim_mode", getattr(settings, "SIMULATION_MODE", "secure"))
    return JsonResponse({"global_vulnerable_mode": True, "session_mode": session_mode})
