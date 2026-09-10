"""
selenium_utils.py - Utilidades para Selenium en mails-docker.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="selenium_utils.log",
)
logger = logging.getLogger(__name__)


class SeleniumUtils:
    @staticmethod
    def init_driver(headless: bool = True) -> webdriver.Chrome:
        """Inicializa el WebDriver de Chrome."""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("WebDriver inicializado.")
            return driver
        except Exception as e:
            logger.error(f"Error al inicializar WebDriver: {e}")
            raise WebDriverException(f"No se pudo inicializar el WebDriver: {e}")

    @staticmethod
    def close_driver(driver: webdriver.Chrome):
        """Cierra el WebDriver."""
        if driver:
            try:
                driver.quit()
                logger.info("WebDriver cerrado.")
            except Exception as e:
                logger.error(f"Error al cerrar WebDriver: {e}")

    @staticmethod
    def wait_for_element(driver: webdriver.Chrome, by: str, value: str, timeout: int = 10):
        """Espera a que un elemento esté presente."""
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logger.info(f"Elemento encontrado: {by}={value}")
            return element
        except TimeoutException as e:
            logger.error(f"Timeout al esperar elemento {by}={value}: {e}")
            raise TimeoutException(f"No se encontró el elemento {by}={value} en {timeout} segundos.")

    @staticmethod
    def take_screenshot(driver: webdriver.Chrome, path: str):
        """Toma una captura de pantalla."""
        try:
            driver.save_screenshot(path)
            logger.info(f"Captura guardada en: {path}")
        except Exception as e:
            logger.error(f"Error al tomar captura: {e}")

    @staticmethod
    def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Añade un retraso aleatorio."""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
        logger.info(f"Retraso aleatorio de {delay:.2f} segundos.")


# Funciones de conveniencia
def init_driver(headless: bool = True) -> webdriver.Chrome:
    return SeleniumUtils.init_driver(headless)

def close_driver(driver: webdriver.Chrome):
    SeleniumUtils.close_driver(driver)

def wait_for_element(driver: webdriver.Chrome, by: str, value: str, timeout: int = 10):
    return SeleniumUtils.wait_for_element(driver, by, value, timeout)

def take_screenshot(driver: webdriver.Chrome, path: str):
    SeleniumUtils.take_screenshot(driver, path)

def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
    SeleniumUtils.random_delay(min_seconds, max_seconds)
