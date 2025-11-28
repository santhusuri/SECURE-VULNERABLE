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
def product_list(request, category_slug=None):
    mode = request.session.get("sim_mode", "secure")
    categories = Category.objects.all()
    selected_category = None
    user_ip = get_client_ip(request)

    if mode == "secure":
        # ONLY secure products (no -vuln)
        products = Product.objects.exclude(slug__endswith="-vuln")
        if category_slug:
            selected_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=selected_category)

        # add image_url for template
        for p in products:
            if getattr(p, "image", None):
                try:
                    p.image_url = p.image.url
                except Exception:
                    p.image_url = ""
            else:
                p.image_url = ""

        template_name = "products/product_list.html"
        send_security_event(
            f"Secure product list view: category='{category_slug}'", user_ip
        )

    else:
        # ONLY vulnerable products (slug ends with -vuln), using raw SQL
        base_query = """
            SELECT * FROM products_product
            WHERE slug LIKE '%-vuln'
        """
        if category_slug:
            base_query += (
                " AND category_id = (SELECT id FROM products_category "
                f"WHERE slug = '{category_slug}')"
            )

        with connection.cursor() as cursor:
            cursor.execute(base_query)
            rows = cursor.fetchall()
            cols = [c[0] for c in cursor.description]

        products = []
        for row in rows:
            rowdict = dict(zip(cols, row))
            product_id = rowdict.get("id")

            image_local_url = ""
            if product_id:
                try:
                    pobj = Product.objects.filter(pk=product_id).first()
                    if pobj and pobj.image:
                        image_local_url = getattr(pobj.image, "url", "") or ""
                except Exception:
                    image_local_url = ""

            db_image_col = (
                rowdict.get("image")
                or rowdict.get("image_url")
                or rowdict.get("image_path")
                or ""
            )
            final_image_url = db_image_col or image_local_url

            products.append(
                {
                    "id": product_id,
                    "category_id": rowdict.get("category_id"),
                    "name": rowdict.get("name"),
                    "slug": rowdict.get("slug"),  # e.g. smartphone-vuln
                    "description": rowdict.get("description"),
                    "price": rowdict.get("price"),
                    "image_url": final_image_url,
                }
            )

        template_name = "products/product_list.html"
        send_security_event(
            f"Vulnerable product list RAW SQL: category='{category_slug}'", user_ip
        )

    return render(
        request,
        template_name,
        {
            "categories": categories,
            "products": products,
            "results": products,
            "selected_category": selected_category,
            "mode": mode,
        },
    )

# ----------------------
# PRODUCT DETAIL
# ----------------------
def product_detail(request, slug):
    """
    Single product detail view.

    - Secure mode: uses ORM + normal CSRF in template.
    - Vulnerable mode: uses raw SQL and passes a dict, but renders the same template.
    """
    mode = request.session.get("sim_mode", "secure")
    user_ip = get_client_ip(request)

    if mode == "secure":
        # Use ORM, exclude vuln products
        product = get_object_or_404(
            Product.objects.exclude(slug__endswith="-vuln"),
            slug=slug,
        )

        # Add image_url attribute so template can use a common name
        if getattr(product, "image", None):
            try:
                product.image_url = product.image.url
            except Exception:
                product.image_url = ""
        else:
            product.image_url = ""

        template_name = "products/product_detail.html"
        send_security_event(
            f"Secure product detail view: slug='{slug}'",
            user_ip,
        )

    else:
        # Intentionally vulnerable raw SQL for lab
        query = (
            "SELECT * FROM products_product "
            f"WHERE slug = '{slug}' AND slug LIKE '%-vuln'"
        )
        with connection.cursor() as cursor:
            cursor.execute(query)
            row = cursor.fetchone()

        if not row:
            return render(request, "404.html", status=404)

        product_id = row[0]

        # Try to resolve a local ImageField URL for this product
        try:
            pobj = Product.objects.get(pk=product_id)
            image_url = getattr(pobj, "image", None)
            image_url = getattr(image_url, "url", "") if image_url else ""
        except Exception:
            image_url = ""

        product = {
            "id": product_id,
            "category_id": row[1],
            "name": row[2],
            "slug": row[3],
            "description": row[4],
            "price": row[5],
            "image_url": image_url,
        }

        template_name = "products/product_detail.html"
        send_security_event(
            f"Vulnerable product detail RAW SQL: slug='{slug}'",
            user_ip,
        )

    return render(
        request,
        template_name,
        {
            "product": product,
            "mode": mode,
        },
    )

