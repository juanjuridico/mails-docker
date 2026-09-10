import pytest
from unittest.mock import MagicMock, patch
from tempmailg_service import TempMailGService


@pytest.fixture
def mock_driver():
    return MagicMock()


@pytest.fixture
def mock_tempmailg_service(mock_driver):
    with patch("tempmailg_service.init_driver", return_value=mock_driver):
        with patch("tempmailg_service.close_driver"):
            service = TempMailGService(headless=True)
            service.driver = mock_driver
            yield service


class TestGenerateEmail:
    @patch("tempmailg_service.wait_for_element")
    @patch("tempmailg_service.add_email")
    def test_generate_email_success(self, mock_add_email, mock_wait, mock_tempmailg_service, mock_driver):
        mock_element = MagicMock()
        mock_element.text = "test@gmail.com"
        mock_wait.return_value = mock_element
        email = mock_tempmailg_service.generate_email()
        assert email == "test@gmail.com"


class TestGenerateEmails:
    @patch("tempmailg_service.TempMailGService.generate_email")
    def test_generate_emails_success(self, mock_generate, mock_tempmailg_service):
        mock_generate.side_effect = ["test1@gmail.com", "test2@gmail.com"]
        emails = mock_tempmailg_service.generate_emails(count=2)
        assert len(emails) == 2
