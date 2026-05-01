from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx

from psychohelp.config.config import config


class EmailDeliveryError(Exception):
    pass


@dataclass(frozen=True)
class EmailPayload:
    to: str
    subject: str
    text: str
    html: str
    sender_alias: str | None = None


class EmailProvider(Protocol):
    async def send(self, payload: EmailPayload) -> None:
        ...


def _mail_service_error_detail(logs: list[dict]) -> str:
    for entry in logs:
        error = entry.get("error")
        if error:
            step = entry.get("step_type", "unknown")
            error_type = error.get("type", "EmailDeliveryError")
            message = error.get("message", "")
            return f"{step}: {error_type}: {message}"
    return "mail service returned success=false"


class MailServiceHttpProvider:
    def __init__(self, base_url: str, from_user: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.from_user = from_user
        self.timeout_seconds = timeout_seconds

    async def send(self, payload: EmailPayload) -> None:
        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{self.base_url}/message",
                    params={"from": self.from_user, "to": payload.to},
                    json={
                        "title": payload.subject,
                        "content": payload.text,
                        "html_content": payload.html,
                        "sender_alias": payload.sender_alias,
                    },
                )
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise EmailDeliveryError("mail service request failed") from exc

        if not data.get("success"):
            raise EmailDeliveryError(
                _mail_service_error_detail(data.get("logs") or [])
            )


def get_email_provider() -> EmailProvider:
    return MailServiceHttpProvider(
        base_url=config.MAIL_SERVICE_URL,
        from_user=config.MAIL_SERVICE_FROM_USER,
        timeout_seconds=config.MAIL_REQUEST_TIMEOUT_SECONDS,
    )
