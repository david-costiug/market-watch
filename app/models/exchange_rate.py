from dataclasses import dataclass


@dataclass
class ExchangeRate:
    currency: str
    buy: float
    sell: float
    timestamp: str

    def __post_init__(self):
        if self.buy <= 0 or self.sell <= 0:
            raise ValueError(f"Invalid rates: buy={self.buy}, sell={self.sell}")
