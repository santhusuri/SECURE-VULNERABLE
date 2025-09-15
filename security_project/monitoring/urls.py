from django.http import HttpResponse
from django.urls import path
from . import views

def home(request):
    return HttpResponse(
        "✅ Security Project is running. Use /api/logs/ to send events, or /dashboard/ to view incidents."
    )

urlpatterns = [
    path("", home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('clear_logs/', views.clear_logs, name='clear_logs'),
    path("api/logs/", views.receive_log, name="receive_log"),
]
