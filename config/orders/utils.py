from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def generate_invoice(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # Header
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 750, "Order Invoice")

    # Order Info
    p.setFont("Helvetica", 12)
    p.drawString(50, 710, f"Order ID: {order.id}")
    p.drawString(50, 690, f"Customer: {order.user.username if order.user else 'Guest'}")
    p.drawString(50, 670, f"Date: {order.created_at.strftime('%B %d, %Y %I:%M %p')}")
    p.drawString(50, 650, f"Total: ${order.total}")

    # Table Header
    y = 610
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Product")
    p.drawString(250, y, "Quantity")
    p.drawString(350, y, "Price")
    p.line(50, y-5, 550, y-5)

    # Table Rows
    p.setFont("Helvetica", 12)
    y -= 30
    for item in order.items.all():
        p.drawString(50, y, item.product.name[:30])  # truncate long names
        p.drawString(260, y, str(item.quantity))
        p.drawString(360, y, f"${item.price}")
        y -= 20

    # Footer
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(50, 100, "Thank you for shopping with us!")

    p.showPage()
    p.save()
    buffer.seek(0)

    return HttpResponse(buffer, content_type='application/pdf')
