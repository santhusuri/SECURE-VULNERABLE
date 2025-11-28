from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product


class Order(models.Model):
    SECURE = "secure"
    VULNERABLE = "vulnerable"
    MODE_CHOICES = [
        (SECURE, "Secure"),
        (VULNERABLE, "Vulnerable"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="orders"
    )
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ✅ mode field
    mode = models.CharField(
        max_length=12,
        choices=MODE_CHOICES,
        default=SECURE,
    )

    def __str__(self):
        return f"Order #{self.pk} by {self.user or 'Guest'} - ${self.total} ({self.mode})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    added_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"
        
        
        
        
        
        
from django.db import models
from django.conf import settings


class SecurityLog(models.Model):
    """
    Logs every order event for auditing secure vs vulnerable behavior.
    """
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    mode = models.CharField(max_length=20, choices=[("secure", "Secure"), ("vulnerable", "Vulnerable")])
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipment_status = models.CharField(max_length=50)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"[{self.mode.upper()}] Order {self.order.id} by {self.user} (${self.total})"

