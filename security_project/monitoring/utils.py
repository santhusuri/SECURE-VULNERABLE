import subprocess
import requests
from django.conf import settings
from .models import BlacklistEntry

# You can customize these in settings.py
SURICATA_EVE_PATH = getattr(__import__('django.conf').conf.settings, "SURICATA_EVE_PATH", "/var/log/suricata/eve.json")
PROJECT_A_REVOKE_URL = getattr(__import__('django.conf').conf.settings, "PROJECT_A_REVOKE_URL", None)
PROJECT_A_API_KEY = getattr(__import__('django.conf').conf.settings, "PROJECT_A_API_KEY", None)

def block_ip_system(ip):
    """
    Attempt to block IP at the system firewall (iptables).
    WARNING: requires root privileges; use with caution.
    This function tries iptables -I INPUT -s <ip> -j DROP.
    If your system uses nftables/firewalld, replace with appropriate commands.
    """
    try:
        cmd = ["sudo", "iptables", "-I", "INPUT", "-s", ip, "-j", "DROP"]
        subprocess.run(cmd, check=True)
        return True, "iptables applied"
    except Exception as e:
        return False, str(e)

def add_blacklist_entry(ip, reason="suricata alert"):
    entry, created = BlacklistEntry.objects.get_or_create(ip_address=ip, defaults={"reason": reason})
    return created, entry

def revoke_session_on_project_a(ip):
    """
    Optional: call Project A endpoint to revoke sessions for IP/users.
    You must configure PROJECT_A_REVOKE_URL in settings.py.
    """
    if not PROJECT_A_REVOKE_URL:
        return False, "no PROJECT_A_REVOKE_URL configured"

    headers = {}
    if PROJECT_A_API_KEY:
        headers["Authorization"] = f"Bearer {PROJECT_A_API_KEY}"

    try:
        resp = requests.post(PROJECT_A_REVOKE_URL, json={"ip": ip}, headers=headers, timeout=5)
        return True, f"revoked, status {resp.status_code}"
    except Exception as e:
        return False, str(e)
