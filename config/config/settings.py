# config/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env if available
load_dotenv()
# ------------------------------------------------------
# Core Paths & Secrets
# ------------------------------------------------------
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-insecure-key")

# Debug mode
DEBUG = os.getenv("DJANGO_DEBUG", "True").lower() == "true"

# Allowed hosts (comma-separated list in environment variable)
ALLOWED_HOSTS = os.getenv(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,bf249ea75f60.ngrok-free.app"
).split(",")

# CSRF trusted origins (comma-separated list in environment variable)
CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", "http://127.0.0.1:8000,https://bf249ea75f60.ngrok-free.app"
).split(",")


# ------------------------------------------------------
# Installed Apps
# ------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Project apps
    "core",
    "accounts",
    "products",
    "cart",
    "shipping",
    "orders.apps.OrdersConfig",
]

# ------------------------------------------------------
# Middleware
# ------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Security monitoring (always active, logs more in vuln mode)
    "core.middleware.SimulationSecurityMiddleware",
]

ROOT_URLCONF = "config.urls"

# ------------------------------------------------------
# Templates
# ------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.simulation_mode",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ------------------------------------------------------
# Database
# ------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", BASE_DIR / "db.sqlite3"),
        "USER": os.getenv("DB_USER", ""),
        "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", ""),
        "PORT": os.getenv("DB_PORT", ""),
    }
}

# ------------------------------------------------------
# Static & Media
# ------------------------------------------------------
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# Default lab simulation mode (can be 'secure' or 'vulnerable')
SIMULATION_MODE = "secure"


# Lab toggles (fine-grained vuln switches)
VULNERABLE_LABS = {
    "csrf_disabled": os.getenv("LAB_CSRF_DISABLED", "False").lower() == "true",
    "raw_sql_injection": os.getenv("LAB_RAW_SQL", "True").lower() == "true",
    "weak_password_hash": os.getenv("LAB_WEAK_HASH", "True").lower() == "true",
}

# ------------------------------------------------------
# Auth
# ------------------------------------------------------
AUTH_USER_MODEL = "accounts.User"

# ------------------------------------------------------
# Security Defaults (secure mode only)
# ------------------------------------------------------
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

# ------------------------------------------------------
# External Project Integration
# ------------------------------------------------------
PROJECT_A_REVOKE_URL = os.getenv("PROJECT_A_REVOKE_URL", "http://127.0.0.1:8000/api/revoke_session/")
PROJECT_A_API_KEY = os.getenv("PROJECT_A_API_KEY", "your_api_key_here")

PROJECT_B_LOG_ENDPOINT = os.getenv("PROJECT_B_LOG_ENDPOINT", None)


# ------------------------------------------------------
# Logging
# ------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs/django.log",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
}

STRIPE_PUBLIC_KEY = "pk_test_51RwKMhJQHrTkAmKCC8L9UubCi6zH4DNrlg5suSmfEHFbfphLk1qirtarAct8SGrney8JdV0AaV8J73RXfcu8vIQc00DqkG4Uiq"
STRIPE_SECRET_KEY = "sk_test_51RwKMhJQHrTkAmKCB3pqysbatgXmnjLhSnnVE5CfKIvViLVvZAEfFHYBUSSdwTZaGGnRFhgEenVOVRQtqIstnwzU007evgPepL"
STRIPE_WEBHOOK_SECRET = "whsec_..."

# ------------------------------------------------------
# Stripe Keys (used in orders/checkout)
# ------------------------------------------------------
"""
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
"""


