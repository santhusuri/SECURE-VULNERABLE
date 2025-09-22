import requests

# Project B endpoint to receive logs
SECURITY_PROJECT_B_URL = "http://127.0.0.1:8001/api/logs/"

def send_security_event(event, ip="127.0.0.1"):
    """
    Sends a security event to Project B.

    Args:
        event (str): Description or data of the security event.
        ip (str): Source IP address of the event.

    Returns:
        dict: Response from Project B or error details.
    """
    try:
        response = requests.post(
            SECURITY_PROJECT_B_URL,
            json={
                "event_data": event,
                "ip_address": ip,
                "attack_type": "other"
            },
            timeout=5
        )
        return response.json()
    except Exception as e:
        return {"error": str(e)}
