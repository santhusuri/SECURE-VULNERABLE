from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout (auto-switches between secure and vulnerable templates based on mode)
    path('', views.checkout, name='checkout'),

    # User orders
    path("my-orders/", views.my_orders, name="my_orders"),

    # Order creation (AJAX, secure flow)
    path('create_order/', views.create_order, name='create_order'),

    # Stripe webhook (secure mode only)
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),

    # Invoices
    path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),

    # Order success page
    path('success/<int:order_id>/', views.order_success, name='order_success'),
]
