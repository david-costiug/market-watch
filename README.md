# Market Watch

An ETL pipeline for tracking Romanian currency exchange rates. Extracts EUR, USD, and GBP buy and sell rates from multiple online sources, transforms raw data into structured records, and loads them into a PostgreSQL database for historical tracking. It also features a recommendation engine to suggest optimal rates for your own exchange office.

## Data Sources

| Source | URL | Entity Type |
|--------|-----|-------------|
| **Valutare** | [valutare.ro](https://www.valutare.ro) | Exchange offices |
| **BNR** (via cursbnr.ro) | [cursbnr.ro](https://www.cursbnr.ro/curs-valutar-banci) | Banks |

## Project Structure

```text
market-watch/
├── app/
│   ├── core/
│   │   ├── config.py            # Centralized configuration (DATABASE_URL, URLs, timezone)
│   │   └── logging.py           # Centralized logging setup
│   ├── database/
│   │   ├── connection.py        # PostgreSQL connection pool management
│   │   ├── init_database.py     # Database initialization from schema
│   │   └── schema.sql           # PostgreSQL table definitions
│   ├── models/
│   │   ├── entity.py            # Entity dataclass (bank / exchange office)
│   │   ├── exchange_rate.py     # ExchangeRate dataclass with validation
│   │   ├── recommendation.py    # Recommendation logic and dataclasses
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
│       ├── own_office_service.py# Own office entity resolution
│       ├── pipeline_service.py  # Orchestrates scraping → storage
│       ├── rate_service.py      # Rate insertion logic
│       └── recommendation_service.py # Market rate recommendation engine
├── scripts/
│   ├── query_rates.py           # Query and display stored rates
│   ├── recommend.py             # Generates rate recommendations
│   ├── run_pipeline.py          # Run all scrapers and store results
│   └── set_own_rate.py          # CLI to set own office rates manually
├── logs/
│   └── pipeline.log             # Pipeline log file (auto-created)
├── .env                         # Environment variables (DATABASE_URL)
├── pyproject.toml
├── .gitignore
└── README.md
```

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Google Chrome installed
- ChromeDriver matching your Chrome version

### Configuration

Create a `.env` file in the root directory:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/market_watch
OWN_OFFICE_NAME="My Exchange"
OWN_OFFICE_CITY="Bucharest"
```

### Initialize the Database

```bash
python -m app.database.init_database
```

## Usage

### Run the ETL Pipeline

Extracts rates from all sources, transforms and loads them into the PostgreSQL database:

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
python -m app.scrapers.bnr_scraper
python -m app.scrapers.valutare_scraper
```

### Set Own Office Rates

Manually set exchange rates for your own office:

```bash
python scripts/set_own_rate.py --currency EUR --buy 5.2 --sell 5.3
```

### Generate Market Recommendations

Recommend optimal buy and sell rates based on market data, incorporating a spread safety guard and stale rate filtering:

```bash
python scripts/recommend.py --currency EUR
```

## Architecture

### ETL Data Flow

```text
[Extract] Scrapers (Selenium) → raw HTML data
    ↓
[Transform] Parse & validate → ScrapedRecord (dataclass)
    ↓
[Load] Pipeline Service → Repositories → PostgreSQL Connection Pool
```

1. **Extract** — Scrapers launch a headless Chrome browser and pull raw rate data from source websites for multiple currencies (EUR, USD, GBP). The Valutare scraper handles lazy-loaded content by scrolling the page.
2. **Transform** — HTML elements are parsed into validated `ScrapedRecord` dataclass objects, with string-to-float conversion (comma → dot decimal), timestamping, and rate validation (buy/sell must be > 0).
3. **Load** — Pipeline service resolves entities (get-or-create) and inserts exchange rates into PostgreSQL using a connection pool. All inserts are batched in a single transaction and committed at the end.

### Database Schema

**entities** — banks and exchange offices

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| platform_source | VARCHAR(255) | Source platform (e.g., "Valutare", "BNR") |
| name | VARCHAR(255) | Entity name |
| city | VARCHAR(255) | City (nullable, used for exchange offices) |
| type | VARCHAR(100) | "bank" or "exchange_office" |

- `UNIQUE(platform_source, name, city)` — prevents duplicate entities

**exchange_rates** — historical rate records

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| entity_id | INTEGER | Foreign key → entities |
| currency | VARCHAR(10) | Currency code (e.g., "EUR") |
| buy_rate | NUMERIC(12, 6) | Buy rate (entity buys from you) |
| sell_rate | NUMERIC(12, 6) | Sell rate (entity sells to you) |
| scraped_at | TIMESTAMP | When the rate was scraped |

- `UNIQUE(entity_id, currency, scraped_at)` — prevents duplicate rate entries
- `INDEX idx_rates_entity_currency_time` on `(entity_id, currency, scraped_at)` — optimizes rate lookups
- Repositories use `ON CONFLICT DO NOTHING` to silently skip duplicate records

## Testing & CI

### Running Tests Locally
The project uses `pytest` for testing. Integration tests use `testcontainers` to automatically spin up a temporary PostgreSQL instance. You must have Docker installed and running locally to execute them.

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest
```

### Continuous Integration (GitHub Actions)
A CI pipeline is configured in `.github/workflows/ci.yml`. It automatically runs on every push and pull request to the `main` branch. The pipeline:
1. Lints the codebase using `ruff`.
2. Runs all unit and integration tests using `pytest` and `testcontainers`.

## Dependencies

- **selenium** — browser automation for scraping
- **beautifulsoup4** — fast HTML parsing
- **psycopg2-binary** — PostgreSQL database adapter & connection pool
- **python-dotenv** — environment variable management
- **zoneinfo** — timezone handling (Python standard library)
- **logging** — pipeline logging (Python standard library)

### Dev Dependencies
- **pytest** — testing framework
- **testcontainers** — spins up ephemeral Docker containers for integration tests
- **ruff** — lightning-fast linter and formatter
