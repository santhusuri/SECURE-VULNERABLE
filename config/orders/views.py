from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

import stripe
import json
import logging

from orders.models import Order, OrderItem
from shipping.models import Shipment
from .utils import generate_invoice

stripe.api_key = settings.STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


def get_mode(request):
    return request.session.get("sim_mode", "secure")


# -----------------------
# My Orders (secure only)
# -----------------------
@login_required
def my_orders(request):
    # Always secure: users should only see their own list
    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related(
            "items__product",
            Prefetch("shipment", queryset=Shipment.objects.all())
        )
        .order_by("-created_at")
    )
    return render(request, "orders/my_orders.html", {"orders": orders})


# -----------------------
# Checkout (secure vs vulnerable)
# -----------------------
def checkout(request):
    mode = get_mode(request)
    cart = request.session.get("cart", {})
    total = sum(item["price"] * item["qty"] for item in cart.values())

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:cart_view")

    if mode == "secure":
        # SECURE: Stripe + order only after verified payment
        request.session["pending_cart"] = cart
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),
            currency="usd",
            metadata={"user_id": request.user.id if request.user.is_authenticated else "guest"},
        )
        return render(
            request,
            "orders/checkout.html",
            {
                "cart": cart,
                "total": total,
                "client_secret": intent.client_secret,
                "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
            },
        )
    else:
        # VULNERABLE: accepts arbitrary amount, instant order
        if request.method == "POST":
            try:
                entered_amount = float(request.POST.get("amount", total))
            except ValueError:
                messages.error(request, "Invalid amount entered.")
                return redirect("orders:checkout")

            order = create_order_with_items(request, request.user, cart, entered_amount)
            messages.warning(
                request,
                f"(VULNERABLE) Payment accepted for ${entered_amount} without verification!",
            )
            logger.warning(f"Vulnerable checkout used by user={request.user} amount={entered_amount}")
            request.session["cart"] = {}
            return redirect("orders:order_success", order.id)

        return render(request, "orders/vuln_checkout.html", {"cart": cart, "total": total})


# -----------------------
# Stripe Webhook (secure)
# -----------------------
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError) as e:
        logger.error(f"Stripe webhook error: {e}")
        return JsonResponse({"status": "failed"}, status=400)

    if event["type"] == "payment_intent.succeeded":
        user_id = event["data"]["object"]["metadata"]["user_id"]
        cart = request.session.get("pending_cart", {})
        total = sum(item["price"] * item["qty"] for item in cart.values())
        user = None
        if user_id != "guest":
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user = None

        if cart:
            create_order_with_items(request, user, cart, total)
            request.session["pending_cart"] = {}

    return JsonResponse({"status": "success"})


# -----------------------
# Order Success (IDOR lab)
# -----------------------
def order_success(request, order_id):
    mode = get_mode(request)

    if mode == "secure":
        # SECURE: only owner can see their order success page
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        order = get_object_or_404(Order, id=order_id, user=request.user)
    else:
        # VULNERABLE: IDOR – no user check, any authenticated user can view any order id
        order = get_object_or_404(Order, id=order_id)

    return render(request, "orders/order_success.html", {"order": order})


# -----------------------
# Create Order (AJAX, secure)
# -----------------------
@csrf_protect
@require_POST
def create_order(request):
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get("payment_intent_id")
        cart = request.session.get("cart", {})
        total = sum(item["price"] * item["qty"] for item in cart.values())
        user = request.user if request.user.is_authenticated else None

        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        if intent.status != "succeeded":
            return JsonResponse({"error": "Payment not verified"}, status=400)

        order = create_order_with_items(request, user, cart, total)
        request.session["cart"] = {}
        return JsonResponse({"order_id": order.id})
    except Exception as e:
        logger.error(f"Create order error: {e}")
        return JsonResponse({"error": str(e)}, status=400)


# -----------------------
# Helper: Create Order + Items
# -----------------------
def create_order_with_items(request, user, cart, total):
    mode = get_mode(request)
    order = Order.objects.create(
        user=user if user and hasattr(user, "is_authenticated") and user.is_authenticated else None,
        total=total,
        mode=mode,
    )
    for product_id, item in cart.items():
        OrderItem.objects.create(
            order=order,
            product_id=product_id,
            quantity=item["qty"],
            price=item["price"],
        )
    logger.info(f"Order created id={order.id} mode={mode} total={total} user={user}")
    return order


# -----------------------
# Download Invoice (IDOR lab)
# -----------------------
@login_required
def download_invoice(request, order_id):
    mode = get_mode(request)

    if mode == "secure":
        # SECURE: enforce ownership
        order = get_object_or_404(Order, id=order_id, user=request.user)
    else:
        # VULNERABLE: IDOR – any logged-in user can download any invoice id
        order = get_object_or_404(Order, id=order_id)

    response = generate_invoice(order)
    filename = f"invoice_order_{order.id}.pdf"
    response["Content-Disposition"] = f'attachment; filename=\"{filename}\"'
    return response
