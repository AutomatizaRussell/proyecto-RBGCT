from django.contrib import admin

from .models import ExternalSyncLog, IntegrationEvent


@admin.register(IntegrationEvent)
class IntegrationEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "status", "retry_count", "created_at", "processed_at")
    list_filter = ("status", "event_type")
    search_fields = ("event_type",)


@admin.register(ExternalSyncLog)
class ExternalSyncLogAdmin(admin.ModelAdmin):
    list_display = ("id", "provider", "entity_type", "entity_id", "status", "created_at")
    list_filter = ("provider", "status")
