from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from zoneinfo import ZoneInfo
import time

ROMANIA_TZ = ZoneInfo("Europe/Bucharest")

BNR_URL = "https://www.cursbnr.ro/curs-valutar-banci"
SOURCE_NAME = "BNR"


def get_driver():
    """Create a headless Chrome driver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    return webdriver.Chrome(options=options)


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
                    {
                        "platform_source": f"{SOURCE_NAME}",
                        "name": f"{bank_name}",
                        "city": None,
                        "type": "bank",
                        "currency": "EUR",
                        "buy": float(buy_rate.replace(",", ".")),
                        "sell": float(sell_rate.replace(",", ".")),
                        "timestamp": datetime.now(ROMANIA_TZ).strftime(
                            "%Y-%m-%dT%H:%M"
                        ),
                    }
                )
        except Exception:
            continue
    return rates


def wait_for_proper_loading(driver):
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "table"))
    )
    time.sleep(2)


if __name__ == "__main__":
    data = scrape_bnr()
    for entry in data:
        print(entry)
