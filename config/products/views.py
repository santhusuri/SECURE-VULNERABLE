from django.shortcuts import render, get_object_or_404
from django.db import connection
from .models import Product, Category
from django.db.models import Q
import subprocess, re
from security_client import send_security_event

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

def product_list(request, category_slug=None):
    mode = request.session.get('sim_mode', 'secure')  # unified mode key
    categories = Category.objects.all()
    selected_category = None
    products = []
    user_ip = get_client_ip(request)

    if mode == 'secure':
        products = Product.objects.all()
        if category_slug:
            selected_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=selected_category)
        send_security_event(f"Secure product list view: category='{category_slug}'", user_ip)
    elif mode == 'vulnerable':
        base_query = "SELECT * FROM products_product"
        if category_slug:
            base_query += f" WHERE category_id = (SELECT id FROM products_category WHERE slug = '{category_slug}')"
        with connection.cursor() as cursor:
            cursor.execute(base_query)
            raw_products = cursor.fetchall()
        products = [
            {
                'id': row[0],
                'category_id': row[1],
                'name': row[2],
                'slug': row[3],
                'description': row[4],
                'price': row[5],
            }
            for row in raw_products
        ]
        send_security_event(f"Vulnerable product list view RAW SQL: category='{category_slug}'", user_ip)

    return render(request, 'products/product_list.html', {
        'categories': categories,
        'products': products,
        'selected_category': selected_category,
        'mode': mode
    })

def product_detail(request, slug):
    mode = request.session.get('sim_mode', 'secure')  # unified mode key
    user_ip = get_client_ip(request)
    if mode == 'secure':
        product = get_object_or_404(Product, slug=slug)
        send_security_event(f"Secure product detail view: slug='{slug}'", user_ip)
    elif mode == 'vulnerable':
        query = f"SELECT * FROM products_product WHERE slug = '{slug}'"
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()
        if not row:
            return render(request, '404.html', status=404)
        product = {
            'id': row[0],
            'category_id': row[1],
            'name': row[2],
            'slug': row[3],
            'description': row[4],
            'price': row[5],
        }
        send_security_event(f"Vulnerable product detail view RAW SQL: slug='{slug}'", user_ip)
    return render(request, 'products/product_detail.html', {
        'product': product,
        'mode': mode
    })

def product_search(request):
    mode = request.session.get('sim_mode', 'secure')  # unified mode key
    query = (request.GET.get('q') or '').strip()
    products = Product.objects.none()
    raw_output = None
    user_ip = get_client_ip(request)

    def whitelist_validate(term: str) -> bool:
        return re.fullmatch(r'[A-Za-z0-9 ]{1,50}', term) is not None

    if mode == 'secure':
        if query and whitelist_validate(query):
            products_matched = Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
            if products_matched.exists():
                categories = Category.objects.filter(products__in=products_matched).distinct()
                products = Product.objects.filter(category__in=categories).distinct()
            else:
                matched_category = Category.objects.filter(name__icontains=query).first()
                if matched_category:
                    products = Product.objects.filter(category=matched_category)
            send_security_event(f"Secure product search: '{query}'", user_ip)
        else:
            products = Product.objects.all()
            query = ''
    else:
        if query:
            try:
                completed = subprocess.run(
                    query,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                raw_output = (completed.stdout or '') + (completed.stderr or '')
                send_security_event(f"Vulnerable product search / command injection: '{query}'", user_ip)
            except subprocess.TimeoutExpired:
                raw_output = "[!] Command timed out."
                send_security_event(f"Vulnerable product search TIMEOUT: '{query}'", user_ip)
            except Exception as exc:
                raw_output = f"[!] Execution error: {exc}"
                send_security_event(f"Vulnerable product search ERROR: '{query}' -> {exc}", user_ip)
        else:
            raw_output = "No query provided."

    return render(request, 'products/product_list.html', {
        'query': query,
        'products': products if mode == 'secure' else None,
        'results': products,
        'mode': mode,
        'categories': Category.objects.all(),
        'raw_output': raw_output
    })
