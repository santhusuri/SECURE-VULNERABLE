import requests
import json

BASE_URL = "http://127.0.0.1:8001"

def test_receive_log_valid():
    url = f"{BASE_URL}/api/logs/"
    data = {
        "attack_type": "sql_injection",
        "event_data": "Test SQL injection attack",
        "ip_address": "192.168.1.1"
    }
    response = requests.post(url, json=data)
    print(f"POST /api/logs/ (valid) - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_receive_log_invalid():
    url = f"{BASE_URL}/api/logs/"
    data = {
        "attack_type": "invalid_attack",
        "event_data": "",
        "ip_address": "invalid_ip"
    }
    response = requests.post(url, json=data)
    print(f"POST /api/logs/ (invalid) - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_receive_log_missing_fields():
    url = f"{BASE_URL}/api/logs/"
    data = {
        "attack_type": "xss"
    }
    response = requests.post(url, json=data)
    print(f"POST /api/logs/ (missing fields) - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_receive_log_different_attacks():
    attacks = ["xss", "bruteforce", "command_injection", "malicious_file_upload", "directory_traversal", "session_hijacking", "csrf_bypass"]
    for attack in attacks:
        url = f"{BASE_URL}/api/logs/"
        data = {
            "attack_type": attack,
            "event_data": f"Test {attack} attack",
            "ip_address": "192.168.1.2"
        }
        response = requests.post(url, json=data)
        print(f"POST /api/logs/ ({attack}) - Status: {response.status_code}, Response: {response.json()}")

def test_incidents_api():
    url = f"{BASE_URL}/api/incidents/"
    response = requests.get(url)
    print(f"GET /api/incidents/ - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_incidents_api_with_last_id():
    url = f"{BASE_URL}/api/incidents/?last_id=1"
    response = requests.get(url)
    print(f"GET /api/incidents/?last_id=1 - Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response

def test_dashboard():
    url = f"{BASE_URL}/dashboard/"
    response = requests.get(url)
    print(f"GET /dashboard/ - Status: {response.status_code}")
    print(f"Content length: {len(response.text)}")
    return response

def test_clear_logs():
    url = f"{BASE_URL}/clear-logs/"
    response = requests.post(url)
    print(f"POST /clear-logs/ - Status: {response.status_code}")
    if response.status_code == 302:
        print("Redirected to dashboard")
    return response

if __name__ == "__main__":
    print("Testing Monitoring API...")
    test_receive_log_valid()
    test_receive_log_invalid()
    test_receive_log_missing_fields()
    test_receive_log_different_attacks()
    test_incidents_api()
    test_incidents_api_with_last_id()
    test_dashboard()
    test_clear_logs()
