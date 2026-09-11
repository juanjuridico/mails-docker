"""Selenium utilities for mails-docker."""

import logging
import os
import random
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filename="selenium_utils.log",
)
logger = logging.getLogger(__name__)


class SeleniumUtils:
    @staticmethod
    def init_driver(headless: bool = True) -> webdriver.Chrome:
        """Inicializa Chromium/Chrome de forma reproducible en Docker y local."""
        try:
            options = Options()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            )

            browser_binary = os.getenv("CHROME_BINARY")
            if browser_binary:
                options.binary_location = browser_binary

            proxy_url = os.getenv("PROXY", "").strip()
            if proxy_url and proxy_url != "http://proxy_ip:port":
                options.add_argument(f"--proxy-server={proxy_url}")
                logger.info("Proxy configurado")

            driver_path = os.getenv("CHROME_DRIVER_PATH", "").strip()
            if driver_path and os.path.exists(driver_path):
                service = Service(driver_path)
            else:
                # Local development fallback; Docker uses the distro driver above.
                service = Service(ChromeDriverManager().install())

            driver = webdriver.Chrome(service=service, options=options)
            logger.info("WebDriver inicializado.")
            return driver
        except Exception as exc:
            logger.exception("Error al inicializar WebDriver")
            raise WebDriverException(f"No se pudo inicializar el WebDriver: {exc}") from exc

    @staticmethod
    def close_driver(driver: webdriver.Chrome):
        if driver:
            try:
                driver.quit()
            except Exception:
                logger.exception("Error al cerrar WebDriver")

    @staticmethod
    def wait_for_element(driver: webdriver.Chrome, by: str, value: str, timeout: int = 10):
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException as exc:
            raise TimeoutException(
                f"No se encontró el elemento {by}={value} en {timeout} segundos."
            ) from exc

    @staticmethod
    def take_screenshot(driver: webdriver.Chrome, path: str):
        try:
            driver.save_screenshot(path)
        except Exception:
            logger.exception("Error al tomar captura")

    @staticmethod
    def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
        time.sleep(random.uniform(min_seconds, max_seconds))


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
