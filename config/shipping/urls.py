# shipping/urls.py
from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    # Single shipment detail
    path('details/<int:order_id>/', views.shipping_details, name='shipping_details'),

    # NEW: Shipment listing (secure = only my shipments, vulnerable = all shipments exposed)
    path('list/', views.all_shipments, name='all_shipments'),

    # NEW: Tracking endpoint (secure = masked, vulnerable = leaked tracking numbers)
    path('track/<int:order_id>/', views.track_shipment, name='track_shipment'),
]
