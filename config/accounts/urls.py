from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [
    path('vuln_login/', views.login_view, name='vuln_login'),
    path('vuln_register/', views.register_view, name='vuln_register'),
    path('lab/create_user/', views.create_lab_vuln_user, name='lab_create_user'),
    path('toggle_mode/', views.toggle_mode, name='toggle_mode'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    # keep your existing secure routes as-is
]
