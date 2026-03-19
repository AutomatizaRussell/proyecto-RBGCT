import requests
from django.conf import settings

from .base import ClientResponse


class OneDriveClient:
    def upload_file(self, filename: str, content: bytes) -> ClientResponse:
        if not settings.ONEDRIVE_BASE_URL or not settings.ONEDRIVE_ACCESS_TOKEN:
            return ClientResponse(ok=False, status_code=400, error="OneDrive integration is not configured.")

        headers = {
            "Authorization": f"Bearer {settings.ONEDRIVE_ACCESS_TOKEN}",
            "Content-Type": "application/octet-stream",
        }
        response = requests.put(f"{settings.ONEDRIVE_BASE_URL}/{filename}:/content", headers=headers, data=content, timeout=30)
        try:
            data = response.json()
        except ValueError:
            data = {"text": response.text}
        return ClientResponse(ok=response.ok, status_code=response.status_code, payload=data, error="" if response.ok else response.text)
