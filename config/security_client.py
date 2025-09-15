import requests

SECURITY_PROJECT_B_URL = "http://127.0.0.1:8001/api/logs/"

def send_security_event(event, ip="127.0.0.1"):
    """
    Sends a log/event to Project B.
    """
    try:
        r = requests.post(
            SECURITY_PROJECT_B_URL,
            json={"event": event, "ip": ip},
            timeout=5
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}
