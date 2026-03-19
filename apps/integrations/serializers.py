from rest_framework import serializers

from .models import IntegrationEvent


class IntegrationEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegrationEvent
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")
