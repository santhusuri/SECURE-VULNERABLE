from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
from .serializers import EventSerializer, IncidentSerializer
from .utils import add_blacklist_entry, block_ip_system, revoke_session_on_project_a
from .models import Incident


@api_view(["POST"])
def receive_log(request):
    serializer = EventSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=400)

    # Model's save() will auto-assign severity
    incident = serializer.save()

    if incident.severity == "High" and incident.ip_address:
        add_blacklist_entry(incident.ip_address, reason=f"Detected {incident.attack_type}")
        block_ip_system(incident.ip_address)
        revoke_session_on_project_a(incident.ip_address)

    return Response({
        "status": "alert" if incident.severity == "High" else "ok",
        "attack": incident.attack_type,
        "severity": incident.severity,
        "action": incident.action_taken
    }, status=201 if incident.severity == "High" else 200)


def dashboard(request):
    incidents = Incident.objects.order_by("-timestamp")[:50]
    return render(request, "dashboard.html", {"incidents": incidents})


@require_POST
def clear_logs(request):
    Incident.objects.all().delete()
    messages.success(request, "All security logs have been cleared.")
    return redirect('dashboard')


def incidents_api(request):
    """
    Return only new incidents since the last_id provided by the frontend.
    """
    last_id = request.GET.get("last_id")
    qs = Incident.objects.order_by("id")

    if last_id and last_id.isdigit():
        qs = qs.filter(id__gt=int(last_id))

    serializer = IncidentSerializer(qs, many=True)
    return JsonResponse(serializer.data, safe=False)
