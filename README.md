
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
    cd ecommerce_site
    # Install dependencies
    pip install -r requirements.txt

    # Run the server
    python manage.py runserver 8000
Open in browser:
👉 http://127.0.0.1:8000/

Use the toggle switch to change between Secure and Vulnerable modes.

3. Setup the Monitoring System
    cd monitoring_system
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