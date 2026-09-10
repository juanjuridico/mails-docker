"""
tempmailg_service.py - Servicio para TempMailG usando Selenium.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium_utils import init_driver, close_driver, wait_for_element, random_delay, take_screenshot
from db import add_email, delete_email as delete_email_db
import logging
import os

# Configuración
TEMPMAILG_URL = os.getenv("TEMPMAILG_URL", "https://tempmailg.com/es")
SCREENSHOT_DIR = "screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="tempmailg_service.log",
)
logger = logging.getLogger(__name__)


class TempMailGService:
    """Servicio para interactuar con TempMailG."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def __enter__(self):
        self.driver = init_driver(headless=self.headless)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            close_driver(self.driver)

    def generate_email(self, max_retries: int = 3) -> str:
        """Genera un correo temporal en TempMailG."""
        if not self.driver:
            self.driver = init_driver(headless=self.headless)

        for attempt in range(max_retries):
            try:
                self.driver.get(TEMPMAILG_URL)
                random_delay()

                email_element = wait_for_element(
                    self.driver,
                    By.XPATH,
                    "//*[@id='email']",
                    timeout=15
                )
                email = email_element.text.strip()

                if not email.endswith("@gmail.com"):
                    logger.warning(f"Intento {attempt + 1}: Correo inválido: {email}")
                    take_screenshot(self.driver, f"{SCREENSHOT_DIR}/invalid_email_attempt_{attempt + 1}.png")
                    if attempt < max_retries - 1:
                        self.driver.refresh()
                        random_delay(1, 3)
                        continue
                    else:
                        raise ValueError(f"El correo {email} no termina en @gmail.com")

                add_email(email, provider="tempmailg", domain="@gmail.com")
                logger.info(f"Correo generado: {email}")
                return email

            except (TimeoutException, NoSuchElementException) as e:
                logger.error(f"Intento {attempt + 1}: Error - {e}")
                take_screenshot(self.driver, f"{SCREENSHOT_DIR}/error_attempt_{attempt + 1}.png")
                if attempt < max_retries - 1:
                    self.driver.refresh()
                    random_delay(1, 3)
                else:
                    return None

        return None

    def generate_emails(self, count: int = 1, max_retries: int = 3) -> list:
        """Genera múltiples correos."""
        emails = []
        for _ in range(count):
            email = self.generate_email(max_retries)
            if email:
                emails.append(email)
        return emails

    def get_emails(self, email: str) -> list:
        """Obtiene los correos recibidos."""
        if not self.driver:
            self.driver = init_driver(headless=self.headless)

        try:
            inbox_url = f"{TEMPMAILG_URL}/inbox/{email}"
            self.driver.get(inbox_url)
            random_delay()

            wait_for_element(self.driver, By.XPATH, "//*[@class='message']", timeout=15)
            messages = self.driver.find_elements(By.XPATH, "//*[@class='message']")

            emails_list = []
            for message in messages:
                try:
                    sender = message.find_element(By.XPATH, ".//*[@class='sender']").text.strip()
                    subject = message.find_element(By.XPATH, ".//*[@class='subject']").text.strip()
                    body = message.find_element(By.XPATH, ".//*[@class='body']").text.strip()
                    date = message.find_element(By.XPATH, ".//*[@class='date']").text.strip()
                    emails_list.append({"from": sender, "subject": subject, "body": body, "date": date})
                except NoSuchElementException:
                    continue

            logger.info(f"Se encontraron {len(emails_list)} correos para {email}")
            return emails_list

        except TimeoutException as e:
            logger.error(f"Timeout al cargar bandeja de {email}: {e}")
            take_screenshot(self.driver, f"{SCREENSHOT_DIR}/inbox_timeout_{email}.png")
            return []
        except Exception as e:
            logger.error(f"Error al obtener correos: {e}")
            take_screenshot(self.driver, f"{SCREENSHOT_DIR}/inbox_error_{email}.png")
            return []

    def delete_email(self, email: str) -> bool:
        """Elimina un correo de la base de datos."""
        try:
            delete_email_db(email)
            logger.info(f"Correo {email} eliminado de la base de datos.")
            return True
        except Exception as e:
            logger.error(f"Error al eliminar correo {email}: {e}")
            return False

    def sync_emails(self):
        """Sincroniza correos."""
        emails = get_emails_db(provider="tempmailg")
        for email in emails:
            inbox_emails = self.get_emails(email["email"])
            logger.info(f"Sincronizados {len(inbox_emails)} correos para {email['email']}")


# Funciones de conveniencia
def generate_email(headless: bool = True, max_retries: int = 3) -> str:
    with TempMailGService(headless) as service:
        return service.generate_email(max_retries)

def generate_emails(count: int = 1, headless: bool = True, max_retries: int = 3) -> list:
    with TempMailGService(headless) as service:
        return service.generate_emails(count, max_retries)

def get_emails(email: str, headless: bool = True) -> list:
    with TempMailGService(headless) as service:
        return service.get_emails(email)

def delete_email(email: str) -> bool:
    with TempMailGService() as service:
        return service.delete_email(email)

def sync_emails(headless: bool = True):
    with TempMailGService(headless) as service:
        service.sync_emails()
