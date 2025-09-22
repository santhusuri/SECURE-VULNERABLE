
---

## 🚀 Features

### E-Commerce Site
- Toggle between **Secure** and **Vulnerable** modes  
- Demonstrates real-world flaws (SQL Injection, XSS, CSRF, etc.)  
- Educational sandbox for security learning  

### Real-Time Monitoring
- Receives logs/events from the e-commerce site  
- Classifies attack types (SQLi, XSS, brute force, etc.)  
- Blocks malicious IPs (blacklist mechanism)  
- Revokes sessions after detection  
- Extensible API for integration with other systems  

---

## 🛠️ Tech Stack

- **Frontend (E-Commerce):** HTML, CSS, JavaScript  
- **Backend (E-Commerce):** Django / Python (adjust if you used something else)  
- **Monitoring System:** Python (Django REST Framework), Requests, JSON APIs  
- **Database:** SQLite / PostgreSQL (adjust to your setup)  

---

## ⚙️ Installation & Setup

1. Clone the Repository
    ```bash
    git clone https://github.com/santhusuri/SECURE-VULNERABLE.git
    cd SECURE-VULNERABLE

2. Setup the E-Commerce Website
    cd config
    # Install dependencies
    pip install -r requirements.txt

    # Run the server
    python manage.py runserver 8000
Open in browser:
👉 http://127.0.0.1:8000/

Use the toggle switch to change between Secure and Vulnerable modes.

3. ngrok (Tunneling — optional)

You can expose your local e-commerce site to the internet for demos or webhook testing using ngrok. **Only use this for short-lived development/testing** — do NOT expose the vulnerable mode to the public.

Example:
    ```bash
    # start ngrok to tunnel port 8000
    ngrok http 8000
This prints a public URL (https://xxxx.ngrok.io
) that forwards traffic to your local server.


---

### Quick commands (local dev)
    
    # 1) Install ngrok (follow official installation)
    # 2) (optional) add your authtoken (one-time)
    ngrok config add-authtoken <YOUR_AUTHTOKEN>

    # 3) Expose your local server on port 8000
    ngrok http 8000

---

4. Setup the Monitoring System
    cd security_project
    # Install dependencies
    pip install -r requirements.txt

    # Run monitoring server
    python manage.py runserver 8001

Monitoring API endpoint:
👉 http://127.0.0.1:8001/api/logs/


## 📡 Usage Flow

Start the monitoring system (listening on port 8001).

Run the e-commerce site.

Perform actions (normal or malicious) on the website.

Monitoring system receives logs in real time and:

Detects attacks

Blocks malicious IPs

Revokes active sessions if needed

Stores logs for later analysis

### Security tips — must read

- DON'T expose vulnerable_mode to the public. Only demo it on an isolated network or to trusted users.

- Use ngrok access controls (basic auth, IP restrictions, reserved domains) if you must share the tunnel. This reduces but does not eliminate risk.

- Keep tunnels short-lived. Stop ngrok when done.

- If testing with real users/data, use the secure mode only.

- Monitor the tunnel (ngrok provides a web inspector, usually at http://127.0.0.1:4040
) to see incoming requests.

- Consider enabling a strong password (or other auth) on any exposed endpoints (or configure ngrok’s auth) to avoid unauthorized access.