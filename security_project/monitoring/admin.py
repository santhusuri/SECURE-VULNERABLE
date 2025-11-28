from django.contrib import admin
from django.utils.html import format_html
from .models import Incident, BlacklistEntry


# === Admin Actions ===
@admin.action(description="Block selected incidents' IPs")
def block_selected_incident_ips(modeladmin, request, queryset):
    """Block IPs from selected incidents."""
    for incident in queryset:
        if incident.ip_address:
            BlacklistEntry.objects.get_or_create(
                ip_address=incident.ip_address,
                defaults={"reason": f"Blocked via Incident Admin (Attack: {incident.attack_type})"}
            )
            # Update incident action_taken
            incident.action_taken = "Blacklisted"
            incident.save(update_fields=["action_taken"])


@admin.action(description="Unblock selected IPs")
def unblock_selected_ips(modeladmin, request, queryset):
    """Unblock IPs from blacklist and update related incidents."""
    for entry in queryset:
        ip = entry.ip_address
        entry.delete()  # remove blacklist entry
        # Reset related incidents
        Incident.objects.filter(ip_address=ip, action_taken="Blacklisted").update(action_taken="Logged")


# === Incident Admin ===
@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("attack_type", "colored_severity", "ip_address", "timestamp", "action_status")
    list_filter = ("attack_type", "severity", "timestamp")
    search_fields = ("event_data", "ip_address")
    ordering = ("-timestamp",)
    actions = [block_selected_incident_ips]

    def colored_severity(self, obj):
        """Show severity with colored badge."""
        color_map = {
            "Low": "#22c55e",      # green
            "Medium": "#facc15",   # yellow
            "High": "#ef4444",     # red
            "Critical": "#b91c1c", # dark red
        }
        color = color_map.get(obj.severity, "gray")
        return format_html(
            '<span style="padding:2px 6px; border-radius:6px; background:{}; color:white; font-weight:bold;">{}</span>',
            color, obj.severity
        )

    colored_severity.short_description = "Severity"

    def action_status(self, obj):
        """Custom column: 🚨 if blacklisted, gray otherwise."""
        if obj.action_taken == "Blacklisted":
            return format_html('<span style="color:red; font-weight:bold;">🚨 {}</span>', obj.action_taken)
        elif obj.action_taken == "Logged":
            return format_html('<span style="color:gray;">{}</span>', obj.action_taken)
        return obj.action_taken

    action_status.short_description = "Action Taken"


# === Blacklist Admin ===
@admin.register(BlacklistEntry)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "reason", "added_at")
    search_fields = ("ip_address", "reason")
    ordering = ("-added_at",)
    actions = [unblock_selected_ips]
