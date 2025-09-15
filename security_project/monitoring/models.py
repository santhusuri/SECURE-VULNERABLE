from django.db import models

class Incident(models.Model):
    ATTACK_TYPES = [
        ("suricata_alert", "Suricata Alert"),
        ("snort_alert", "Snort Alert"),
        ("sql_injection", "SQL Injection"),
        ("xss", "Cross-Site Scripting"),
        ("bruteforce", "Brute Force"),
        ("other", "Other"),
    ]

    attack_type = models.CharField(max_length=50, choices=ATTACK_TYPES, default="other")
    event_data = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action_taken = models.CharField(max_length=255, default="Logged")
    timestamp = models.DateTimeField(auto_now_add=True)
    suricata_raw = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.attack_type} from {self.ip_address} at {self.timestamp}"


class BlacklistEntry(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    added_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.ip_address} ({self.reason})"
