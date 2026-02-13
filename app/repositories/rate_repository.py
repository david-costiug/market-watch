from app.models.exchange_rate import ExchangeRate


def insert_exchange_rate(conn, entity_id: int, rate: ExchangeRate):
    """Insert a new exchange rate record."""
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO exchange_rates
        (entity_id, currency, buy_rate, sell_rate, scraped_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (entity_id, rate.currency, rate.buy, rate.sell, rate.timestamp),
    )
    return cursor.lastrowid


def get_rates(conn):
    """Fetch all exchange rates joined with entity info, ordered by most recent."""
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT er.id, platform_source, currency, buy_rate, sell_rate, scraped_at
        FROM exchange_rates er
        JOIN entities e ON er.entity_id=e.id
        ORDER BY scraped_at DESC
        """
    )

    return cursor.fetchall()
