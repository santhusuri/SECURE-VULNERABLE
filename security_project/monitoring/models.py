from django.db import models

class Incident(models.Model):
    ATTACK_TYPES = [
        ("suricata_alert", "Suricata Alert"),
        ("snort_alert", "Snort Alert"),
        ("sql_injection", "SQL Injection"),
        ("xss", "Cross-Site Scripting"),
        ("bruteforce", "Brute Force"),
        ("command_injection", "Command Injection"),  # 👈 add here
        ("other", "Other"),
    ]

    SEVERITY_LEVELS = [
        ("Low", "Low"),
        ("Medium", "Medium"),
        ("High", "High"),
    ]

    attack_type = models.CharField(max_length=50, choices=ATTACK_TYPES, default="other")
    event_data = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    action_taken = models.CharField(max_length=255, default="Logged")
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default="Low")
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Auto-assign severity based on attack_type."""
        if self.attack_type in ["sql_injection", "suricata_alert", "snort_alert"]:
            self.severity = "High"
        elif self.attack_type in ["xss", "bruteforce"]:
            self.severity = "Medium"
        elif self.attack_type in ["command_injection"]:
            self.severity = "Low"
        else:
            self.severity = "Low"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attack_type} ({self.severity}) from {self.ip_address} at {self.timestamp}"


class BlacklistEntry(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    added_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.ip_address} ({self.reason})"

