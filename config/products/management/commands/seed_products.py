from django.core.management.base import BaseCommand
from products.models import Category, Product
from django.core.files.base import ContentFile
import base64

# 1x1px transparent GIF (to avoid internet download issues)
DUMMY_IMAGE = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="
)

class Command(BaseCommand):
    help = "Delete all products and seed demo products with secure images and vuln image URLs"

    def handle(self, *args, **kwargs):
        # Step 1: Delete old products
        Product.objects.all().delete()
        self.stdout.write(self.style.WARNING("🗑️ Deleted all products."))

        # Step 2: Ensure categories exist
        electronics, _ = Category.objects.get_or_create(name="Electronics", slug="electronics")
        clothing, _ = Category.objects.get_or_create(name="Clothing", slug="clothing")
        books, _ = Category.objects.get_or_create(name="Books", slug="books")

        # Step 3: Demo products with both secure + vuln images
        demo_products = [
            (electronics, "Smartphone", "smartphone", "A high-performance smartphone with 5G connectivity.", 699.99, 50, "https://via.placeholder.com/200x120?text=Smartphone"),
            (electronics, "Laptop", "laptop", "Lightweight laptop with 16GB RAM and 512GB SSD.", 1199.99, 30, "https://via.placeholder.com/200x120?text=Laptop"),
            (clothing, "T-Shirt", "t-shirt", "Comfortable cotton T-shirt available in multiple colors.", 19.99, 200, "https://via.placeholder.com/200x120?text=T-Shirt"),
            (clothing, "Jeans", "jeans", "Slim-fit denim jeans with a stylish design.", 49.99, 120, "https://via.placeholder.com/200x120?text=Jeans"),
            (books, "Python Programming", "python-programming", "Learn Python programming from beginner to advanced.", 39.99, 100, "https://via.placeholder.com/200x120?text=Python+Book"),
            (books, "Django Web Development", "django-web-development", "Master Django framework with real-world projects.", 44.99, 80, "https://via.placeholder.com/200x120?text=Django+Book"),
        ]

        for category, name, slug, desc, price, stock, img_url in demo_products:
            product = Product.objects.create(
                category=category,
                name=name,
                slug=slug,
                description=desc,
                price=price,
                stock=stock,
                image_url=img_url  # vulnerable image URL ✅
            )
            # Attach a dummy local image for secure mode ✅
            product.image.save(f"{slug}.jpg", ContentFile(DUMMY_IMAGE), save=True)
            self.stdout.write(self.style.SUCCESS(f"✅ Created {name}"))

        self.stdout.write(self.style.SUCCESS("🎉 6 demo products created successfully with images"))
