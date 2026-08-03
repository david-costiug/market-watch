from __future__ import annotations

from app.models.recommendation import MarketStats, OwnRateRanking, RateRecommendation
from app.repositories.rate_repository import get_latest_rates_by_currency
from app.services.own_office_service import get_own_office_entity_id

DEFAULT_MIN_SPREAD = 0.005
DEFAULT_MAX_AGE_HOURS = 24.0


def get_market_stats(
    conn,
    currency: str,
    exclude_entity_id: int | None = None,
    max_age_hours: float | None = DEFAULT_MAX_AGE_HOURS,
) -> MarketStats:
    """Calculate best and average buy & sell rates across competitors within max_age_hours."""
    if exclude_entity_id is None:
        exclude_entity_id = get_own_office_entity_id(conn)

    rates = get_latest_rates_by_currency(
        conn,
        currency,
        exclude_entity_id=exclude_entity_id,
        max_age_hours=max_age_hours,
    )

    if not rates:
        age_info = f" in the last {max_age_hours} hours" if max_age_hours is not None else ""
        raise ValueError(f"No competitor rate data available for currency '{currency.upper()}'{age_info}.")

    buy_rates = [r["buy_rate"] for r in rates]
    sell_rates = [r["sell_rate"] for r in rates]

    best_buy = max(buy_rates)
    best_sell = min(sell_rates)
    avg_buy = sum(buy_rates) / len(rates)
    avg_sell = sum(sell_rates) / len(rates)

    return MarketStats(
        currency=currency.upper(),
        best_buy=round(best_buy, 4),
        best_sell=round(best_sell, 4),
        avg_buy=round(avg_buy, 4),
        avg_sell=round(avg_sell, 4),
        competitor_count=len(rates),
    )


def recommend_rate(
    conn,
    currency: str,
    strategy: str = "beat_best",
    margin: float = 0.002,
    min_spread: float = DEFAULT_MIN_SPREAD,
    max_age_hours: float | None = DEFAULT_MAX_AGE_HOURS,
) -> RateRecommendation:
    """
    Recommend a buy/sell exchange rate based on market stats and strategy.
    
    Strategies:
      - 'beat_best': recommended_buy = best_buy + margin, recommended_sell = best_sell - margin
      - 'match_average': recommended_buy = avg_buy, recommended_sell = avg_sell

    Safety Guard:
      If 'beat_best' shrinks spread (recommended_sell - recommended_buy) below min_spread,
      falls back to the average-based strategy.
    """
    stats = get_market_stats(conn, currency, max_age_hours=max_age_hours)

    is_fallback = False
    strategy_used = strategy

    if strategy == "beat_best":
        rec_buy = stats.best_buy + margin
        rec_sell = stats.best_sell - margin
        spread = rec_sell - rec_buy

        if spread < min_spread:
            # Fallback to match_average to preserve margin safety
            rec_buy = stats.avg_buy
            rec_sell = stats.avg_sell
            spread = rec_sell - rec_buy
            is_fallback = True
            strategy_used = "fallback_match_average"
    elif strategy == "match_average":
        rec_buy = stats.avg_buy
        rec_sell = stats.avg_sell
        spread = rec_sell - rec_buy
    else:
        raise ValueError(f"Unknown strategy '{strategy}'. Supported strategies: 'beat_best', 'match_average'.")

    return RateRecommendation(
        currency=currency.upper(),
        recommended_buy=round(rec_buy, 4),
        recommended_sell=round(rec_sell, 4),
        strategy_used=strategy_used,
        margin=margin,
        spread=round(spread, 4),
        is_fallback=is_fallback,
    )


def rank_own_rate(
    conn,
    currency: str,
    max_age_hours: float | None = DEFAULT_MAX_AGE_HOURS,
) -> OwnRateRanking:
    """Rank own office's posted rate against competitor rates within max_age_hours."""
    own_entity_id = get_own_office_entity_id(conn)
    all_rates = get_latest_rates_by_currency(conn, currency, max_age_hours=max_age_hours)

    own_rates = [r for r in all_rates if r["entity_id"] == own_entity_id]
    competitor_rates = [r for r in all_rates if r["entity_id"] != own_entity_id]

    total_competitors = len(competitor_rates)

    if not own_rates:
        return OwnRateRanking(
            currency=currency.upper(),
            own_buy=None,
            own_sell=None,
            buy_rank=None,
            sell_rank=None,
            total_competitors=total_competitors,
            buy_rank_text="N/A (No active rate set)",
            sell_rank_text="N/A (No active rate set)",
        )

    own_rate = own_rates[0]
    own_buy = own_rate["buy_rate"]
    own_sell = own_rate["sell_rate"]

    higher_buy_count = sum(1 for c in competitor_rates if c["buy_rate"] > own_buy)
    buy_rank = higher_buy_count + 1

    lower_sell_count = sum(1 for c in competitor_rates if c["sell_rate"] < own_sell)
    sell_rank = lower_sell_count + 1

    return OwnRateRanking(
        currency=currency.upper(),
        own_buy=round(own_buy, 4),
        own_sell=round(own_sell, 4),
        buy_rank=buy_rank,
        sell_rank=sell_rank,
        total_competitors=total_competitors,
        buy_rank_text=f"#{buy_rank} of {total_competitors} on buy",
        sell_rank_text=f"#{sell_rank} of {total_competitors} on sell",
    )

