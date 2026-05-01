from hashlib import sha256
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
from fastapi import HTTPException

from psychohelp.routes.controllers import users as users_controller
from psychohelp.schemas.users import PasswordResetConfirmRequest, PasswordResetRequest
from psychohelp.services import email as email_service
from psychohelp.services.email import EmailDeliveryError, EmailPayload, MailServiceHttpProvider
from psychohelp.services.users import password_reset


@pytest.mark.asyncio
async def test_request_password_reset_sends_email_without_disclosing_user(monkeypatch):
    user_id = uuid4()
    created_token = {}
    sent_payloads = []

    async def fake_get_user_by_email(email):
        assert email == "user@example.com"
        return SimpleNamespace(id=user_id, email=email)

    async def fake_create_password_reset_token(user_id, token_hash, expires_at, now):
        created_token["user_id"] = user_id
        created_token["token_hash"] = token_hash
        created_token["expires_at"] = expires_at
        created_token["now"] = now

    class FakeEmailProvider:
        async def send(self, payload):
            sent_payloads.append(payload)

    monkeypatch.setattr(password_reset, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(
        password_reset.reset_tokens_repo,
        "create_password_reset_token",
        fake_create_password_reset_token,
    )
    monkeypatch.setattr(password_reset, "get_email_provider", lambda: FakeEmailProvider())
    monkeypatch.setattr(password_reset, "token_urlsafe", lambda length: "reset-token")
    monkeypatch.setattr(
        password_reset.config,
        "PASSWORD_RESET_URL_TEMPLATE",
        "https://example.com/reset?token={token}",
    )

    result = await password_reset.request_password_reset("user@example.com")

    assert result == password_reset.PASSWORD_RESET_REQUEST_MESSAGE
    assert created_token["user_id"] == user_id
    assert created_token["token_hash"] == sha256(b"reset-token").hexdigest()
    assert created_token["expires_at"] > created_token["now"]
    assert len(sent_payloads) == 1
    assert sent_payloads[0].to == "user@example.com"
    assert "https://example.com/reset?token=reset-token" in sent_payloads[0].text


@pytest.mark.asyncio
async def test_request_password_reset_for_unknown_email_does_not_send(monkeypatch):
    async def fake_get_user_by_email(_email):
        return None

    async def fake_create_password_reset_token(*_args, **_kwargs):
        raise AssertionError("token should not be created")

    class FakeEmailProvider:
        async def send(self, _payload):
            raise AssertionError("email should not be sent")

    monkeypatch.setattr(password_reset, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(
        password_reset.reset_tokens_repo,
        "create_password_reset_token",
        fake_create_password_reset_token,
    )
    monkeypatch.setattr(password_reset, "get_email_provider", lambda: FakeEmailProvider())

    result = await password_reset.request_password_reset("missing@example.com")

    assert result == password_reset.PASSWORD_RESET_REQUEST_MESSAGE


@pytest.mark.asyncio
async def test_request_password_reset_invalidates_token_when_email_fails(monkeypatch):
    user_id = uuid4()
    invalidated = {}

    async def fake_get_user_by_email(email):
        return SimpleNamespace(id=user_id, email=email)

    async def fake_create_password_reset_token(*_args, **_kwargs):
        return None

    async def fake_invalidate_password_reset_token(token_hash, now):
        invalidated["token_hash"] = token_hash
        invalidated["now"] = now

    class FailingEmailProvider:
        async def send(self, _payload):
            raise EmailDeliveryError("mail unavailable")

    monkeypatch.setattr(password_reset, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(
        password_reset.reset_tokens_repo,
        "create_password_reset_token",
        fake_create_password_reset_token,
    )
    monkeypatch.setattr(
        password_reset.reset_tokens_repo,
        "invalidate_password_reset_token",
        fake_invalidate_password_reset_token,
    )
    monkeypatch.setattr(password_reset, "get_email_provider", lambda: FailingEmailProvider())
    monkeypatch.setattr(password_reset, "token_urlsafe", lambda length: "reset-token")

    with pytest.raises(EmailDeliveryError):
        await password_reset.request_password_reset("user@example.com")

    assert invalidated["token_hash"] == sha256(b"reset-token").hexdigest()
    assert invalidated["now"] is not None


@pytest.mark.asyncio
async def test_reset_password_uses_token_hash_and_new_password(monkeypatch):
    captured = {}

    async def fake_use_password_reset_token(token_hash, hashed_password, now):
        captured["token_hash"] = token_hash
        captured["hashed_password"] = hashed_password
        captured["now"] = now
        return True

    monkeypatch.setattr(password_reset, "hash_password", lambda password: f"hashed-{password}")
    monkeypatch.setattr(
        password_reset.reset_tokens_repo,
        "use_password_reset_token",
        fake_use_password_reset_token,
    )

    await password_reset.reset_password("reset-token", "new-password")

    assert captured["token_hash"] == sha256(b"reset-token").hexdigest()
    assert captured["hashed_password"] == "hashed-new-password"
    assert captured["now"] is not None


@pytest.mark.asyncio
async def test_reset_password_rejects_invalid_token(monkeypatch):
    async def fake_use_password_reset_token(*_args, **_kwargs):
        return False

    monkeypatch.setattr(
        password_reset.reset_tokens_repo,
        "use_password_reset_token",
        fake_use_password_reset_token,
    )

    with pytest.raises(password_reset.InvalidPasswordResetToken):
        await password_reset.reset_password("bad-token", "new-password")


@pytest.mark.asyncio
async def test_mail_service_provider_posts_message(monkeypatch):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json={"success": True, "logs": []})

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        email_service.httpx,
        "AsyncClient",
        lambda timeout: original_client(transport=transport, timeout=timeout),
    )

    provider = MailServiceHttpProvider(
        base_url="https://mail.example.com/",
        from_user="root",
        timeout_seconds=3,
    )
    await provider.send(
        EmailPayload(
            to="user@example.com",
            subject="Subject",
            text="Text",
            html="<p>Text</p>",
            sender_alias="Alias",
        )
    )

    assert len(requests) == 1
    request = requests[0]
    assert request.url.path == "/message"
    assert request.url.params["from"] == "root"
    assert request.url.params["to"] == "user@example.com"
    assert request.content


@pytest.mark.asyncio
async def test_mail_service_provider_raises_on_unsuccessful_response(monkeypatch):
    def handler(_request):
        return httpx.Response(
            200,
            json={
                "success": False,
                "logs": [
                    {
                        "step_type": "DNS_LOOKUP",
                        "domain": "example.com",
                        "error": {"type": "RuntimeError", "message": "failed"},
                    }
                ],
            },
        )

    transport = httpx.MockTransport(handler)
    original_client = httpx.AsyncClient
    monkeypatch.setattr(
        email_service.httpx,
        "AsyncClient",
        lambda timeout: original_client(transport=transport, timeout=timeout),
    )

    provider = MailServiceHttpProvider(
        base_url="https://mail.example.com",
        from_user="root",
        timeout_seconds=3,
    )

    with pytest.raises(EmailDeliveryError) as exc:
        await provider.send(
            EmailPayload(
                to="user@example.com",
                subject="Subject",
                text="Text",
                html="<p>Text</p>",
            )
        )

    assert "DNS_LOOKUP" in str(exc.value)


@pytest.mark.asyncio
async def test_password_reset_request_endpoint_returns_message(monkeypatch):
    async def fake_request_password_reset(email):
        assert email == "user@example.com"
        return "sent"

    monkeypatch.setattr(users_controller.limiter, "enabled", False)
    monkeypatch.setattr(
        users_controller,
        "request_password_reset",
        fake_request_password_reset,
    )

    result = await users_controller.request_password_reset_email(
        SimpleNamespace(),
        PasswordResetRequest(email="user@example.com"),
    )

    assert result == {"message": "sent"}


@pytest.mark.asyncio
async def test_password_reset_confirm_endpoint_maps_invalid_token(monkeypatch):
    async def fake_reset_password(_token, _new_password):
        raise password_reset.InvalidPasswordResetToken()

    monkeypatch.setattr(users_controller.limiter, "enabled", False)
    monkeypatch.setattr(users_controller, "reset_password", fake_reset_password)

    with pytest.raises(HTTPException) as exc:
        await users_controller.confirm_password_reset(
            SimpleNamespace(),
            PasswordResetConfirmRequest(token="bad-token", new_password="new-password"),
        )

    assert exc.value.status_code == 400
