import subprocess
import requests
from django.conf import settings
from .models import BlacklistEntry

PROJECT_A_REVOKE_URL = getattr(settings, "PROJECT_A_REVOKE_URL", None)
PROJECT_A_API_KEY = getattr(settings, "PROJECT_A_API_KEY", None)

def block_ip_system(ip):
    try:
        cmd = ["sudo", "iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"]
        subprocess.run(cmd, check=True)
        return True, "iptables applied"
    except Exception as e:
        return False, str(e)

def add_blacklist_entry(ip, reason="Detected incident"):
    entry, created = BlacklistEntry.objects.get_or_create(ip_address=ip, defaults={"reason": reason})
    return created, entry

def revoke_session_on_project_a(ip):
    if not PROJECT_A_REVOKE_URL:
        return False, "PROJECT_A_REVOKE_URL not configured"
    headers = {}
    if PROJECT_A_API_KEY:
        headers["Authorization"] = f"Bearer {PROJECT_A_API_KEY}"
    try:
        resp = requests.post(PROJECT_A_REVOKE_URL, json={"ip": ip}, headers=headers, timeout=5)
        if resp.status_code == 200:
            return True, "Session revoked successfully"
        return False, f"Failed: status {resp.status_code}"
    except Exception as e:
        return False, str(e)
