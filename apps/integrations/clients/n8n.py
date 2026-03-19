import requests
from django.conf import settings

from .base import ClientResponse


class N8NClient:
    def send_event(self, payload: dict) -> ClientResponse:
        if not settings.N8N_WEBHOOK_URL:
            return ClientResponse(ok=False, status_code=400, error="N8N_WEBHOOK_URL is not configured.")
        response = requests.post(settings.N8N_WEBHOOK_URL, json=payload, timeout=10)
        try:
            data = response.json()
        except ValueError:
            data = {"text": response.text}
        return ClientResponse(ok=response.ok, status_code=response.status_code, payload=data, error="" if response.ok else response.text)
