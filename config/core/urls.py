# core/urls.py
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("search/", views.search_view, name="search"),
    path("upload/", views.upload_view, name="upload"),

    # Legacy UI toggle (keeps old behavior if some templates still post here)
   

    # New session-based toggle (staff-only)
    path("toggle-session-mode/", views.toggle_session_simulation_mode, name="toggle_session_mode"),
]
