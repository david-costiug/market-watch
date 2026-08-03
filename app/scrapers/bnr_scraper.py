from datetime import datetime
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from app.core.config import BNR_URL, TIMEZONE, TIMESTAMP_FORMAT
from app.scrapers.driver import get_driver
from app.models.entity import Entity
from app.models.exchange_rate import ExchangeRate
from app.models.scraped_record import ScrapedRecord

SOURCE_NAME = "BNR"


def scrape_bnr() -> list[ScrapedRecord]:
    """Scrape exchange rates from cursbnr.ro (EUR, USD, GBP)."""
    driver = None
    all_rates = []
    currencies = ["EUR", "USD", "GBP"]
    try:
        driver = get_driver()
        driver.get(BNR_URL)
        wait_for_proper_loading(driver)

        for currency in currencies:
            html = fetch_page_source(driver, currency)
            rates = parse_html(html, currency)
            all_rates.extend(rates)

        return all_rates

    except Exception as e:
        print(f"[ERROR] BNR scraping failed: {e}")
        return all_rates

    finally:
        if driver:
            driver.quit()


def fetch_page_source(driver, currency: str) -> str:
    """Select currency and fetch page source HTML."""
    select_element = driver.find_element(By.ID, "c1")
    select = Select(select_element)
    select.select_by_value(currency)

    time.sleep(2)
    wait_for_proper_loading(driver)
    return driver.page_source


def parse_html(html: str, currency: str) -> list[ScrapedRecord]:
    """Extract exchange rates from HTML using BeautifulSoup."""
    rates = []
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.find_all("tr")

    for row in rows:
        try:
            cells = row.find_all("td")
            if len(cells) < 3:
                continue

            bank_name = cells[0].get_text(strip=True)
            buy_rate = cells[1].get_text(strip=True)
            sell_rate = cells[2].get_text(strip=True)

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
