from django.db import models
from django.utils import timezone


class Incident(models.Model):
    ATTACK_TYPES = [
        ("suricata_alert", "Suricata Alert"),
        ("snort_alert", "Snort Alert"),
        ("sql_injection", "SQL Injection"),
        ("xss", "Cross-Site Scripting"),
        ("bruteforce", "Brute Force"),
        ("command_injection", "Command Injection"),
        ("other", "Other"),
    ]

    SEVERITY_LEVELS = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
        ("Critical", "Critical"),
    ]

    # Mapping for auto-severity
    SEVERITY_MAP = {
        "sql_injection": "High",
        "command_injection": "High",
        "suricata_alert": "High",
        "snort_alert": "High",
        "xss": "Medium",
        "bruteforce": "Medium",
        "other": "Low",
    }

    attack_type = models.CharField(max_length=50, choices=ATTACK_TYPES, default="other")
    event_data = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action_taken = models.CharField(max_length=255, default="Logged")
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default="Low")
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-assign severity & blacklist dangerous IPs."""
        self.severity = self.SEVERITY_MAP.get(self.attack_type, "Low")
        super().save(*args, **kwargs)

        # Auto-blacklist High/Critical attackers
        if self.severity in ["High", "Critical"] and self.ip_address:
            BlacklistEntry.objects.get_or_create(
                ip_address=self.ip_address,
                defaults={"reason": f"Auto-blacklisted due to {self.attack_type} ({self.severity})"}
            )
            # Update action_taken
            if self.action_taken == "Logged":
                self.action_taken = "Blacklisted"
                super().save(update_fields=["action_taken"])

    def __str__(self):
        return f"{self.attack_type} ({self.severity}) from {self.ip_address} at {self.timestamp}"


class BlacklistEntry(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    added_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.ip_address} ({self.reason or 'No reason'})"
