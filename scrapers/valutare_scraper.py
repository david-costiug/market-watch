from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from zoneinfo import ZoneInfo
import time

ROMANIA_TZ = ZoneInfo("Europe/Bucharest")

VALUTARE_URL = "https://www.valutare.ro/curs/curs-valutar-case-de-schimb.html"
SOURCE_NAME = "Valutare"


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
                    {
                        "platform_source": f"{SOURCE_NAME}",
                        "name": f"{exchange_name}",
                        "city": f"{city_name}",
                        "type": "exchange_office",
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


def handle_lazy_loading(driver):
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
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "exchangegrid"))
    )

    time.sleep(2)


if __name__ == "__main__":
    data = scrape_valutare()
    for entry in data:
        print(entry)
