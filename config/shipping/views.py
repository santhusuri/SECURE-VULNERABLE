from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from shipping.models import Shipment
from security_client import send_security_event


def get_client_ip(request):
    """Helper to extract client IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def shipping_details(request, order_id):
    """
    Shipment detail view.
    - Secure mode: Only allow owner (or staff) to view their shipment.
    - Vulnerable mode: Anyone can access by guessing order_id (IDOR).
    """
    mode = request.session.get("sim_mode", "secure")
    shipment = get_object_or_404(Shipment, order_id=order_id)
    user_ip = get_client_ip(request)

    if mode == "secure":
        # Secure check: allow only owner or staff
        if request.user.is_authenticated:
            if shipment.order.user != request.user and not request.user.is_staff:
                send_security_event(
                    f"Unauthorized shipment access attempt by {request.user.username}", user_ip
                )
                return HttpResponseForbidden("Not allowed to view this shipment.")
        else:
            return HttpResponseForbidden("Login required to view this shipment.")

        template_name = "shipping/shipment_detail.html"
        send_security_event(
            f"Secure shipment access for order_id={order_id}", user_ip
        )

    else:  # vulnerable mode
        # No authorization check → IDOR vulnerability
        template_name = "shipping/vuln_shipment_detail.html"
        send_security_event(
            f"VULNERABLE shipment access for order_id={order_id}", user_ip
        )

    return render(request, template_name, {"shipment": shipment, "mode": mode})


@login_required
def all_shipments(request):
    """
    - Secure mode: Show shipments belonging to the logged-in user only.
    - Vulnerable mode: Expose ALL shipments to any logged-in user.
    """
    mode = request.session.get("sim_mode", "secure")
    user_ip = get_client_ip(request)

    if mode == "secure":
        shipments = Shipment.objects.filter(order__user=request.user)
        template_name = "shipping/shipment_list.html"
        send_security_event(
            f"Secure shipments list for user={request.user.username}", user_ip
        )

    else:  # vulnerable mode
        shipments = Shipment.objects.all()  # 🔓 data leakage
        template_name = "shipping/vuln_shipment_list.html"
        send_security_event(
            f"VULNERABLE shipments list exposed to {request.user.username}", user_ip
        )

    return render(request, template_name, {"shipments": shipments, "mode": mode})


def track_shipment(request, tracking_number):
    """
    Shipment tracking view.
    - Secure mode: Mask tracking number + ownership check.
    - Vulnerable mode: No validation → tracking enumeration possible.
    """
    mode = request.session.get("sim_mode", "secure")
    user_ip = get_client_ip(request)

    try:
        shipment = Shipment.objects.get(tracking_number=tracking_number)
    except Shipment.DoesNotExist:
        return render(request, "shipping/track_not_found.html", {"tracking_number": tracking_number})

    if mode == "secure":
        # Secure: Ensure user owns the order or is staff
        if not request.user.is_authenticated or (
            shipment.order.user != request.user and not request.user.is_staff
        ):
            send_security_event(
                f"Unauthorized tracking attempt: {tracking_number}", user_ip
            )
            return HttpResponseForbidden("You cannot track this shipment.")

        tracking_display = shipment.masked_tracking_number()
        template_name = "shipping/track_secure.html"
        send_security_event(f"Secure tracking view: {tracking_number}", user_ip)

    else:
        # Vulnerable: Directly expose raw tracking number
        tracking_display = shipment.expose_tracking_number()
        template_name = "shipping/track_vulnerable.html"
        send_security_event(f"VULNERABLE tracking view: {tracking_number}", user_ip)

    return render(
        request,
        template_name,
        {"shipment": shipment, "tracking_display": tracking_display, "mode": mode},
    )
