"""Servicio TempMailG: API oficial primero, Selenium como fallback opcional."""

import logging
import os
from typing import Optional

from db import add_email, delete_email as delete_email_db, get_emails as get_emails_db, update_email_expiry
from tempmailg_api import TempMailGAPI, TempMailGAPIError
from browser_agent import run as run_browser_agent, extract_email, BrowserAgentError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TempMailGService:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.api = TempMailGAPI()
        self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.driver:
            try:
                from selenium_utils import close_driver
                close_driver(self.driver)
            finally:
                self.driver = None

    def generate_email(self, max_retries: int = 3) -> Optional[str]:
        if self.api.configured:
            data = self.api.create_email()
            email = data.get("email")
            if not email:
                raise TempMailGAPIError("La API no devolvió un correo")
            add_email(email, provider="tempmailg-api", domain=f"@{data.get('domain', email.rsplit('@', 1)[-1])}")
            if data.get("expire_at"):
                update_email_expiry(email, data["expire_at"])
            return email

        if os.getenv("ENABLE_BROWSER_AGENT", "True").lower() == "true":
            task=os.getenv("TEMPMAILG_BROWSER_CREATE_TASK", "Abre https://tempmailg.com/es y genera u obtén un correo temporal. Observa la pantalla antes de cada acción. Si la página muestra una verificación de seguridad que no se completa, detente e informa el bloqueo. Si consigues un correo, termina indicando la dirección completa. No inventes una dirección.")
            try:
                result=run_browser_agent(task,max_steps=max_retries*4)
                email=extract_email(result)
                if email:
                    add_email(email,provider="tempmailg-browser",domain=f"@{email.rsplit('@',1)[-1]}")
                    return email
                raise TempMailGAPIError(result.get("message") or result.get("status") or "browser-agent no obtuvo una dirección")
            except BrowserAgentError as exc:
                raise TempMailGAPIError(str(exc)) from exc

        raise TempMailGAPIError("TempMailG API no configurada y browser-agent deshabilitado")

    def generate_emails(self, count: int = 1, max_retries: int = 3) -> list:
        return [email for _ in range(count) if (email := self.generate_email(max_retries))]

    def get_emails(self, email: str) -> list:
        if self.api.configured:
            return self.api.messages(email)
        if os.getenv("ENABLE_BROWSER_AGENT", "True").lower() == "true":
            result=run_browser_agent(f"Revisa la bandeja del correo {email} usando el Chromium persistente de TempMailG. No inventes mensajes. Lee por OCR lo que esté visible y devuelve remitente, asunto, fecha y contenido confirmado. Si aparece una verificación de seguridad que no se completa, informa el bloqueo.",max_steps=10)
            return [{"type":"browser-agent","email":email,"agent":result}]
        raise TempMailGAPIError("Configure TEMPMAILG_API_KEY o ENABLE_BROWSER_AGENT")

    def delete_email(self, email: str) -> bool:
        if self.api.configured:
            self.api.delete_email(email)
        elif os.getenv("ENABLE_BROWSER_AGENT", "True").lower() == "true":
            run_browser_agent(f"En el navegador TempMailG elimina o cierra el buzón {email} si la interfaz lo permite. Confirma visualmente la acción y no inventes éxito.",max_steps=8)
        return delete_email_db(email)

    def sync_emails(self):
        for row in get_emails_db(provider="tempmailg-api"):
            try:
                self.get_emails(row["email"])
            except Exception as exc:
                logger.warning("No se pudo sincronizar %s: %s", row["email"], exc)


def generate_email(headless: bool = True, max_retries: int = 3):
    with TempMailGService(headless) as service:
        return service.generate_email(max_retries)


def generate_emails(count: int = 1, headless: bool = True, max_retries: int = 3):
    with TempMailGService(headless) as service:
        return service.generate_emails(count, max_retries)


def get_emails(email: str, headless: bool = True):
    with TempMailGService(headless) as service:
        return service.get_emails(email)


def delete_email(email: str) -> bool:
    with TempMailGService() as service:
        return service.delete_email(email)


def sync_emails(headless: bool = True):
    with TempMailGService(headless) as service:
        service.sync_emails()
