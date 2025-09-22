from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/logs/', views.receive_log, name='receive_log'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('clear-logs/', views.clear_logs, name='clear_logs'),
    path('api/incidents/', views.incidents_api, name='incidents_api'),

    # Redirect root URL to dashboard
    path('', RedirectView.as_view(url='dashboard/', permanent=False)),
]