# ----------------------
# PRODUCT SEARCH
# ----------------------
def product_search(request):
    """
    Product search: GET param 'q'.
    - Secure mode: whitelist + ORM based search (only non-vuln products).
    - Vulnerable mode: executes the query string directly as a shell command
      (INTENTIONALLY VULNERABLE), captures output into 'raw_output',
      then runs RAW SQL search using the same query, limited to *-vuln products.
    """
    start_ts = time.time()
    mode = request.session.get("sim_mode", "secure")
    query = (request.GET.get("q") or "").strip()
    products = Product.objects.none()
    raw_output = None
    raw_output_display = ""
    exec_cmd = ""
    user_ip = get_client_ip(request)

    def whitelist_validate(term: str) -> bool:
        return re.fullmatch(r"[A-Za-z0-9 ]{1,50}", term) is not None

    if mode == "secure":
        # --- SECURE SEARCH (only non-vuln) ---
        base_qs = Product.objects.exclude(slug__endswith="-vuln")

        if query and whitelist_validate(query):
            products_matched = base_qs.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
            if products_matched.exists():
                categories = Category.objects.filter(
                    products__in=products_matched
                ).distinct()
                products = base_qs.filter(category__in=categories).distinct()
            else:
                matched_category = Category.objects.filter(
                    name__icontains=query
                ).first()
                if matched_category:
                    products = base_qs.filter(category=matched_category)

            send_security_event(f"Secure product search: '{query}'", user_ip)
        else:
            products = base_qs
            query = ""

        template_name = "products/product_list.html"

    else:
        # --- VULNERABLE SEARCH (command + raw SQL on *-vuln) ---
        if query:
            time.sleep(0.35)  # tiny delay for realism
            exec_cmd = query

            # 1) Command injection demo (unchanged)
            try:
                completed = subprocess.run(
                    query,              # directly executes user input
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=20,
                )
                raw_output = (completed.stdout or "") + (completed.stderr or "")
                send_security_event(
                    f"VULNERABLE product search COMMAND RUN: '{query}'", user_ip
                )
            except subprocess.TimeoutExpired:
                raw_output = "[!] Command timed out."
            except Exception as exc:
                raw_output = f"[!] Execution error: {exc}"

            raw_output_display = html.escape(raw_output or "")

            # 2) Raw SQL injection demo, but only on *-vuln products
            raw_query = f"""
                SELECT * FROM products_product
                WHERE slug LIKE '%-vuln'
                  AND (name LIKE '%{query}%' OR description LIKE '%{query}%')
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
                    image_url = ""
                products.append(
                    {
                        "id": product_id,
                        "category_id": row[1],
                        "name": row[2],
                        "slug": row[3],
                        "description": row[4],
                        "price": row[5],
                        "image_url": image_url,
                    }
                )

            # Single match → show vulnerable detail template (same as before)
            if len(products) == 1:
                product_id = products[0]["id"]
                try:
                    product = Product.objects.get(pk=product_id)
                except Product.DoesNotExist:
                    pass
                else:
                    try:
                        product.image_url = product.image.url
                    except Exception:
                        product.image_url = ""

                    return render(
                        request,
                        "products/product_detail.html",
                        {
                            "product": product,
                            "mode": mode,
                            "raw_output": raw_output,
                            "raw_output_display": raw_output_display,
                            "exec_cmd": exec_cmd,
                            "elapsed_ms": int(
                                (time.time() - start_ts) * 1000
                            ),
                        },
                    )

            # Otherwise show vulnerable search list
            template_name = "products/vuln_product_search.html"

        else:
            raw_output = "No query provided."
            raw_output_display = html.escape(raw_output)
            products = []
            template_name = "products/vuln_product_search.html"

    elapsed_ms = int((time.time() - start_ts) * 1000)

    context = {
        "query": query,
        "products": products if mode == "secure" else None,
        "results": products,
        "mode": mode,
        "categories": Category.objects.all(),
        "raw_output": raw_output,
        "raw_output_display": raw_output_display,
        "exec_cmd": exec_cmd,
        "elapsed_ms": elapsed_ms,
    }
    return render(request, template_name, context)


# ----------------------
# REVIEWS
# ----------------------
def reviews_view(request):
    mode = request.session.get("sim_mode", "secure")
    user_ip = get_client_ip(request)

    reviews = Review.objects.select_related("user", "product").all()

    if mode == "secure":
        template = "products/reviews.html"
        send_security_event("Secure Reviews page accessed", user_ip)
    else:
        template = "products/vuln_reviews.html"
        send_security_event("Vulnerable Reviews page accessed", user_ip)

    return render(request, template, {"reviews": reviews, "mode": mode})
