from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

from app.core.config import VALUTARE_URL, TIMEZONE, TIMESTAMP_FORMAT
from app.scrapers.driver import get_driver
from app.models.entity import Entity
from app.models.exchange_rate import ExchangeRate
from app.models.scraped_record import ScrapedRecord

SOURCE_NAME = "Valutare"


def scrape_valutare():
    """Scrape exchange rates from valutare.ro (EUR only)."""
    driver = None
    try:
        driver = get_driver()
        driver.get(VALUTARE_URL)

        wait_for_proper_loading(driver)

        handle_lazy_loading(driver)

        rates = extract_exchange_rates(driver)

        return rates

    except Exception as e:
        print(f"[ERROR] Valutare scraping failed: {e}")
        return []

    finally:
        if driver:
            driver.quit()


def extract_exchange_rates(driver):
    """Extract exchange rates in format: {source}, {exchange-name}, {city}, {currency}, {buy}, {sell}, {timestamp}"""
    rates = []
    exchange_rows = driver.find_elements(By.CLASS_NAME, "exchange-row")

    for row in exchange_rows:
        try:
            # Get exchange name
            name_element = row.find_element(By.CLASS_NAME, "exchange-name-txt")
            exchange_name = name_element.get_attribute("textContent").strip()

            # Get exchange city
            city_element = row.find_element(By.CLASS_NAME, "oras")
            city_name = city_element.get_attribute("textContent").strip()

            # Get buy rate
            buy_element = row.find_element(By.CLASS_NAME, "buy-rate")
            buy_text = buy_element.get_attribute("textContent").strip()
            buy_rate = buy_text.split()[0] if buy_text else ""

            # Get sell rate (what they charge to sell EUR to you)
            sell_element = row.find_element(By.CLASS_NAME, "sell-rate")
            sell_text = sell_element.get_attribute("textContent").strip()
            sell_rate = sell_text.split()[0] if sell_text else ""

            if buy_rate and sell_rate:
                rates.append(
                    ScrapedRecord(
                        entity=Entity(
                            platform_source=SOURCE_NAME,
                            name=exchange_name,
                            city=city_name,
                            type="exchange_office",
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


def handle_lazy_loading(driver):
    """Handle lazy loading by scrolling down until no new rows are loaded."""
    max_scroll_attempts = 10
    scroll_attempts = 0

    while scroll_attempts < max_scroll_attempts:
        current_rows = driver.find_elements(By.CLASS_NAME, "exchange-row")
        current_count = len(current_rows)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        new_rows = driver.find_elements(By.CLASS_NAME, "exchange-row")
        if len(new_rows) == current_count and current_count > 0:
            break

        scroll_attempts += 1


def wait_for_proper_loading(driver):
    """Wait for the table to load properly."""
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "exchangegrid"))
    )

    time.sleep(2)


if __name__ == "__main__":
    data = scrape_valutare()
    for entry in data:
        print(entry)
