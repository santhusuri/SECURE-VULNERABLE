import os
from datetime import datetime
import random
import requests
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Absolute paths for logs
LOGS_DIR = os.path.join(BASE_DIR, "logs")
IDS_LOG_FILE = os.path.join(LOGS_DIR, "ids.log")
AIRS_LOG_FILE = os.path.join(LOGS_DIR, "airs.log")

# Ensure logs directory exists
os.makedirs(LOGS_DIR, exist_ok=True)

# Ensure log files exist
for log_file in (IDS_LOG_FILE, AIRS_LOG_FILE):
    open(log_file, "a").close()


def _write_log(file_path, message: str):
    """Internal helper: append a line to the given log file."""
    try:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(message + "\n")
    except Exception as e:
        print(f"[Logger] Failed to write log: {e}")


def write_ids_log(user_id: str, action: str):
    """
    Write an entry to the IDS log.
    Format: TIMESTAMP | User: X | ACTION
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | User: {user_id} | {action}"
    _write_log(IDS_LOG_FILE, line)


def write_airs_log(alert_type: str):
    """
    Write an entry to the AIRS log.
    Format: TIMESTAMP | Alert ID: XXXX | Type: alert_type
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alert_id = random.randint(1000, 9999)
    line = f"{timestamp} | Alert ID: {alert_id} | Type: {alert_type}"
    _write_log(AIRS_LOG_FILE, line)


def send_security_event(event_message: str, ip_address: str):
    """
    Try sending a security event to an external logging service (Project B).
    Falls back to local IDS log if unreachable.
    """
    endpoint = getattr(settings, "PROJECT_B_LOG_ENDPOINT", None)
    payload = {"event": event_message, "ip": ip_address}

    if endpoint:
        try:
            response = requests.post(endpoint, json=payload, timeout=3)
            if response.status_code == 200:
                return {"status": "success", "response": response.text}
            else:
                write_ids_log("system", f"Failed to send to Project B ({response.status_code}): {event_message}")
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            write_ids_log("system", f"Error sending to Project B: {event_message} | {e}")
            return {"status": "error", "exception": str(e)}

    # Fallback: local IDS log
    write_ids_log("system", f"[LOCAL] {event_message}")
    return {"status": "local_logged"}
