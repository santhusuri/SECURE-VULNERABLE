#core/urls
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('search/', views.search_view, name='search'),
    path('upload/', views.upload_view, name='upload'),
    path('toggle_mode/', views.toggle_mode, name='toggle_mode'),  # mode toggle
]
