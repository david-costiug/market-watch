CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    platform_source VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    city VARCHAR(255),
    type VARCHAR(100) NOT NULL,
    UNIQUE(platform_source, name, city)
);

CREATE TABLE IF NOT EXISTS exchange_rates (
    id SERIAL PRIMARY KEY,
    entity_id INTEGER NOT NULL,
    currency VARCHAR(10) NOT NULL,
    buy_rate NUMERIC(12, 6) NOT NULL,
    sell_rate NUMERIC(12, 6) NOT NULL,
    scraped_at TIMESTAMP NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES entities(id),
    UNIQUE(entity_id, currency, scraped_at)
);

CREATE INDEX IF NOT EXISTS idx_rates_entity_currency_time
ON exchange_rates(entity_id, currency, scraped_at);
