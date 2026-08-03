from __future__ import annotations

from dataclasses import dataclass


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
    own_buy: float | None
    own_sell: float | None
    buy_rank: int | None
    sell_rank: int | None
    total_competitors: int
    buy_rank_text: str
    sell_rank_text: str
