from dataclasses import dataclass
from app.models.entity import Entity
from app.models.exchange_rate import ExchangeRate


@dataclass
class ScrapedRecord:
    """Combined entity + rate data as it comes from a scraper."""

    entity: Entity
    rate: ExchangeRate
