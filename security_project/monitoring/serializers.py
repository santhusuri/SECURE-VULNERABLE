from rest_framework import serializers
from .models import Incident

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['attack_type', 'event_data', 'ip_address', 'action_taken']
        # 👆 severity excluded (auto-assigned in model)


class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = ['id', 'attack_type', 'event_data', 'ip_address', 'action_taken', 'severity', 'timestamp']
