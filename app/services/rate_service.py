from app.repositories.rate_repository import insert_exchange_rate
from app.models.exchange_rate import ExchangeRate


def create_exchange_rate(conn, entity_id: int, rate: ExchangeRate):
    """Insert a new exchange rate record."""
    return insert_exchange_rate(conn, entity_id, rate)
