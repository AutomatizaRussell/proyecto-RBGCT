from dataclasses import dataclass
from typing import Any


@dataclass
class ClientResponse:
    ok: bool
    status_code: int
    payload: dict[str, Any] | None = None
    error: str = ""
