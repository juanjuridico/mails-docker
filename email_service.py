"""
email_service.py - Servicio principal de correos para mails-docker.
"""

from tempmailg_service import generate_email as generate_tempmailg_email, \
    generate_emails as generate_tempmailg_emails, \
    get_emails as get_tempmailg_emails, \
    delete_email as delete_tempmailg_email, \
    sync_emails as sync_tempmailg_emails
from db import get_emails as get_emails_db, mark_as_inactive
from typing import List, Dict, Optional


class EmailService:
    """Servicio principal para manejar correos temporales."""

    def __init__(self):
        self.providers = {
            "tempmailg": {
                "generate": generate_tempmailg_email,
                "generate_emails": generate_tempmailg_emails,
                "get_emails": get_tempmailg_emails,
                "delete": delete_tempmailg_email,
                "sync": sync_tempmailg_emails,
            },
        }

    def generate_email(self, provider: str = "tempmailg", **kwargs) -> Optional[str]:
        """Genera un correo temporal."""
        if provider not in self.providers:
            return None
        try:
            generate_func = self.providers[provider]["generate"]
            return generate_func(**kwargs)
        except Exception:
            return None

    def generate_emails(self, count: int = 1, provider: str = "tempmailg", **kwargs) -> List[str]:
        """Genera múltiples correos temporales."""
        if provider not in self.providers:
            return []
        try:
            generate_emails_func = self.providers[provider]["generate_emails"]
            return generate_emails_func(count=count, **kwargs)
        except Exception:
            return []

    def get_emails(self, email: str, provider: str = "tempmailg", **kwargs) -> List[Dict]:
        """Obtiene los correos recibidos."""
        if provider not in self.providers:
            return []
        try:
            get_emails_func = self.providers[provider]["get_emails"]
            return get_emails_func(email, **kwargs)
        except Exception:
            return []

    def delete_email(self, email: str, provider: str = "tempmailg", **kwargs) -> bool:
        """Elimina un correo."""
        if provider not in self.providers:
            return False
        try:
            delete_func = self.providers[provider]["delete"]
            return delete_func(email, **kwargs)
        except Exception:
            return False

    def sync_emails(self, provider: str = "tempmailg", **kwargs):
        """Sincroniza correos."""
        if provider not in self.providers:
            return
        try:
            sync_func = self.providers[provider]["sync"]
            sync_func(**kwargs)
        except Exception:
            pass

    def list_emails(self, provider: Optional[str] = None, is_active: bool = True) -> List[Dict]:
        """Lista correos almacenados."""
        return get_emails_db(provider=provider, is_active=is_active)

    def deactivate_email(self, email: str) -> bool:
        """Marca un correo como inactivo."""
        return mark_as_inactive(email)


# Instancia global
email_service = EmailService()


# Funciones de conveniencia
def generate_email(provider: str = "tempmailg", **kwargs) -> Optional[str]:
    return email_service.generate_email(provider, **kwargs)

def generate_emails(count: int = 1, provider: str = "tempmailg", **kwargs) -> List[str]:
    return email_service.generate_emails(count, provider, **kwargs)

def get_emails(email: str, provider: str = "tempmailg", **kwargs) -> List[Dict]:
    return email_service.get_emails(email, provider, **kwargs)

def delete_email(email: str, provider: str = "tempmailg", **kwargs) -> bool:
    return email_service.delete_email(email, provider, **kwargs)

def sync_emails(provider: str = "tempmailg", **kwargs):
    email_service.sync_emails(provider, **kwargs)

def list_emails(provider: Optional[str] = None, is_active: bool = True) -> List[Dict]:
    return email_service.list_emails(provider, is_active)

def deactivate_email(email: str) -> bool:
    return email_service.deactivate_email(email)
