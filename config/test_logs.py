# test_logs.py
from security_client import send_security_event

# List of sample events (attack_type, IP)
logs = [
    ("SELECT * FROM users WHERE username='' OR 1=1 --", "192.168.0.15"),  # SQL Injection
    ("<script>alert('XSS')</script>", "192.168.0.20"),                     # XSS
    ("Failed login attempt for user admin", "192.168.0.30"),               # Brute Force
    ("Normal user activity: browsing products", "192.168.0.40"),           # Normal event
]

print("Sending test logs to External Project for Monitoring Attacks in Real-Time ...\n")

for event, ip in logs:
    resp = send_security_event(event, ip)
    print(f"Event: {event}")
    print(f"IP: {ip}")
    print(f"Response: {resp}\n")

print("Test complete.")
