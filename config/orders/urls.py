#orders/urls
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    
    path('', views.checkout, name='checkout'),
    path("my-orders/", views.my_orders, name="my_orders"),
    path('create_order/', views.create_order, name='create_order'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
]
