from unittest.mock import MagicMock, patch

from tempmailg_service import TempMailGService


def test_generate_email_via_official_api():
    service = TempMailGService()
    service.api.api_key = "test-key"
    service.api.create_email = MagicMock(return_value={
        "email": "test@example.com",
        "domain": "example.com",
        "expire_at": "2026-09-11T23:59:00Z",
    })
    with patch("tempmailg_service.add_email") as add_email, patch("tempmailg_service.update_email_expiry"):
        assert service.generate_email() == "test@example.com"
        add_email.assert_called_once_with(
            "test@example.com", provider="tempmailg-api", domain="@example.com"
        )


def test_generate_emails_success():
    service = TempMailGService()
    with patch.object(service, "generate_email", side_effect=["a@example.com", "b@example.com"]):
        assert service.generate_emails(count=2) == ["a@example.com", "b@example.com"]
