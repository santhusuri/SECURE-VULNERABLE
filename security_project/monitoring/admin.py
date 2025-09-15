from django.contrib import admin
from .models import Incident, BlacklistEntry

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ("attack_type", "ip_address", "timestamp", "action_taken")
    list_filter = ("attack_type", "timestamp")
    search_fields = ("event_data", "ip_address")


@admin.register(BlacklistEntry)
class BlacklistAdmin(admin.ModelAdmin):
    list_display = ("ip_address", "reason", "added_at")
    search_fields = ("ip_address",)
