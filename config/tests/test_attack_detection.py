import pytest
from orders.models import PerformanceLog

@pytest.mark.django_db
def test_attack_detection_logging(client):
    # Define attacks with URLs and payload keys
    attacks = [
        {"type": "sql_injection", "payload": "' OR '1'='1' --", "url": "/accounts/login/"},
        {"type": "xss", "payload": "<script>alert('XSS')</script>", "url": "/products/search/"},
        {"type": "bruteforce", "payload": "failed login", "url": "/accounts/login/"},
        {"type": "command_injection", "payload": "; ls", "url": "/orders/"},
        {"type": "session_hijacking", "payload": "PHPSESSID=12345", "url": "/accounts/profile/"},
        {"type": "csrf_bypass", "payload": "csrfmiddlewaretoken=fake_token", "url": "/orders/"},
    ]

    # Toggle mode to vulnerable first
    client.post("/accounts/toggle_mode/", data={'mode': 'vulnerable'})

    for attack in attacks:
        response = client.post(attack["url"], data={"username": attack["payload"], "password": "password123"})
        assert response.status_code in [200, 403, 400, 302]
        logs = PerformanceLog.objects.filter(attack_type=attack["type"])
        assert logs.exists()

    # Toggle mode to secure
    client.post("/accounts/toggle_mode/", data={'mode': 'secure'})

    for attack in attacks:
        response = client.post(attack["url"], data={"username": attack["payload"], "password": "password123"})
        assert response.status_code in [200, 403, 400, 302]
        logs = PerformanceLog.objects.filter(attack_type=attack["type"])
        assert logs.exists()
