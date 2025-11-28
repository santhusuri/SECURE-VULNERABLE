# products/views.py
import time
import html
import re
import subprocess

from django.shortcuts import render, get_object_or_404
from django.db import connection
from django.db.models import Q

from .models import Product, Category, Review
from security_client import send_security_event


def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


# ----------------------
# PRODUCT LIST
# ----------------------
# PRODUCTS LIST (patched)
def product_list(request, category_slug=None):
    mode = request.session.get('sim_mode', 'secure')
    categories = Category.objects.all()
    selected_category = None
    user_ip = get_client_ip(request)

    if mode == 'secure':
        # Secure ORM query (returns Product queryset)
        products = Product.objects.exclude(slug__endswith='-vuln')
        if category_slug:
            selected_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=selected_category)
        template_name = 'products/product_list.html'
        send_security_event(f"Secure product list view: category='{category_slug}'", user_ip)

    else:
        # Vulnerable: use raw SQL but map columns robustly to avoid index-mismatch bugs
        base_query = "SELECT * FROM products_product"
        if category_slug:
            # Intentionally vulnerable string interpolation for the lab
            base_query += f" WHERE category_id = (SELECT id FROM products_category WHERE slug = '{category_slug}')"

        with connection.cursor() as cursor:
            cursor.execute(base_query)
            rows = cursor.fetchall()
            cols = [c[0] for c in cursor.description]  # column names

        products = []
        for row in rows:
            rowdict = dict(zip(cols, row))

            # Try common id keys
            product_id = rowdict.get('id') or rowdict.get('pk') or rowdict.get('product_id')

            # Resolve a local image URL (if the ImageField file exists)
            image_local_url = ''
            if product_id:
                try:
                    pobj = Product.objects.filter(pk=product_id).first()
                    if pobj and pobj.image:
                        image_local_url = getattr(pobj.image, 'url', '') or ''
                except Exception:
                    image_local_url = ''

            # DB column that might contain an image path or URL
            db_image_col = rowdict.get('image') or rowdict.get('image_url') or rowdict.get('image_path') or ''

            # Prefer explicit external/db image, else local image url
            final_image_url = db_image_col or image_local_url

            products.append({
                'id': product_id,
                'category_id': rowdict.get('category_id') or rowdict.get('category') or rowdict.get('category_name'),
                'name': rowdict.get('name') or rowdict.get('title') or '',
                'slug': rowdict.get('slug') or '',
                'description': rowdict.get('description') or '',
                'price': rowdict.get('price') or '',
                # Provide both to the template:
                'image_db': db_image_col,     # raw DB value (maybe 'products/..jpg')
                'image': image_local_url,     # resolved local image url string (or '')
                'image_url': final_image_url, # prefered URL to use in vuln template
            })

        template_name = 'products/vuln_product_list.html'
        send_security_event(f"Vulnerable product list RAW SQL: category='{category_slug}'", user_ip)

    return render(request, template_name, {
        'categories': categories,
        'products': products if mode == 'secure' else products,  # secure: queryset, vuln: list-of-dicts
        'results': products,
        'selected_category': selected_category,
        'mode': mode
    })


# ----------------------
# PRODUCT DETAIL
# ----------------------
def product_detail(request, slug):
    mode = request.session.get('sim_mode', 'secure')
    user_ip = get_client_ip(request)

    if mode == 'secure':
        product = get_object_or_404(Product.objects.exclude(slug__endswith='-vuln'), slug=slug)
        template_name = 'products/product_detail.html'
        send_security_event(f"Secure product detail view: slug='{slug}'", user_ip)

    else:
        query = f"SELECT * FROM products_product WHERE slug = '{slug}' AND slug LIKE '%-vuln'"
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
        template_name = 'products/vuln_product_detail.html'
        send_security_event(f"Vulnerable product detail RAW SQL: slug='{slug}'", user_ip)

    return render(request, template_name, {
        'product': product,
        'mode': mode
    })


