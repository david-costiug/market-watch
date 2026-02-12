def insert_exchange_rate(conn, entity_id, currency, buy, sell, timestamp):
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO exchange_rates
        (entity_id, currency, buy_rate, sell_rate, scraped_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (entity_id, currency, buy, sell, timestamp),
    )
