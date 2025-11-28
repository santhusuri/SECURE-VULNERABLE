# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


from products.models import Product
from security_client import send_security_event  # your logging integration


def get_cart(request):
    """Retrieves the shopping cart from session. If no cart exists, returns an empty dict."""
    return request.session.get('cart', {})


def save_cart(request, cart):
    """Saves the updated cart into session."""
    request.session['cart'] = cart
    request.session.modified = True


def cart_view(request):
    """Display cart contents, switching template based on mode."""
    cart = get_cart(request)
    total = 0
    for item in cart.values():
        item['subtotal'] = item['price'] * item['qty']
        total += item['subtotal']

    mode = request.session.get('sim_mode', 'secure')
    template = 'cart/cart_view.html' if mode == 'secure' else 'cart/vuln_cart_view.html'

    return render(request, template, {
        'cart': cart,
        'total': total,
        'mode': mode,
    })

@csrf_exempt   # LAB ONLY: disables CSRF for this endpoint
def add_to_cart(request, product_id):
    """
    Adds a product to the shopping cart.
    Behavior depends on current mode:
    - Secure mode: validates product existence.
    - Vulnerable mode: no validation (for demonstration).
    """
    mode = request.session.get('sim_mode', 'secure')
    cart = get_cart(request)

    try:
        if mode == 'secure':
            product = get_object_or_404(Product, id=product_id)
            send_security_event(f"SECURE: add_to_cart product_id={product_id}", request.META.get("REMOTE_ADDR"))
        else:
            # Vulnerable: no validation (may raise Product.DoesNotExist if bad id)
            product = Product.objects.get(id=product_id)
            send_security_event(f"VULN: add_to_cart product_id={product_id} (no validation)", request.META.get("REMOTE_ADDR"))
    except Exception as e:
        # Keep user-friendly behavior: if product lookup fails
        messages.error(request, "Product not found.")
        return redirect('cart:cart_view')

    pid = str(product.id)
    if pid not in cart:
        cart[pid] = {
            'name': product.name,
            'price': float(product.price),
            'qty': 1
        }
    else:
        cart[pid]['qty'] += 1

    save_cart(request, cart)

    if mode == 'secure':
        messages.success(request, f"{product.name} added to cart.")
    else:
        messages.warning(request, f"(VULNERABLE) {product.name} added to cart without checks.")

    return redirect('cart:cart_view')


def remove_from_cart(request, product_id):
    """Removes a specific product from the shopping cart."""
    cart = get_cart(request)
    if str(product_id) in cart:
        del cart[str(product_id)]
        save_cart(request, cart)
        messages.info(request, "Item removed from cart.")
        send_security_event(f"remove_from_cart product_id={product_id}", request.META.get("REMOTE_ADDR"))
    return redirect('cart:cart_view')


def clear_cart(request):
    """Empties the entire shopping cart."""
    save_cart(request, {})
    messages.info(request, "Cart cleared.")
    send_security_event("clear_cart", request.META.get("REMOTE_ADDR"))
    return redirect('cart:cart_view')


@require_POST
def update_quantity(request, id):
    """
    Secure: only POST, CSRF protected by default, validates product existence.
    Accepts 'action' values: 'increase' or 'decrease' (keeps min qty = 1).
    """
    product = get_object_or_404(Product, id=id)
    action = request.POST.get('action')
    cart = get_cart(request)
    current_qty = cart.get(str(id), {}).get('qty', 0)

    if action == 'increase':
        new_qty = current_qty + 1
    elif action == 'decrease':
        new_qty = current_qty - 1 if current_qty > 1 else 1
    else:
        return redirect('cart:cart_view')

    cart[str(id)]['qty'] = new_qty if new_qty >= 1 else 1
    save_cart(request, cart)

    send_security_event(f"SECURE: update_quantity product_id={id} set to {new_qty}", request.META.get("REMOTE_ADDR"))
    return redirect('cart:cart_view')


# ---------------- VULNERABLE endpoint (LAB only) ----------------
@csrf_exempt
def vuln_update_quantity(request, id):
    """
    LAB-VULN: intentionally vulnerable:
      - No CSRF protection
      - Accepts GET or POST
      - Accepts raw `qty` parameter and applies it directly
    Guarded: only available when DEBUG and VULNERABLE_MODE are enabled.
    """
    if not (settings.DEBUG and getattr(settings, "VULNERABLE_MODE", False)):
        return HttpResponseForbidden("Vulnerable endpoint disabled (not in lab mode).")

    cart = get_cart(request)

    qty_raw = None
    if request.method == 'POST':
        qty_raw = request.POST.get('qty')
        action = request.POST.get('action')
    else:
        qty_raw = request.GET.get('qty')
        action = request.GET.get('action')

    # If action present (increase/decrease) behave similarly but without checks
    if not qty_raw and action:
        current_qty = cart.get(str(id), {}).get('qty', 0)
        if action == 'increase':
            new_qty = current_qty + 1
        elif action == 'decrease':
            new_qty = current_qty - 1
        else:
            return redirect('cart:cart_view')
    else:
        try:
            new_qty = int(qty_raw)
        except (TypeError, ValueError):
            # invalid qty -> fallback to no-op
            return redirect('cart:cart_view')

    pid = str(id)
    if pid not in cart:
        # intentionally create a placeholder without DB validation
        cart[pid] = {
            'name': f"product_{id} (insecure placeholder)",
            'price': 0.0,
            'qty': new_qty
        }
    else:
        cart[pid]['qty'] = new_qty

    request.session['cart'] = cart
    request.session.modified = True

    send_security_event(f"VULN: vuln_update_quantity product_id={id} applied qty={new_qty}", request.META.get("REMOTE_ADDR"))
    return redirect('cart:cart_view')
