import pytest
from unittest.mock import patch
from email_service import EmailService


@pytest.fixture
def mock_email_service():
    return EmailService()


class TestGenerateEmail:
    @patch("email_service.generate_tempmailg_email")
    def test_generate_email_success(self, mock_generate, mock_email_service):
        mock_generate.return_value = "test@gmail.com"
        email = mock_email_service.generate_email(provider="tempmailg")
        assert email == "test@gmail.com"


class TestListEmails:
    @patch("email_service.get_emails_db")
    def test_list_emails_all(self, mock_get_emails_db, mock_email_service):
        mock_get_emails_db.return_value = [
            {"id": 1, "email": "test@gmail.com", "provider": "tempmailg", "domain": "@gmail.com", "created_at": "2026-09-10", "is_active": True}
        ]
        emails = mock_email_service.list_emails()
        assert len(emails) == 1
