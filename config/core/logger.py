#core/logger
import os
from datetime import datetime
import random
import requests
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute paths for logs
IDS_LOG_FILE = os.path.join(BASE_DIR, "logs/ids.log")
AIRS_LOG_FILE = os.path.join(BASE_DIR, "logs/airs.log")

# Ensure directory exists
os.makedirs(os.path.dirname(IDS_LOG_FILE), exist_ok=True)
os.makedirs(os.path.dirname(AIRS_LOG_FILE), exist_ok=True)

# Create files if they don't exist
open(IDS_LOG_FILE, 'a').close()
open(AIRS_LOG_FILE, 'a').close()


def write_ids_log(user_id, action):
    """Write to IDS log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(IDS_LOG_FILE, "a") as f:
        f.write(f"{timestamp} | User: {user_id} | {action}\n")


def write_airs_log(alert_type):
    """Write to AIRS log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_id = random.randint(1000, 9999)
    with open(AIRS_LOG_FILE, "a") as f:
        f.write(f"{timestamp} | Alert ID: {alert_id} | Type: {alert_type}\n")


def send_security_event(event_message, ip_address):
    """
    Send a security event to Project B logging endpoint.
    Falls back to local IDS log if endpoint unavailable.
    """
    endpoint = getattr(settings, "PROJECT_B_LOG_ENDPOINT", None)
    payload = {"event": event_message, "ip": ip_address}

    if endpoint:
        try:
            response = requests.post(endpoint, json=payload, timeout=3)
            if response.status_code == 200:
                return {"status": "success", "response": response.text}
            else:
                write_ids_log("system", f"Failed to send to Project B: {event_message}")
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            write_ids_log("system", f"Error sending to Project B: {event_message} | {e}")
            return {"status": "error", "exception": str(e)}
    else:
        # If endpoint not set, just log locally
        write_ids_log("system", f"[LOCAL] {event_message}")
        return {"status": "local_logged"}
