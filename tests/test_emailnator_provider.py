import emailnator_provider as provider


def test_create_mailbox_requires_gmail(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "emails.db"))
    provider._init()
    calls = []

    def fake_post(path, payload):
        calls.append((path, payload))
        return {"status": "success", "email": "abc.def@gmail.com", "email_type_id": 3}

    monkeypatch.setattr(provider, "_post", fake_post)
    monkeypatch.setattr(provider, "add_email", lambda *args, **kwargs: None)
    assert provider.create_mailbox() == "abc.def@gmail.com"
    assert calls == [("/generate-email", {"ids": [3]})]


def test_messages_reads_list_and_detail(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "emails.db"))
    provider._init()
    import sqlite3
    with sqlite3.connect(str(tmp_path / "emails.db")) as conn:
        conn.execute("INSERT INTO emailnator_mailboxes VALUES (?, ?)", ("abc.def@gmail.com", 3))
        conn.commit()

    monkeypatch.setattr(provider, "_post", lambda *a, **k: {
        "status": "success",
        "messages": [{"id": "m1", "from": "Sender", "subject": "Hello", "timestamp": 1}],
    })
    monkeypatch.setattr(provider, "_detail", lambda mid: {
        "id": mid, "from": "Sender <sender@example.com>", "subject": "Hello",
        "date": 2, "content": "<p>Hi <b>Juan</b></p><script>x()</script>",
    })
    data = provider.messages("abc.def@gmail.com")
    assert data[0]["subject"] == "Hello"
    assert data[0]["preview"] == ""


def test_message_preserves_html(monkeypatch, tmp_path):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "emails.db"))
    provider._init()
    import sqlite3
    with sqlite3.connect(str(tmp_path / "emails.db")) as conn:
        conn.execute("INSERT INTO emailnator_mailboxes VALUES (?, ?)", ("abc.def@gmail.com", 3))
        conn.commit()
    monkeypatch.setattr(provider, "_detail", lambda mid: {
        "id": mid, "from": "Sender <sender@example.com>", "subject": "Hello",
        "date": 2, "content": "<p>Hi <b>Juan</b></p><a href=\"https://example.com\">Abrir</a>",
    })
    data = provider.message("abc.def@gmail.com", "m1")
    assert data["html"].startswith("<p>")
    assert "href=\"https://example.com\"" in data["html"]
    assert data["content"] == "Hi Juan\nAbrir"
