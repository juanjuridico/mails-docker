import pytest
import sqlite3
import os
import tempfile
from db import init_db, add_email, get_emails, delete_email


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


class TestAddEmail:
    def test_add_email_success(self, temp_db):
        add_email("test@gmail.com", "tempmailg", "@gmail.com")
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM emails WHERE email = ?", ("test@gmail.com",))
        result = cursor.fetchone()
        conn.close()
        assert result is not None


class TestGetEmails:
    def test_get_emails_all(self, temp_db):
        add_email("test1@gmail.com", "tempmailg", "@gmail.com")
        add_email("test2@gmail.com", "tempmailg", "@gmail.com")
        emails = get_emails()
        assert len(emails) == 2


class TestDeleteEmail:
    def test_delete_email_success(self, temp_db):
        add_email("test@gmail.com", "tempmailg", "@gmail.com")
        result = delete_email("test@gmail.com")
        assert result is True
