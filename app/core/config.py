from pathlib import Path
from zoneinfo import ZoneInfo

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data" / "exchange_rates.db"

# Timezone
TIMEZONE = ZoneInfo("Europe/Bucharest")
TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M"

# Scraper URLs
BNR_URL = "https://www.cursbnr.ro/curs-valutar-banci"
VALUTARE_URL = "https://www.valutare.ro/curs/curs-valutar-case-de-schimb.html"

# Chrome options
CHROME_OPTIONS = [
    "--headless",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
]
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
