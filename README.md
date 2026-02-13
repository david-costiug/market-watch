# Market Watch

An ETL pipeline for tracking Romanian currency exchange rates. Extracts EUR/RON buy and sell rates from multiple online sources, transforms raw data into structured records, and loads them into a local SQLite database for historical tracking.

## Data Sources

| Source | URL | Entity Type |
|--------|-----|-------------|
| **Valutare** | [valutare.ro](https://www.valutare.ro/curs/curs-valutar-case-de-schimb.html) | Exchange offices |
| **BNR** (via cursbnr.ro) | [cursbnr.ro](https://www.cursbnr.ro/curs-valutar-banci) | Banks |

## Project Structure

```
market-watch/
├── app/
│   ├── core/
│   │   ├── config.py            # Centralized configuration (DB path, URLs, timezone)
│   │   └── logging.py           # Centralized logging setup
│   ├── database/
│   │   ├── connection.py        # SQLite connection management
│   │   ├── init_database.py     # Database initialization from schema
│   │   └── schema.sql           # Table definitions
│   ├── models/
│   │   ├── entity.py            # Entity dataclass (bank / exchange office)
│   │   ├── exchange_rate.py     # ExchangeRate dataclass with validation
│   │   └── scraped_record.py    # ScrapedRecord dataclass (entity + rate pair)
│   ├── repositories/
│   │   ├── entity_repository.py # Entity CRUD operations
│   │   └── rate_repository.py   # Exchange rate CRUD and queries
│   ├── scrapers/
│   │   ├── driver.py            # Shared Selenium Chrome driver setup
│   │   ├── bnr_scraper.py       # BNR bank rate scraper
│   │   └── valutare_scraper.py  # Valutare exchange office scraper
│   └── services/
│       ├── entity_service.py    # Entity lookup/creation logic
│       ├── rate_service.py      # Rate insertion logic
│       └── pipeline_service.py  # Orchestrates scraping → storage
├── scripts/
│   ├── run_pipeline.py          # Run all scrapers and store results
│   └── query_rates.py           # Query and display stored rates
├── data/
│   └── exchange_rates.db        # SQLite database (auto-created)
├── logs/
│   └── pipeline.log             # Pipeline log file (auto-created)
├── pyproject.toml
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Python 3.9+
- Google Chrome installed
- ChromeDriver matching your Chrome version

### Initialize the Database

```bash
python app/database/init_database.py
```

## Usage

### Run the ETL Pipeline

Extracts rates from all sources, transforms and loads them into the database:

```bash
python scripts/run_pipeline.py
```

### Query Stored Rates

Display all exchange rates ordered by most recent:

```bash
python scripts/query_rates.py
```

### Run Individual Scrapers

Each scraper can be run standalone for testing (prints results to stdout without storing to the database):

```bash
python app/scrapers/bnr_scraper.py
python app/scrapers/valutare_scraper.py
```

## Architecture

### ETL Data Flow

```
[Extract] Scrapers (Selenium) → raw HTML data
    ↓
[Transform] Parse & validate → ScrapedRecord (dataclass)
    ↓
[Load] Pipeline Service → Repositories → SQLite
```

1. **Extract** — Scrapers launch a headless Chrome browser and pull raw rate data from source websites. The Valutare scraper handles lazy-loaded content by scrolling the page up to 10 times until all exchange rows are loaded.
2. **Transform** — HTML elements are parsed into validated `ScrapedRecord` dataclass objects, with string-to-float conversion (comma → dot decimal), timestamping, and rate validation (buy/sell must be > 0).
3. **Load** — Pipeline service resolves entities (get-or-create) and inserts exchange rates into SQLite. All inserts are batched in a single transaction and committed at the end.

### Database Schema

**entities** — banks and exchange offices

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (autoincrement) |
| platform_source | TEXT | Source platform (e.g., "Valutare", "BNR") |
| name | TEXT | Entity name |
| city | TEXT | City (nullable, used for exchange offices) |
| type | TEXT | "bank" or "exchange_office" |

- `UNIQUE(platform_source, name, city)` — prevents duplicate entities

**exchange_rates** — historical rate records

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key (autoincrement) |
| entity_id | INTEGER | Foreign key → entities |
| currency | TEXT | Currency code (e.g., "EUR") |
| buy_rate | REAL | Buy rate (entity buys from you) |
| sell_rate | REAL | Sell rate (entity sells to you) |
| scraped_at | TIMESTAMP | When the rate was scraped |

- `UNIQUE(entity_id, currency, scraped_at)` — prevents duplicate rate entries
- `INDEX idx_rates_entity_currency_time` on `(entity_id, currency, scraped_at)` — optimizes rate lookups
- Repositories use `INSERT OR IGNORE` to silently skip duplicate records

### Data Models

```python
# app/models/entity.py
@dataclass
class Entity:
    platform_source: str
    name: str
    city: Optional[str]
    type: str                # "bank" or "exchange_office"

# app/models/exchange_rate.py
@dataclass
class ExchangeRate:
    currency: str
    buy: float
    sell: float
    timestamp: str
    # __post_init__ raises ValueError if buy <= 0 or sell <= 0

# app/models/scraped_record.py
@dataclass
class ScrapedRecord:
    entity: Entity
    rate: ExchangeRate
```

## Configuration

All configuration is centralized in `app/core/config.py`:

| Setting | Value / Description |
|---------|---------------------|
| `BASE_DIR` | Project root directory (resolved relative to `config.py`) |
| `DB_PATH` | `data/exchange_rates.db` (relative to `BASE_DIR`) |
| `TIMEZONE` | `ZoneInfo("Europe/Bucharest")` |
| `TIMESTAMP_FORMAT` | `"%Y-%m-%dT%H:%M"` |
| `BNR_URL` | `https://www.cursbnr.ro/curs-valutar-banci` |
| `VALUTARE_URL` | `https://www.valutare.ro/curs/curs-valutar-case-de-schimb.html` |
| `CHROME_OPTIONS` | `["--headless", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]` |
| `USER_AGENT` | Custom Chrome user-agent string |

## Logging

The project uses a centralized logging system configured in `app/core/logging.py`. All pipeline activity is logged to `logs/pipeline.log` (auto-created on first run).

| Setting | Value |
|---------|-------|
| Log file | `logs/pipeline.log` |
| Log level | `INFO` |
| Format | `%(asctime)s - %(levelname)s - %(message)s` |
| Logger name | `market-watch` |

## Error Handling

- **Scraper-level** — Each scraper wraps its execution in a try/except. On failure, it logs the error and returns an empty list so the pipeline can continue with other sources.
- **Row-level** — Individual row parsing errors within a scraper are silently skipped (`continue`), allowing partial data extraction from a page.
- **Pipeline-level** — `run_pipeline.py` catches per-scraper exceptions and continues to the next scraper. If no records are collected from any source, it logs a warning and exits early.
- **Rate validation** — `ExchangeRate.__post_init__` raises `ValueError` if buy or sell rates are not positive, preventing invalid data from reaching the database.
- **Database dedup** — `INSERT OR IGNORE` combined with UNIQUE constraints prevents duplicate records without raising errors.

## Dependencies

- **selenium** — browser automation for scraping
- **sqlite3** — database (Python standard library)
- **zoneinfo** — timezone handling (Python standard library)
- **logging** — pipeline logging (Python standard library)
