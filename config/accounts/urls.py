# accounts/urls.py
from django.urls import path
from django.conf import settings
from . import views


app_name = "accounts"

urlpatterns = [
    # Lab-specific endpoints (explicitly map to lab views)
    path("vuln_login/", views.login_view, name="vuln_login"),
    path("vuln_register/", views.register_view, name="vuln_register"),
    #path("lab/create_user/", views.create_lab_vuln_user, name="lab_create_user"),
    path("toggle_mode/", views.toggle_mode, name="toggle_mode"),

    # Public/auth routes — use the mode-aware lab views so single URL can show secure or vuln
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    # If you have other secure-only views in views.py, include them here:
    # path("secure-only/", views.some_secure_view, name="secure_only"),
]
