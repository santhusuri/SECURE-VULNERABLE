# Setting up ASGI Server for Monitoring App with Django Channels

## Overview
The monitoring app uses Django Channels for WebSocket support to enable real-time updates on the dashboard. To enable this, the app must be run with an ASGI server such as Daphne or Uvicorn instead of the default Django runserver.

## Steps to Setup and Run

### 1. Install Daphne or Uvicorn
You can install Daphne or Uvicorn using pip:

```bash
pip install daphne
# or
pip install uvicorn
```

### 2. Run the Monitoring App with ASGI Server

#### Using Daphne:
```bash
daphne -p 8001 security_project.asgi:application
```

#### Using Uvicorn:
```bash
uvicorn security_project.asgi:application --host 127.0.0.1 --port 8001
```

### 3. Access the Dashboard
Open your browser and navigate to:
```
http://127.0.0.1:8001/dashboard/
```

### 4. Verify WebSocket Connection
The dashboard should now connect successfully to the WebSocket endpoint `/ws/incidents/` and receive real-time updates.

## Notes
- Make sure your `asgi.py` is correctly configured with Channels routing.
- Ensure `channels` is added to your `INSTALLED_APPS` in `settings.py`.
- If you encounter issues, check your firewall or proxy settings that might block WebSocket connections.

## Summary
Running the app with an ASGI server is essential for WebSocket support and real-time dashboard updates. Follow the above steps to upgrade your development environment accordingly.
