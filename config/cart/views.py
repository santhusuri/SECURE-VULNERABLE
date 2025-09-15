from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from products.models import Product
from django.views.decorators.http import require_POST

def get_cart(request):
    """Retrieves the shopping cart from session. If no cart exists, returns an empty dict."""
    return request.session.get('cart', {})

def save_cart(request, cart):
    """Saves the updated cart into session."""
    request.session['cart'] = cart
    
def cart_view(request):
    cart = get_cart(request)
    total = 0
    for item in cart.values():
        item['subtotal'] = item['price'] * item['qty']
        total += item['subtotal']
    return render(request, 'cart/cart_view.html', {
        'cart': cart,
        'total': total
    })




def add_to_cart(request, product_id):
    """
    Adds a product to the shopping cart.
    Behavior depends on current mode:
    - Secure mode: validates product existence.
    - Vulnerable mode: no validation (for demonstration).
    """
    mode = request.session.get('sim_mode', 'secure')  # unified mode key
    cart = get_cart(request)
    if mode == 'secure':
        product = get_object_or_404(Product, id=product_id)
    else:
        product = Product.objects.get(id=product_id)  # no validation

    if str(product.id) not in cart:
        cart[str(product.id)] = {
            'name': product.name,
            'price': float(product.price),
            'qty': 1
        }
    else:
        cart[str(product.id)]['qty'] += 1
    save_cart(request, cart)

    if mode == 'secure':
        messages.success(request, f"{product.name} added to cart.")
    else:
        messages.warning(request, f"(Vulnerable) {product.name} added to cart without checks.")
    return redirect('cart:cart_view')

def remove_from_cart(request, product_id):
    """Removes a specific product from the shopping cart."""
    cart = get_cart(request)
    if str(product_id) in cart:
        del cart[str(product_id)]
        save_cart(request, cart)
        messages.info(request, "Item removed from cart.")
    return redirect('cart:cart_view')

def clear_cart(request):
    """Empties the entire shopping cart."""
    save_cart(request, {})
    messages.info(request, "Cart cleared.")
    return redirect('cart:cart_view')

@require_POST
def update_quantity(request, id):
    product = get_object_or_404(Product, id=id)
    action = request.POST.get('action')
    cart = request.session.get('cart', {})
    current_qty = cart.get(str(id), {}).get('qty', 0)
    if action == 'increase':
        new_qty = current_qty + 1
    elif action == 'decrease':
        new_qty = current_qty - 1 if current_qty > 1 else 1  # minimum qty = 1
    else:
        return redirect('cart:cart_view')

    if new_qty >= 1:
        cart[str(id)]['qty'] = new_qty
    else:
        cart.pop(str(id), None)
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart:cart_view')
