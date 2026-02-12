from db import get_connection


def get_latest_rates():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT e.id, platform_source, currency, buy_rate, sell_rate, scraped_at
        FROM exchange_rates er
        JOIN entities e ON er.entity_id=e.id
        ORDER BY scraped_at DESC
    """
    )

    rows = cursor.fetchall()
    conn.close()
    return rows


if __name__ == "__main__":
    records = get_latest_rates()
    for record in records:
        print(record)
