from rest_framework import serializers
from .models import Incident

class EventSerializer(serializers.Serializer):
    event = serializers.CharField()
    ip = serializers.IPAddressField()
