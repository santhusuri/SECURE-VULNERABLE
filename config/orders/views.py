from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import stripe
import json
from datetime import date, timedelta
from orders.models import Order
from shipping.models import Shipment

stripe.api_key = settings.STRIPE_SECRET_KEY

def checkout(request):
    """
    Handles checkout flow depending on mode.
    - Secure mode:
        Creates a Stripe PaymentIntent.
        Order is created only AFTER successful payment.
    - Vulnerable mode:
        Accepts user input amount and immediately creates an order.
    """
    mode = request.session.get('sim_mode', 'secure')  # unified mode key
    cart = request.session.get('cart', {})
    total = sum(item['price'] * item['qty'] for item in cart.values())
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('cart:cart_view')

    if mode == 'secure':
        intent = stripe.PaymentIntent.create(
            amount=int(total * 100),
            currency='usd',
            metadata={'user_id': request.user.id if request.user.is_authenticated else 'guest'}
        )
        return render(request, 'orders/checkout.html', {
            'cart': cart,
            'total': total,
            'client_secret': intent.client_secret,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        })
    else:  # vulnerable mode
        if request.method == 'POST':
            entered_amount = float(request.POST.get('amount', total))
            order, shipment = create_order_and_shipment(request.user, cart, entered_amount)
            messages.warning(request, f"(Vulnerable) Payment accepted for ${entered_amount} without verification!")
            request.session['cart'] = {}
            return redirect('orders:order_success', order.id)
        return render(request, 'orders/vuln_checkout.html', {
            'cart': cart,
            'total': total
        })

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return render(request, 'orders/webhook_failed.html')

    if event['type'] == 'payment_intent.succeeded':
        user_id = event['data']['object']['metadata']['user_id']
        cart = {}
        total = 0
        user = None
        if user_id != 'guest':
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                user = None
        create_order_and_shipment(user, cart, total)
    return render(request, 'orders/webhook_success.html')

def order_success(request, order_id):
    order = Order.objects.get(id=order_id)
    return render(request, 'orders/order_success.html', {'order': order})

def create_order_and_shipment(user, cart, total):
    order = Order.objects.create(
        user=user if user and hasattr(user, 'is_authenticated') and user.is_authenticated else None,
        total=total,
    )
    shipment = Shipment.objects.create(
        order=order,
        tracking_number=f"TRACK{order.id}XYZ",
        carrier="Django Express",
        estimated_delivery=date.today() + timedelta(days=5),
        shipped_date=None,
        status="pending"
    )
    return order, shipment

@csrf_protect
@require_POST
def create_order(request):
    try:
        data = json.loads(request.body)
        payment_intent_id = data.get("payment_intent_id")
        cart = request.session.get('cart', {})
        total = sum(item['price'] * item['qty'] for item in cart.values())
        user = request.user if request.user.is_authenticated else None
        # TODO: Verify payment_intent_id with Stripe before creating order
        order, shipment = create_order_and_shipment(user, cart, total)
        request.session['cart'] = {}
        return JsonResponse({"order_id": order.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
