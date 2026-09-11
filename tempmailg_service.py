"""Servicio TempMailG: API oficial primero, Selenium como fallback opcional."""

import logging
import os
from typing import Optional

from db import add_email, delete_email as delete_email_db, get_emails as get_emails_db, update_email_expiry
from tempmailg_api import TempMailGAPI, TempMailGAPIError

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
        # API oficial: no depende del desafío Cloudflare de la web pública.
        if self.api.configured:
            data = self.api.create_email()
            email = data.get("email")
            if not email:
                raise TempMailGAPIError("La API no devolvió un correo")
            add_email(email, provider="tempmailg-api", domain=f"@{data.get('domain', email.rsplit('@', 1)[-1])}")
            if data.get("expire_at"):
                update_email_expiry(email, data["expire_at"])
            return email

        # Mantener fallback Selenium para instalaciones que dispongan de una
        # sesión/navegación autorizada. No intentamos resolver/burlar Turnstile.
        if os.getenv("ENABLE_SELENIUM_FALLBACK", "False").lower() != "true":
            raise TempMailGAPIError(
                "TempMailG API no configurada. Configure TEMPMAILG_API_KEY; "
                "la web pública está protegida por Cloudflare Turnstile."
            )

        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import TimeoutException, NoSuchElementException
        from selenium_utils import init_driver, wait_for_element, random_delay

        if not self.driver:
            self.driver = init_driver(headless=self.headless)
        url = os.getenv("TEMPMAILG_URL", "https://tempmailg.com/es")
        for attempt in range(max_retries):
            try:
                self.driver.get(url)
                random_delay()
                element = wait_for_element(self.driver, By.XPATH, "//*[@id='email']", timeout=15)
                email = element.text.strip()
                if email:
                    add_email(email, provider="tempmailg-web", domain=f"@{email.rsplit('@', 1)[-1]}")
                    return email
            except (TimeoutException, NoSuchElementException) as exc:
                logger.warning("Selenium TempMailG intento %s/%s: %s", attempt + 1, max_retries, exc)
                if attempt < max_retries - 1:
                    self.driver.refresh()
                    random_delay(1, 3)
        return None

    def generate_emails(self, count: int = 1, max_retries: int = 3) -> list:
        return [email for _ in range(count) if (email := self.generate_email(max_retries))]

    def get_emails(self, email: str) -> list:
        if self.api.configured:
            return self.api.messages(email)
        if os.getenv("ENABLE_SELENIUM_FALLBACK", "False").lower() != "true":
            raise TempMailGAPIError("Configure TEMPMAILG_API_KEY para leer la bandeja")
        return []

    def delete_email(self, email: str) -> bool:
        if self.api.configured:
            self.api.delete_email(email)
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
