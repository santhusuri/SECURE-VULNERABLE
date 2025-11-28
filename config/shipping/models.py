from django.db import models
from django.utils import timezone


class Shipment(models.Model):
    order = models.OneToOneField(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="shipment"
    )
    tracking_number = models.CharField(max_length=100)
    carrier = models.CharField(max_length=100)
    estimated_delivery = models.DateField()
    shipped_date = models.DateField(null=True, blank=True)
    delivered_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "Pending"),
            ("shipped", "Shipped"),
            ("in_transit", "In Transit"),
            ("delivered", "Delivered"),
            ("delayed", "Delayed"),
            ("out_of_stock", "Out of Stock"),
        ],
        default="pending"
    )

    last_updated = models.DateTimeField(auto_now=True)  # track changes

    def __str__(self):
        return f"Shipment for Order #{self.order.id} - {self.status}"

    # ---------- Secure Helpers ----------
    def mark_shipped(self):
        """Securely mark shipment as shipped."""
        self.status = "shipped"
        self.shipped_date = timezone.now().date()
        self.save()

    def mark_delivered(self):
        """Securely mark shipment as delivered."""
        self.status = "delivered"
        self.delivered_date = timezone.now().date()
        self.save()

    # ---------- Vulnerable Lab Helper ----------
    def expose_tracking_number(self):
        """
        For vulnerable mode: directly return tracking number without masking.
        """
        return self.tracking_number

    def masked_tracking_number(self):
        """
        For secure mode: partially mask the tracking number.
        Example: TRK-12345 -> TRK-1****45
        """
        if not self.tracking_number:
            return ""
        if len(self.tracking_number) <= 6:
            return self.tracking_number[:2] + "*" * (len(self.tracking_number) - 2)
        head = self.tracking_number[:3]
        tail = self.tracking_number[-3:]
        middle = "*" * (len(self.tracking_number) - len(head) - len(tail))
        return f"{head}{middle}{tail}"
