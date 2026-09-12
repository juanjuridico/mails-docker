"""Proveedores gratuitos de correo temporal sin API key.

Usa TempMailPortal como primera opción y smails.dev como respaldo. Ambos
entregan un token por buzón, por lo que no hay credenciales globales.
"""
import secrets
import sqlite3
import requests
from db import _db_path, add_email, mark_as_inactive

PROVIDERS = [
    {
        "name": "tempmailportal",
        "create": "https://api.tempmailportal.com/api/inbox",
        "messages": "https://api.tempmailportal.com/api/messages",
    },
    {
        "name": "smails",
        "create": "https://smails.dev/api/mailbox",
        "messages": "https://smails.dev/api/mailbox/messages",
    },
]
TIMEOUT = 20


def _init():
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS free_mailboxes (
            email TEXT PRIMARY KEY,
            provider TEXT NOT NULL,
            token TEXT NOT NULL
        )""")
        conn.commit()


def create_mailbox():
    _init()
    last=None
    for p in PROVIDERS:
        try:
            r=requests.post(p["create"],timeout=TIMEOUT)
            r.raise_for_status()
            data=r.json(); email=data["address"]; token=data["token"]
            with sqlite3.connect(_db_path()) as conn:
                conn.execute("INSERT OR REPLACE INTO free_mailboxes(email,provider,token) VALUES (?,?,?)",
                             (email,p["name"],token)); conn.commit()
            add_email(email, provider=p["name"], domain="@"+email.split("@",1)[1])
            return email
        except Exception as exc:
            last=exc
    raise RuntimeError(f"No hay proveedor gratuito disponible: {last}")


def _get(email):
    _init()
    with sqlite3.connect(_db_path()) as conn:
        row=conn.execute("SELECT provider,token FROM free_mailboxes WHERE email=?",(email,)).fetchone()
    if not row: raise RuntimeError("No existe la sesión local del buzón")
    return row


def messages(email):
    provider,token=_get(email)
    p=next(x for x in PROVIDERS if x["name"]==provider)
    r=requests.get(p["messages"],headers={"Authorization":f"Bearer {token}"},timeout=TIMEOUT)
    r.raise_for_status(); data=r.json()
    items=(data.get("messages", []) if isinstance(data, dict) else data)
    out=[]
    for m in items:
        if not isinstance(m, dict):
            continue
        out.append({
            "id":m.get("id"), "subject":m.get("subject", ""),
            "from":m.get("from", ""), "from_email":m.get("from", ""),
            "date":m.get("date") or m.get("received_at"),
            "content":m.get("text") or m.get("body") or m.get("intro") or "",
            "html":m.get("html") or "",
        })
    return out


def delete(email):
    _init()
    with sqlite3.connect(_db_path()) as conn:
        conn.execute("DELETE FROM free_mailboxes WHERE email=?",(email,)); conn.commit()
    return mark_as_inactive(email)


_init()
