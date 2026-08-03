from datetime import datetime
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.core.config import VALUTARE_URL, TIMEZONE, TIMESTAMP_FORMAT
from app.scrapers.driver import get_driver
from app.models.entity import Entity
from app.models.exchange_rate import ExchangeRate
from app.models.scraped_record import ScrapedRecord

SOURCE_NAME = "Valutare"


def scrape_valutare() -> list[ScrapedRecord]:
    """Scrape exchange rates from valutare.ro (EUR, USD, GBP)."""
    driver = None
    all_rates = []
    currencies = ["EUR", "USD", "GBP"]
    try:
        driver = get_driver()
        for currency in currencies:
            html = fetch_page_source(driver, currency)
            rates = parse_html(html, currency)
            all_rates.extend(rates)

        return all_rates

    except Exception as e:
        print(f"[ERROR] Valutare scraping failed: {e}")
        return all_rates

    finally:
        if driver:
            driver.quit()


def fetch_page_source(driver, currency: str) -> str:
    """Fetch page source HTML after lazy loading."""
    url = VALUTARE_URL.format(currency.lower())
    driver.get(url)
    wait_for_proper_loading(driver)
    handle_lazy_loading(driver)
    return driver.page_source


def parse_html(html: str, currency: str) -> list[ScrapedRecord]:
    """Extract exchange rates from HTML using BeautifulSoup."""
    rates = []
    soup = BeautifulSoup(html, "html.parser")
    exchange_rows = soup.select(".exchange-row")

    for row in exchange_rows:
        try:
            # Get exchange name
            name_el = row.select_one(".exchange-name-txt")
            exchange_name = name_el.get_text(strip=True) if name_el else ""

            # Get exchange city
            city_el = row.select_one(".oras")
            city_name = city_el.get_text(strip=True) if city_el else ""

            # Get buy rate
            buy_el = row.select_one(".buy-rate")
            buy_text = buy_el.get_text(strip=True) if buy_el else ""
            buy_rate = buy_text.split()[0] if buy_text else ""

            # Get sell rate
            sell_el = row.select_one(".sell-rate")
            sell_text = sell_el.get_text(strip=True) if sell_el else ""
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
                            currency=currency,
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
