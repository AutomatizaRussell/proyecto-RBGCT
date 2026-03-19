from django.utils import timezone

from .clients.n8n import N8NClient
from .models import ExternalSyncLog, IntegrationEvent


class IntegrationEventService:
    @staticmethod
    def queue_event(event_type: str, payload: dict) -> IntegrationEvent:
        return IntegrationEvent.objects.create(event_type=event_type, payload=payload)

    @staticmethod
    def deliver_event(event: IntegrationEvent) -> IntegrationEvent:
        client = N8NClient()
        result = client.send_event({"event_type": event.event_type, "payload": event.payload})
        event.retry_count += 1
        event.processed_at = timezone.now()
        if result.ok:
            event.status = IntegrationEvent.STATUS_SENT
            event.last_error = ""
            ExternalSyncLog.objects.create(
                provider="n8n",
                entity_type="integration_event",
                entity_id=str(event.id),
                request_payload=event.payload,
                response_payload=result.payload or {},
                status=ExternalSyncLog.STATUS_SUCCESS,
            )
        else:
            event.status = IntegrationEvent.STATUS_FAILED
            event.last_error = result.error
            ExternalSyncLog.objects.create(
                provider="n8n",
                entity_type="integration_event",
                entity_id=str(event.id),
                request_payload=event.payload,
                response_payload=result.payload or {"error": result.error},
                status=ExternalSyncLog.STATUS_FAILED,
            )
        event.save(update_fields=["retry_count", "processed_at", "status", "last_error", "updated_at"])
        return event
