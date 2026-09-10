"""
db.py - Módulo de base de datos SQLite para mails-docker.
"""

import sqlite3
import os
from typing import List, Dict, Optional

# Configuración
DB_PATH = os.getenv("DB_PATH", "/app/data/emails.db")

# Asegurar que el directorio de la base de datos exista
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    """Inicializa la base de datos y crea las tablas."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE,
                provider TEXT NOT NULL,
                domain TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        conn.commit()


def add_email(email: str, provider: str, domain: str):
    """Añade un correo a la base de datos."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO emails (email, provider, domain) VALUES (?, ?, ?)", (email, provider, domain))
        conn.commit()


def get_emails(provider: Optional[str] = None, is_active: bool = True) -> List[Dict]:
    """Obtiene una lista de correos."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if provider:
            cursor.execute("""
                SELECT id, email, provider, domain, created_at, is_active
                FROM emails WHERE provider = ? AND is_active = ?
            """, (provider, int(is_active)))
        else:
            cursor.execute("""
                SELECT id, email, provider, domain, created_at, is_active
                FROM emails WHERE is_active = ?
            """, (int(is_active),))
        
        emails = []
        for row in cursor.fetchall():
            emails.append({
                "id": row[0],
                "email": row[1],
                "provider": row[2],
                "domain": row[3],
                "created_at": row[4],
                "is_active": bool(row[5])
            })
        return emails


def get_email_by_email(email: str) -> Optional[Dict]:
    """Obtiene un correo específico."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, provider, domain, created_at, is_active FROM emails WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "email": row[1],
                "provider": row[2],
                "domain": row[3],
                "created_at": row[4],
                "is_active": bool(row[5])
            }
        return None


def delete_email(email: str) -> bool:
    """Elimina un correo de la base de datos."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM emails WHERE email = ?", (email,))
        conn.commit()
        return cursor.rowcount > 0


def mark_as_inactive(email: str) -> bool:
    """Marca un correo como inactivo."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE emails SET is_active = 0 WHERE email = ?", (email,))
        conn.commit()
        return cursor.rowcount > 0


def update_email_expiry(email: str, expires_at: str) -> bool:
    """Actualiza la fecha de expiración de un correo."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE emails SET expires_at = ? WHERE email = ?", (expires_at, email))
        conn.commit()
        return cursor.rowcount > 0


# Inicializar la base de datos al importar el módulo
init_db()
