from rest_framework import serializers
from .models import Incident

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['attack_type', 'event_data', 'ip_address', 'severity', 'action_taken']

    def create(self, validated_data):
        # Auto-assign severity
        attack_type = validated_data.get("attack_type", "other")
        if attack_type in ["sql_injection", "xss", "bruteforce"]:
            validated_data["severity"] = "High"
        elif attack_type == "other":
            validated_data["severity"] = "Low"
        else:
            validated_data["severity"] = "Medium"
        return super().create(validated_data)


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['id', 'attack_type', 'event_data', 'ip_address', 'action_taken', 'severity', 'timestamp']
