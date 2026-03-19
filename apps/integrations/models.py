from django.db import models

from apps.common.models import TimeStampedModel


class IntegrationEvent(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    event_type = models.CharField(max_length=120)
    payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    retry_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["status"]),
        ]


class ExternalSyncLog(TimeStampedModel):
    STATUS_SUCCESS = "success"
    STATUS_FAILED = "failed"

    STATUS_CHOICES = [
        (STATUS_SUCCESS, "Success"),
        (STATUS_FAILED, "Failed"),
    ]

    provider = models.CharField(max_length=50)
    entity_type = models.CharField(max_length=50)
    entity_id = models.CharField(max_length=64)
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    class Meta:
        ordering = ["-created_at"]
