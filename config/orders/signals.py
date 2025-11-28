from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import random

from django.db import models  # for F expressions
from django.conf import settings
from orders.models import Order
from shipping.models import Shipment
from orders.models import SecurityLog  # ✅ new model for auditing


@receiver(post_save, sender=Order)
def create_shipment_for_order(sender, instance, created, **kwargs):
    """
    Auto-create a Shipment when an Order is placed + log audit info.

    🔐 Secure mode:
        - Checks stock availability
        - Introduces random delays (to simulate real logistics)
        - Correctly sets status ("pending", "delayed", "out_of_stock")

    ⚠ Vulnerable mode:
        - Always creates shipment blindly (even if stock is insufficient)
        - Ignores delays
        - Demonstrates insecure business logic
    """
    if not created:
        return

    # Determine simulation mode (fallback to settings default)
    request_mode = getattr(instance, "_sim_mode", None)
    mode = request_mode or getattr(settings, "SIMULATION_MODE", "secure")

    # Estimated delivery date
    delivery_days = random.choice([3, 5])
    estimated_delivery = timezone.now().date() + timedelta(days=delivery_days)

    shipment_status = "pending"

    if mode == "secure":
        # --- Secure shipment logic ---
        # Case 1: Out of stock
        if instance.items.filter(product__stock__lt=models.F("quantity")).exists():
            shipment_status = "out_of_stock"

        # Case 2: Random technical issue (20% chance)
        elif random.choice([True, False, False, False, False]):
            shipment_status = "delayed"

        # Otherwise remains pending
        Shipment.objects.create(
            order=instance,
            tracking_number=f"TRK-{instance.pk}-{int(timezone.now().timestamp())}",
            carrier="Default Carrier",
            estimated_delivery=estimated_delivery,
            status=shipment_status,
        )

    else:
        # --- Vulnerable shipment logic ---
        shipment_status = "pending"
        Shipment.objects.create(
            order=instance,
            tracking_number=f"VULN-{instance.pk}-{int(timezone.now().timestamp())}",
            carrier="Insecure Carrier",
            estimated_delivery=estimated_delivery,
            status=shipment_status,
        )

    # ✅ Always log the order creation event
    SecurityLog.objects.create(
        order=instance,
        user=instance.user,
        mode=mode,
        total=instance.total,
        shipment_status=shipment_status,
        timestamp=timezone.now(),
    )
