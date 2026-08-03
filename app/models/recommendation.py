from dataclasses import dataclass
from typing import Optional


@dataclass
class MarketStats:
    currency: str
    best_buy: float
    best_sell: float
    avg_buy: float
    avg_sell: float
    competitor_count: int


@dataclass
class RateRecommendation:
    currency: str
    recommended_buy: float
    recommended_sell: float
    strategy_used: str
    margin: float
    spread: float
    is_fallback: bool = False


@dataclass
class OwnRateRanking:
    currency: str
    own_buy: Optional[float]
    own_sell: Optional[float]
    buy_rank: Optional[int]
    sell_rank: Optional[int]
    total_competitors: int
    buy_rank_text: str
    sell_rank_text: str
