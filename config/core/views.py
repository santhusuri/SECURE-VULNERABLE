from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
import subprocess
import re
from django.core.files.storage import default_storage
from security_client import send_security_event  # Project B integration

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

def toggle_mode(request):
    current = request.session.get('sim_mode', 'secure')
    request.session['sim_mode'] = 'vulnerable' if current == 'secure' else 'secure'
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', reverse('product_list')))

def search_view(request):
    mode = request.session.get('sim_mode', 'secure')  # unified mode key
    search_result = ''
    user_ip = get_client_ip(request)
    if request.method == 'POST':
        query = request.POST.get('query', '')
        if mode == 'vulnerable':
            try:
                result = subprocess.check_output(
                    f"ping -c 1 {query}",
                    shell=True, stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                search_result = result
            except subprocess.CalledProcessError as e:
                search_result = e.output
            send_security_event(f"Vulnerable Command Injection Search: query='{query}'", user_ip)
        else:
            if re.fullmatch(r'[a-zA-Z0-9\.\-]+', query):
                try:
                    result = subprocess.check_output(
                        ['ping', '-c', '1', query],
                        universal_newlines=True
                    )
                    search_result = result
                except subprocess.CalledProcessError as e:
                    search_result = e.output
                send_security_event(f"Secure Command Search: query='{query}'", user_ip)
            else:
                messages.error(request, "Invalid input provided.")
    return render(request, 'search.html', {'search_result': search_result})

def upload_view(request):
    mode = request.session.get('sim_mode', 'secure')  # unified mode key
    upload_result = ''
    user_ip = get_client_ip(request)
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        filename = request.POST.get('filename', uploaded_file.name)
        if mode == 'vulnerable':
            save_path = default_storage.save(filename, uploaded_file)
            try:
                result = subprocess.check_output(
                    f"ls -al {save_path}",
                    shell=True, stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                upload_result = result
            except subprocess.CalledProcessError as e:
                upload_result = e.output
            send_security_event(f"Vulnerable File Upload: filename='{filename}'", user_ip)
        else:
            if re.fullmatch(r'[a-zA-Z0-9_.-]+', filename):
                safe_path = default_storage.save(filename, uploaded_file)
                try:
                    result = subprocess.check_output(
                        ['ls', '-al', safe_path],
                        universal_newlines=True
                    )
                    upload_result = result
                except subprocess.CalledProcessError as e:
                    upload_result = e.output
                send_security_event(f"Secure File Upload: filename='{filename}'", user_ip)
            else:
                messages.error(request, "Invalid filename provided.")
    return render(request, 'upload.html', {'upload_result': upload_result})
