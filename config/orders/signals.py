from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import random

from django.db import models  # 👈 needed for F expressions
from orders.models import Order
from shipping.models import Shipment


@receiver(post_save, sender=Order)
def create_shipment_for_order(sender, instance, created, **kwargs):
    if created:
        # Estimated delivery = 3 or 5 days
        delivery_days = random.choice([3, 5])
        estimated_delivery = timezone.now().date() + timedelta(days=delivery_days)

        # --- Decide shipment status ---
        status = "pending"

        # Case 1: Out of stock (quantity requested > available stock)
        if instance.items.filter(product__stock__lt=models.F('quantity')).exists():
            status = "out_of_stock"

        # Case 2: Simulate technical issue (20% chance)
        elif random.choice([True, False, False, False, False]):
            status = "delayed"

        # Otherwise: Pending
        else:
            status = "pending"

        # --- Create shipment ---
        Shipment.objects.create(
            order=instance,
            tracking_number=f"TRK-{instance.pk}-{int(timezone.now().timestamp())}",
            carrier="Default Carrier",
            estimated_delivery=estimated_delivery,
            status=status
        )
