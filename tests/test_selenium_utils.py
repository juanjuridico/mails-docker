import pytest
from unittest.mock import MagicMock, patch
from selenium_utils import SeleniumUtils, init_driver, close_driver


@pytest.fixture
def mock_driver():
    return MagicMock()


class TestInitDriver:
    @patch("selenium_utils.webdriver.Chrome")
    @patch("selenium_utils.ChromeDriverManager")
    def test_init_driver_success(self, mock_chrome_driver, mock_chrome):
        mock_driver = MagicMock()
        mock_chrome.return_value = mock_driver
        mock_chrome_driver.return_value.install.return_value = "/path/to/chromedriver"
        driver = SeleniumUtils.init_driver(headless=True)
        assert driver is not None


class TestCloseDriver:
    def test_close_driver_success(self, mock_driver):
        SeleniumUtils.close_driver(mock_driver)
        mock_driver.quit.assert_called_once()
