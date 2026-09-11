from unittest.mock import patch

from email_service import EmailService


def test_generate_email_success():
    service = EmailService()
    with patch("email_service.generate_tempmailg_email", return_value="test@gmail.com"):
        assert service.generate_email(provider="tempmailg") == "test@gmail.com"


def test_list_emails_all():
    service = EmailService()
    with patch("email_service.get_emails_db", return_value=[
        {"id": 1, "email": "test@gmail.com", "provider": "tempmailg", "domain": "@gmail.com", "created_at": "2026-09-10", "is_active": True}
    ]):
        assert len(service.list_emails()) == 1
