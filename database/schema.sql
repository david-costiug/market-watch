CREATE TABLE entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_source TEXT NOT NULL,
    name TEXT NOT NULL,
    city TEXT,
    type TEXT NOT NULL,
    UNIQUE(platform_source, name, city)
);

CREATE TABLE exchange_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id INTEGER NOT NULL,
    currency TEXT NOT NULL,
    buy_rate REAL NOT NULL,
    sell_rate REAL NOT NULL,
    scraped_at TIMESTAMP NOT NULL,
    FOREIGN KEY (entity_id) REFERENCES entities(id),
    UNIQUE(entity_id, currency, scraped_at)
);

CREATE INDEX idx_rates_entity_currency_time
ON exchange_rates(entity_id, currency, scraped_at);
