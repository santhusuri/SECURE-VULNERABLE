# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from core import views as core_views
from accounts import views as accounts_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Home
    path("", core_views.home, name="home"),

    # Simulation / mode control
    path("mode-status/", core_views.mode_status, name="mode_status"),
    path("accounts/toggle_mode/", accounts_views.toggle_mode, name="toggle_mode"),

    # Accounts
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),

    # Products, Cart, Orders, Shipping apps
    path("products/", include(("products.urls", "products"), namespace="products")),
    path("cart/", include(("cart.urls", "cart"), namespace="cart")),
    path("core/", include(("core.urls", "core"), namespace="core")),
    path("orders/", include(("orders.urls", "orders"), namespace="orders")),
    path("shipping/", include(("shipping.urls", "shipping"), namespace="shipping")),

    # Demo Views (optional lab)
    path("search/", core_views.search_view, name="search_view"),
    path("upload/", core_views.upload_view, name="upload_view"),
]

# This line adds media URL serving only when DEBUG=True (development)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
