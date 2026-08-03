from datetime import datetime, timedelta

from app.core.config import TIMESTAMP_FORMAT, TIMEZONE
from app.models.exchange_rate import ExchangeRate


def insert_exchange_rate(conn, entity_id: int, rate: ExchangeRate):
    """Insert a new exchange rate record."""
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO exchange_rates
        (entity_id, currency, buy_rate, sell_rate, scraped_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (entity_id, currency, scraped_at) DO NOTHING
        RETURNING id
        """,
        (entity_id, rate.currency, rate.buy, rate.sell, rate.timestamp),
    )

    result = cursor.fetchone()
    return result[0] if result else None


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


def get_latest_rates_by_currency(
    conn,
    currency: str,
    exclude_entity_id: int | None = None,
    max_age_hours: int | float | None = None,
):
    """Fetch the most recent exchange rate per entity for a given currency using Postgres DISTINCT ON."""
    cursor = conn.cursor()

    conditions = ["er.currency = %s"]
    params = [currency.upper()]

    if exclude_entity_id is not None:
        conditions.append("er.entity_id != %s")
        params.append(exclude_entity_id)

    if max_age_hours is not None:
        cutoff = datetime.now(TIMEZONE) - timedelta(hours=max_age_hours)
        conditions.append("er.scraped_at >= %s")
        params.append(cutoff.strftime(TIMESTAMP_FORMAT))

    where_clause = " WHERE " + " AND ".join(conditions)

    query = f"""
        SELECT DISTINCT ON (er.entity_id)
            er.id,
            er.entity_id,
            e.name,
            e.platform_source,
            er.currency,
            er.buy_rate,
            er.sell_rate,
            er.scraped_at
        FROM exchange_rates er
        JOIN entities e ON er.entity_id = e.id
        {where_clause}
        ORDER BY er.entity_id, er.scraped_at DESC
    """
    cursor.execute(query, tuple(params))

    rows = cursor.fetchall()
    return [
        {
            "id": r[0],
            "entity_id": r[1],
            "name": r[2],
            "platform_source": r[3],
            "currency": r[4],
            "buy_rate": float(r[5]),
            "sell_rate": float(r[6]),
            "scraped_at": r[7],
        }
        for r in rows
    ]


def get_latest_rate_for_entity(conn, entity_id: int, currency: str):
    """Fetch the most recent exchange rate for a specific entity and currency."""
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT buy_rate, sell_rate
        FROM exchange_rates
        WHERE entity_id = %s AND currency = %s
        ORDER BY scraped_at DESC
        LIMIT 1
        """,
        (entity_id, currency.upper()),
    )
    
    row = cursor.fetchone()
    if row:
        return {
            "buy_rate": float(row[0]),
            "sell_rate": float(row[1])
        }
    return None

