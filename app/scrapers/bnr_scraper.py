from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

from app.core.config import BNR_URL, TIMEZONE, TIMESTAMP_FORMAT
from app.scrapers.driver import get_driver
from app.models.entity import Entity
from app.models.exchange_rate import ExchangeRate
from app.models.scraped_record import ScrapedRecord

SOURCE_NAME = "BNR"


def scrape_bnr():
    """Scrape exchange rates from cursbnr.ro (EUR only)."""
    driver = None
    try:
        driver = get_driver()
        driver.get(BNR_URL)

        wait_for_proper_loading(driver)

        rates = extract_exchange_rates(driver)

        return rates

    except Exception as e:
        print(f"[ERROR] BNR scraping failed: {e}")
        return []

    finally:
        if driver:
            driver.quit()


def extract_exchange_rates(driver):
    """Extract exchange rates in format: {source}, {name}, {city}, {currency}, {buy}, {sell}, {timestamp}"""
    rates = []
    exchange_rows = driver.find_elements(By.TAG_NAME, "tr")

    for row in exchange_rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 3:
                continue

            bank_name = cells[0].get_attribute("textContent").strip()
            buy_rate = cells[1].get_attribute("textContent").strip()
            sell_rate = cells[2].get_attribute("textContent").strip()

            if buy_rate and sell_rate and bank_name:
                rates.append(
                    ScrapedRecord(
                        entity=Entity(
                            platform_source=SOURCE_NAME,
                            name=bank_name,
                            city=None,
                            type="bank",
                        ),
                        rate=ExchangeRate(
                            currency="EUR",
                            buy=float(buy_rate.replace(",", ".")),
                            sell=float(sell_rate.replace(",", ".")),
                            timestamp=datetime.now(TIMEZONE).strftime(TIMESTAMP_FORMAT),
                        ),
                    )
                )
        except Exception:
            continue
    return rates


def wait_for_proper_loading(driver):
    """Wait for the table to load properly."""
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    time.sleep(2)


if __name__ == "__main__":
    data = scrape_bnr()
    for entry in data:
        print(entry)
