from __future__ import annotations

import json
import socket
from http.client import HTTPResponse
from typing import Any, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .models import AccountingResponse, AccountingTimeout


class AccountingClient(Protocol):
    def post(self, document: Mapping[str, Any], idempotency_key: str) -> AccountingResponse:
        ...


class UrllibAccountingClient:
    def __init__(self, endpoint: str, timeout_seconds: float = 30.0):
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds

    def post(self, document: Mapping[str, Any], idempotency_key: str) -> AccountingResponse:
        request = Request(
            self.endpoint,
            data=json.dumps(document).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Idempotency-Key": idempotency_key,
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                return self._response(response)
        except HTTPError as response:
            return self._response(response)
        except (TimeoutError, socket.timeout) as exc:
            raise AccountingTimeout from exc
        except URLError as exc:
            if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                raise AccountingTimeout from exc
            raise

    @staticmethod
    def _response(response: HTTPResponse) -> AccountingResponse:
        raw_body = response.read()
        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            body = None
        document_id = body.get("document_id") if isinstance(body, dict) else None
        return AccountingResponse(response.status, document_id, body)
