from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from .serializers import EventSerializer
from .utils import add_blacklist_entry, block_ip_system, revoke_session_on_project_a
from .models import Incident
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.contrib import messages


@api_view(["POST"])
def receive_log(request):
    """
    REST endpoint for Project A to push logs/events.
    Expects JSON: {"event": "...", "ip": "x.x.x.x"}
    """
    serializer = EventSerializer(data=request.data)
    if not serializer.is_valid():
        return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    event = serializer.validated_data["event"]
    ip = serializer.validated_data["ip"]

    attack_type = None
    lowered = event.lower()
    if any(x in lowered for x in ["' or 1=1", "union select", "drop table", "--"]):
        attack_type = "sql_injection"
    elif any(x in lowered for x in ["<script>", "onerror=", "alert("]):
        attack_type = "xss"
    elif "failed login" in lowered or "invalid password" in lowered:
        attack_type = "bruteforce"

    if attack_type:
        inc = Incident.objects.create(
            attack_type=attack_type,
            event_data=event,
            ip_address=ip,
            action_taken="Logged by REST ingest"
        )

        # Example AIRS actions
        created, entry = add_blacklist_entry(ip, reason=f"Detected {attack_type} via REST")
        blocked_ok, blocked_msg = block_ip_system(ip)
        revoked_ok, revoked_msg = revoke_session_on_project_a(ip)

        inc.action_taken = f"blacklist_created={created}; iptables={blocked_msg}; revoke={revoked_msg}"
        inc.save()

        return Response(
            {"status": "alert", "attack": attack_type, "action": inc.action_taken},
            status=status.HTTP_201_CREATED,
        )

    # Log informational event
    Incident.objects.create(
        attack_type="other",
        event_data=event,
        ip_address=ip,
        action_taken="logged_rest_noalert",
    )
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


def dashboard(request):
    """Simple dashboard UI to view incidents"""
    incidents = Incident.objects.order_by("-timestamp")
    return render(request, "dashboard.html", {"incidents": incidents})
    

@require_POST
def clear_logs(request):
    Incident.objects.all().delete()
    messages.success(request, "All security logs have been cleared.")
    return redirect('dashboard')  # Change to your dashboard url name
