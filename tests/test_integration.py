import pytest
from tempmailg_service import TempMailGService
from db import add_email, get_emails, init_db
import os
import tempfile


@pytest.fixture
def temp_db():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    original_db_path = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = db_path
    init_db()
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)
    if original_db_path:
        os.environ["DB_PATH"] = original_db_path


class TestDbIntegration:
    def test_add_and_list_emails(self, temp_db):
        add_email("test@gmail.com", "tempmailg", "@gmail.com")
        emails = get_emails()
        assert len(emails) == 1
