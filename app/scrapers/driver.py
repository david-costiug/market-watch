from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from app.core.config import CHROME_OPTIONS, USER_AGENT


def get_driver():
    """Create a headless Chrome driver."""
    options = Options()
    for opt in CHROME_OPTIONS:
        options.add_argument(opt)
    options.add_argument(f"user-agent={USER_AGENT}")
    return webdriver.Chrome(options=options)
