from django.shortcuts import render, get_object_or_404

from shipping.models import Shipment

def shipping_details(request, order_id):
    mode = request.session.get('sim_mode', 'secure')  # unified mode key
    shipment = get_object_or_404(Shipment, order_id=order_id)
    context = {
        'shipment': shipment,
        'mode': mode  # pass mode to template for conditional display if needed
    }
    template_name = 'shipping/shipment_detail.html'
    # Optionally use a different template in vulnerable mode, e.g.:
    # if mode == 'vulnerable':
    #     template_name = 'shipping/vuln_shipment_detail.html'
    return render(request, template_name, context)
