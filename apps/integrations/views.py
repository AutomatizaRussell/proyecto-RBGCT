from rest_framework import decorators, response, status, viewsets

from apps.common.permissions import IsStaffOrReadOnly

from .models import IntegrationEvent
from .serializers import IntegrationEventSerializer
from .services import IntegrationEventService


class IntegrationEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = IntegrationEvent.objects.all()
    serializer_class = IntegrationEventSerializer
    permission_classes = [IsStaffOrReadOnly]
    filterset_fields = ["status", "event_type"]
    search_fields = ["event_type"]
    ordering_fields = ["created_at", "processed_at", "retry_count"]

    @decorators.action(detail=True, methods=["post"])
    def deliver(self, request, pk=None):
        event = self.get_object()
        event = IntegrationEventService.deliver_event(event)
        serializer = self.get_serializer(event)
        return response.Response(serializer.data, status=status.HTTP_200_OK)
