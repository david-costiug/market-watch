from app.models.exchange_rate import ExchangeRate
from app.repositories.rate_repository import insert_exchange_rate


def create_exchange_rate(conn, entity_id: int, rate: ExchangeRate):
    """Insert a new exchange rate record."""
    return insert_exchange_rate(conn, entity_id, rate)
