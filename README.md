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
│   │   └── exchange_rate.py     # Dataclasses (Entity, ExchangeRate, ScrapedRecord)
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
├── pyproject.toml
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Python 3.9+
- Google Chrome installed
- ChromeDriver matching your Chrome version

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd market-watch

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install in editable mode
pip install -e .
```

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

## Architecture

### ETL Data Flow

```
[Extract] Scrapers (Selenium) → raw HTML data
    ↓
[Transform] Parse & validate → ScrapedRecord (dataclass)
    ↓
[Load] Pipeline Service → Repositories → SQLite
```

1. **Extract** — Scrapers launch a headless Chrome browser and pull raw rate data from source websites
2. **Transform** — HTML elements are parsed into validated `ScrapedRecord` dataclass objects, with string-to-float conversion and timestamping
3. **Load** — Pipeline service resolves entities (get-or-create) and inserts exchange rates into SQLite

### Database Schema

**entities** — banks and exchange offices

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| platform_source | TEXT | Source platform (e.g., "Valutare", "BNR") |
| name | TEXT | Entity name |
| city | TEXT | City (nullable, used for exchange offices) |
| type | TEXT | "bank" or "exchange_office" |

**exchange_rates** — historical rate records

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| entity_id | INTEGER | Foreign key → entities |
| currency | TEXT | Currency code (e.g., "EUR") |
| buy_rate | REAL | Buy rate (entity buys from you) |
| sell_rate | REAL | Sell rate (entity sells to you) |
| scraped_at | TIMESTAMP | When the rate was scraped |

### Data Models

```python
@dataclass
class Entity:
    platform_source: str
    name: str
    city: Optional[str]
    type: str

@dataclass
class ExchangeRate:
    currency: str
    buy: float      # Validated > 0
    sell: float     # Validated > 0
    timestamp: str

@dataclass
class ScrapedRecord:
    entity: Entity
    rate: ExchangeRate
```

## Configuration

All configuration is centralized in `app/core/config.py`:

| Setting | Description |
|---------|-------------|
| `DB_PATH` | Path to the SQLite database |
| `TIMEZONE` | Timezone for timestamps (Europe/Bucharest) |
| `TIMESTAMP_FORMAT` | Timestamp format string |
| `BNR_URL` | BNR scraper target URL |
| `VALUTARE_URL` | Valutare scraper target URL |
| `CHROME_OPTIONS` | Headless Chrome arguments |
| `USER_AGENT` | Browser user agent string |

## Logging

The project uses a centralized logging system configured in `app/core/logging.py`. All pipeline activity is logged to `logs/pipeline.log` (auto-created on first run).

| Setting | Value |
|---------|-------|
| Log file | `logs/pipeline.log` |
| Log level | `INFO` |
| Format | `%(asctime)s - %(levelname)s - %(message)s` |
| Logger name | `market-watch` |

## Dependencies

- **selenium** — browser automation for scraping
- **sqlite3** — database (Python standard library)
- **logging** — pipeline logging (Python standard library)