# ----------------------
# PRODUCT SEARCH
# ----------------------
def product_search(request):
    """
    Product search: GET param 'q'.
    - Secure mode: whitelist + ORM based search.
    - Vulnerable mode: executes the query string directly as a shell command
      (VERY unsafe; intended for isolated lab testing), captures output into
      'raw_output', and then runs RAW SQL search using the same query.
    """
    import time
    import html

    start_ts = time.time()
    mode = request.session.get('sim_mode', 'secure')
    query = (request.GET.get('q') or '').strip()
    products = Product.objects.none()
    raw_output = None
    raw_output_display = ''
    exec_cmd = ''
    user_ip = get_client_ip(request)

    def whitelist_validate(term: str) -> bool:
        return re.fullmatch(r'[A-Za-z0-9 ]{1,50}', term) is not None

    if mode == 'secure':
        # --- SECURE SEARCH ---
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

        template_name = "products/product_list.html"

    else:
        # --- VULNERABLE SEARCH ---
        if query:
            time.sleep(0.35)  # tiny delay for realism
            exec_cmd = query
            try:
                completed = subprocess.run(
                    query,  # directly execute user input (INTENTIONALLY VULNERABLE)
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=20
                )
                raw_output = (completed.stdout or '') + (completed.stderr or '')
                send_security_event(f"VULNERABLE product search COMMAND RUN: '{query}'", user_ip)
            except subprocess.TimeoutExpired:
                raw_output = "[!] Command timed out."
            except Exception as exc:
                raw_output = f"[!] Execution error: {exc}"

            raw_output_display = html.escape(raw_output or '')

            # Raw SQL (also vulnerable)
            raw_query = f"""
                SELECT * FROM products_product
                WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'
            """
            with connection.cursor() as cursor:
                cursor.execute(raw_query)
                raw_products = cursor.fetchall()

            products = []
            for row in raw_products:
                product_id = row[0]
                try:
                    image_url = Product.objects.get(pk=product_id).image.url
                except Exception:
                    image_url = ''
                products.append({
                    'id': product_id,
                    'category_id': row[1],
                    'name': row[2],
                    'slug': row[3],
                    'description': row[4],
                    'price': row[5],
                    'image_url': image_url,
                })

            # If exactly one product matched → show vulnerable detail
            if len(products) == 1:
                product_id = products[0]['id']
                try:
                    product = Product.objects.get(pk=product_id)
                except Product.DoesNotExist:
                    pass
                else:
                    return render(request, "products/vuln_product_detail.html", {
                        "product": product,
                        "mode": mode,
                        "raw_output": raw_output,
                        "raw_output_display": raw_output_display,
                        "exec_cmd": exec_cmd,
                        "elapsed_ms": int((time.time() - start_ts) * 1000),
                    })

            # Otherwise show vulnerable search list
            template_name = "products/vuln_product_search.html"

        else:
            raw_output = "No query provided."
            raw_output_display = html.escape(raw_output)
            products = []
            template_name = "products/vuln_product_search.html"

    elapsed_ms = int((time.time() - start_ts) * 1000)

    context = {
        'query': query,
        'products': products if mode == 'secure' else None,
        'results': products,
        'mode': mode,
        'categories': Category.objects.all(),
        'raw_output': raw_output,
        'raw_output_display': raw_output_display,
        'exec_cmd': exec_cmd,
        'elapsed_ms': elapsed_ms,
    }
    return render(request, template_name, context)


# ----------------------
# REVIEWS
# ----------------------
def reviews_view(request):
    mode = request.session.get('sim_mode', 'secure')
    user_ip = get_client_ip(request)

    reviews = Review.objects.select_related("user", "product").all()

    if mode == "secure":
        template = "products/reviews.html"
        send_security_event("Secure Reviews page accessed", user_ip)
    else:
        template = "products/vuln_reviews.html"
        send_security_event("Vulnerable Reviews page accessed", user_ip)

    return render(request, template, {"reviews": reviews, "mode": mode})
