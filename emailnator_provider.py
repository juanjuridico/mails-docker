"""Emailnator provider: disposable addresses ending in @gmail.com.

Uses Emailnator's own JSON endpoints directly; no browser, Selenium, API key,
or RapidAPI account is required for the public disposable-Gmail flow.
"""
import html as html_lib
import json
import re
import sqlite3
import subprocess
from html.parser import HTMLParser


from db import _db_path, add_email, mark_as_inactive

BASE_URL = "https://www.emailnator.com/api"
# Emailnator's current public email-type IDs: 2=plus Gmail, 3=dot Gmail.
GMAIL_TYPE_IDS = (3, 2)
TIMEOUT = 20


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript"}:
            self.skip += 1
        elif tag.lower() in {"br", "p", "div", "li", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "noscript"} and self.skip:
            self.skip -= 1
        elif tag.lower() in {"p", "div", "li", "tr", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def _text_from_html(value):
    if not value:
        return ""
    parser = _TextExtractor()
    try:
        parser.feed(value)
        text = html_lib.unescape("".join(parser.parts))
    except Exception:
        text = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+", " ", text)).strip()


def _init():
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS emailnator_mailboxes (
            email TEXT PRIMARY KEY,
            type_id INTEGER NOT NULL
        )""")
        conn.commit()


def _curl_json(method, url, payload=None):
    cmd = [
        "curl", "-4", "--fail-with-body", "--silent", "--show-error",
        "--connect-timeout", "8", "--max-time", str(TIMEOUT),
        "-H", "User-Agent: mails-docker/1.0",
        "-H", "Accept: application/json",
        "-X", method,
    ]
    if payload is not None:
        cmd += ["-H", "Content-Type: application/json", "--data", json.dumps(payload)]
    cmd.append(url)
    try:
        raw = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(exc.output.strip() or "Error HTTP de Emailnator") from exc
    return json.loads(raw)


def _post(path, payload):
    data = _curl_json("POST", f"{BASE_URL}{path}", payload)
    if data.get("status") != "success":
        raise RuntimeError(data.get("message") or "Emailnator devolvió un error")
    return data


def create_mailbox():
    _init()
    last = None
    for type_id in GMAIL_TYPE_IDS:
        try:
            data = _post("/generate-email", {"ids": [type_id]})
            email = data.get("email", "")
            if not email.lower().endswith("@gmail.com"):
                raise RuntimeError(f"Emailnator devolvió un dominio no Gmail: {email}")
            with sqlite3.connect(_db_path()) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO emailnator_mailboxes(email,type_id) VALUES (?,?)",
                    (email, type_id),
                )
                conn.commit()
            add_email(email, provider="emailnator", domain="@gmail.com")
            return email
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Emailnator no pudo crear un @gmail.com: {last}")


def _known(email):
    _init()
    with sqlite3.connect(_db_path()) as conn:
        row = conn.execute(
            "SELECT type_id FROM emailnator_mailboxes WHERE email=?", (email,)
        ).fetchone()
    if not row:
        raise RuntimeError("No existe la sesión local del buzón Emailnator")
    return row[0]


def _list(email):
    _known(email)
    return _post("/message-list", {"email": email, "limit": 20}).get("messages", [])


def _detail(message_id):
    from urllib.parse import quote
    return _curl_json("GET", f"{BASE_URL}/message/{quote(str(message_id), safe='')}")


def messages(email):
    out = []
    for item in _list(email):
        if not isinstance(item, dict):
            continue
        if item.get("locked"):
            out.append({
                "id": item.get("id"),
                "subject": item.get("subject", ""),
                "from": item.get("from", ""),
                "from_email": item.get("from", ""),
                "date": item.get("timestamp"),
                "content": "Contenido retenido por Emailnator (mensaje antiguo).",
                "html": "",
                "locked": True,
            })
            continue
        try:
            detail = _detail(item.get("id"))
        except Exception:
            detail = item
        content = detail.get("content") or detail.get("body") or ""
        out.append({
            "id": detail.get("id", item.get("id")),
            "subject": detail.get("subject", item.get("subject", "")),
            "from": detail.get("from", item.get("from", "")),
            "from_email": detail.get("from", item.get("from", "")),
            "date": detail.get("date", item.get("timestamp")),
            "content": _text_from_html(content),
            "html": "",
            "locked": False,
        })
    return out


def delete(email):
    _init()
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("DELETE FROM emailnator_mailboxes WHERE email=?", (email,))
        conn.commit()
    # Emailnator's public API does not expose an address-delete endpoint;
    # locally we stop tracking it so it disappears from this application's UI.
    return mark_as_inactive(email)


_init()
