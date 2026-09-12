"""Proveedor Mail.tm: buzones temporales gratuitos sin API key."""
import secrets
import string
import requests
from db import _db_path, get_email_by_email, add_email, mark_as_inactive
import sqlite3

BASE_URL = "https://api.mail.tm"
TIMEOUT = 20


def init_credentials_db():
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS mailbox_credentials (
            email TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            token TEXT NOT NULL,
            password TEXT NOT NULL
        )""")
        conn.commit()


def _password():
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return "".join(secrets.choice(alphabet) for _ in range(28))


def _domain():
    r = requests.get(f"{BASE_URL}/domains", timeout=TIMEOUT)
    r.raise_for_status()
    domains = r.json().get("hydra:member", [])
    active = [x["domain"] for x in domains if x.get("isActive")]
    if not active:
        raise RuntimeError("Mail.tm no tiene dominios disponibles")
    return secrets.choice(active)


def create_mailbox():
    init_credentials_db()
    for _ in range(5):
        email = f"m{secrets.token_hex(7)}@{_domain()}"
        password = _password()
        r = requests.post(f"{BASE_URL}/accounts", json={"address": email, "password": password}, timeout=TIMEOUT)
        if r.status_code == 201:
            account = r.json()
            t = requests.post(f"{BASE_URL}/token", json={"address": email, "password": password}, timeout=TIMEOUT)
            t.raise_for_status()
            token = t.json()["token"]
            with sqlite3.connect(_db_path()) as conn:
                conn.execute("INSERT INTO mailbox_credentials(email, account_id, token, password) VALUES (?,?,?,?)",
                             (email, account.get("id", ""), token, password))
                conn.commit()
            add_email(email, provider="mailtm", domain="@" + email.split("@", 1)[1])
            return email
        if r.status_code not in (400, 409):
            r.raise_for_status()
    raise RuntimeError("Mail.tm no pudo crear el buzón")


def _token(email):
    init_credentials_db()
    with sqlite3.connect(_db_path()) as conn:
        row = conn.execute("SELECT token FROM mailbox_credentials WHERE email=?", (email,)).fetchone()
    if not row:
        raise RuntimeError("No existe la sesión local del buzón")
    return row[0]


def messages(email):
    token = _token(email)
    r = requests.get(f"{BASE_URL}/messages", headers={"Authorization": f"Bearer {token}"}, timeout=TIMEOUT)
    if r.status_code == 401:
        raise RuntimeError("La sesión de Mail.tm expiró")
    r.raise_for_status()
    out=[]
    for m in r.json().get("hydra:member", []):
        out.append({
            "id": m.get("id"),
            "subject": m.get("subject", ""),
            "from": (m.get("from") or {}).get("address", ""),
            "from_email": (m.get("from") or {}).get("address", ""),
            "to": [(x or {}).get("address", "") for x in (m.get("to") or [])],
            "date": m.get("createdAt") or m.get("updatedAt"),
            "content": m.get("intro", ""),
            "html": "",
        })
    return out


def message(email, message_id):
    token = _token(email)
    r = requests.get(f"{BASE_URL}/messages/{message_id}", headers={"Authorization": f"Bearer {token}"}, timeout=TIMEOUT)
    r.raise_for_status()
    m=r.json()
    return {
        "id": m.get("id"), "subject": m.get("subject", ""),
        "from": (m.get("from") or {}).get("address", ""),
        "from_email": (m.get("from") or {}).get("address", ""),
        "date": m.get("createdAt"), "content": m.get("text", ""),
        "html": (m.get("html") or [""])[0] if isinstance(m.get("html"), list) else (m.get("html") or ""),
    }


def delete(email):
    init_credentials_db()
    try:
        with sqlite3.connect(_db_path()) as conn:
            row=conn.execute("SELECT account_id, token FROM mailbox_credentials WHERE email=?", (email,)).fetchone()
        if row:
            requests.delete(f"{BASE_URL}/accounts/{row[0]}", headers={"Authorization": f"Bearer {row[1]}"}, timeout=TIMEOUT)
            with sqlite3.connect(_db_path()) as conn:
                conn.execute("DELETE FROM mailbox_credentials WHERE email=?", (email,)); conn.commit()
    finally:
        return mark_as_inactive(email)


init_credentials_db()
