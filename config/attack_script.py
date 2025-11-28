import requests
import time

BASE_URL = "http://127.0.0.1:8000"

# Attack payloads for all 8 attack types with target URLs
attacks = [
    {"type": "sql_injection", "payload": "' OR '1'='1' --", "url": "/accounts/login/"},
    {"type": "xss", "payload": "<script>alert('XSS')</script>", "url": "/products/vuln_product_search/"},
    {"type": "bruteforce", "payload": "failed login", "url": "/accounts/login/"},
    {"type": "command_injection", "payload": "; ls", "url": "/orders/"},
    {"type": "malicious_file_upload", "payload": "file.php", "url": "/products/vuln_product_detail/"},
    {"type": "directory_traversal", "payload": "../etc/passwd", "url": "/shipping/details/1/"},
    {"type": "session_hijacking", "payload": "PHPSESSID=12345", "url": "/accounts/profile/"},
    {"type": "csrf_bypass", "payload": "csrfmiddlewaretoken=fake_token", "url": "/orders/"},
]

def send_attack(session, attack_type, payload, url):
    print(f"Sending {attack_type} attack to {url}")
    data = {
        "username": payload,
        "password": "password123",
        "csrfmiddlewaretoken": "dummy_token"
    }
    try:
        response = session.post(f"{BASE_URL}{url}", data=data)
        print(f"Response status: {response.status_code}")
    except Exception as e:
        print(f"Error sending attack: {e}")

def set_mode(session, mode):
    print(f"Setting mode to {mode}")
    try:
        response = session.post(f"{BASE_URL}/accounts/toggle_mode/")
        print(f"Toggle response: {response.status_code}, mode: {response.json()}")
    except Exception as e:
        print(f"Error setting mode: {e}")

def main():
    session = requests.Session()

    # Set to vulnerable mode
    set_mode(session, "vulnerable")
    time.sleep(1)

    # Send attacks in vulnerable mode
    print("Sending attacks in vulnerable mode")
    for attack in attacks:
        send_attack(session, attack["type"], attack["payload"], attack["url"])
        time.sleep(1)

    # Set to secure mode
    set_mode(session, "secure")
    time.sleep(1)

    # Send attacks in secure mode
    print("Sending attacks in secure mode")
    for attack in attacks:
        send_attack(session, attack["type"], attack["payload"], attack["url"])
        time.sleep(1)

if __name__ == "__main__":
    main()
