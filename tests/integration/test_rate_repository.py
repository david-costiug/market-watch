from pathlib import Path
import pytest
import psycopg2
from testcontainers.community.postgres import PostgresContainer

from app.models.exchange_rate import ExchangeRate
from app.repositories.rate_repository import (
    insert_exchange_rate,
    get_latest_rates_by_currency,
    get_latest_rate_for_entity,
)


@pytest.fixture(scope="module")
def postgres_conn():
    with PostgresContainer("postgres:15-alpine") as postgres:
        conn = psycopg2.connect(
            dbname=postgres.dbname,
            user=postgres.username,
            password=postgres.password,
            host=postgres.get_container_host_ip(),
            port=postgres.get_exposed_port(5432),
        )
        schema_path = Path(__file__).parent.parent.parent / "app" / "database" / "schema.sql"
        with conn.cursor() as cur:
            cur.execute(schema_path.read_text(encoding="utf-8"))
        conn.commit()
        yield conn
        conn.close()


def test_repository_postgres_integration(postgres_conn):
    conn = postgres_conn
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO entities (platform_source, name, city, type) VALUES ('BNR', 'BT Test', 'Cluj', 'bank') RETURNING id;"
    )
    entity_id = cursor.fetchone()[0]
    conn.commit()

    # Test ON CONFLICT and ordering
    rate1 = ExchangeRate(currency="EUR", buy=4.90, sell=4.95, timestamp="2026-08-01 10:00:00")
    rate2 = ExchangeRate(currency="EUR", buy=4.92, sell=4.97, timestamp="2026-08-01 12:00:00")

    id1 = insert_exchange_rate(conn, entity_id, rate1)
    id2 = insert_exchange_rate(conn, entity_id, rate2)
    conn.commit()

    assert id1 is not None
    assert id2 is not None

    # ON CONFLICT test: inserting exact duplicate should yield None
    id_dup = insert_exchange_rate(conn, entity_id, rate2)
    assert id_dup is None

    # Test get_latest_rate_for_entity
    latest = get_latest_rate_for_entity(conn, entity_id, "EUR")
    assert latest["buy_rate"] == 4.92
    assert latest["sell_rate"] == 4.97

    # Test DISTINCT ON via get_latest_rates_by_currency
    rates = get_latest_rates_by_currency(conn, "EUR")
    assert len(rates) == 1
    assert rates[0]["entity_id"] == entity_id
    assert rates[0]["buy_rate"] == 4.92
