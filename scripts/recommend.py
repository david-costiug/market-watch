import argparse
import sys

from app.database.connection import get_connection
from app.services.recommendation_service import (
    DEFAULT_MAX_AGE_HOURS,
    DEFAULT_MIN_SPREAD,
    get_market_stats,
    rank_own_rate,
    recommend_rate,
)


def main():
    parser = argparse.ArgumentParser(description="Get market stats and recommended exchange rates.")
    parser.add_argument("currency", type=str, help="Currency code (e.g. EUR, USD)")
    parser.add_argument(
        "--strategy",
        type=str,
        default="beat_best",
        choices=["beat_best", "match_average"],
        help="Recommendation strategy (default: beat_best)",
    )
    parser.add_argument(
        "--margin",
        type=float,
        default=0.002,
        help="Margin to add to buy rate / subtract from sell rate (default: 0.002)",
    )
    parser.add_argument(
        "--min-spread",
        type=float,
        default=DEFAULT_MIN_SPREAD,
        help=f"Minimum allowable spread before fallback (default: {DEFAULT_MIN_SPREAD})",
    )
    parser.add_argument(
        "--max-age-hours",
        type=float,
        default=DEFAULT_MAX_AGE_HOURS,
        help=f"Max age of rates in hours to include (default: {DEFAULT_MAX_AGE_HOURS})",
    )

    args = parser.parse_args()
    currency = args.currency.upper()

    try:
        with get_connection() as conn:
            stats = get_market_stats(conn, currency, max_age_hours=args.max_age_hours)
            rec = recommend_rate(
                conn,
                currency,
                strategy=args.strategy,
                margin=args.margin,
                min_spread=args.min_spread,
                max_age_hours=args.max_age_hours,
            )
            own_rank = rank_own_rate(conn, currency, max_age_hours=args.max_age_hours)

        print("=" * 55)
        print(f" MARKET WATCH - RATE RECOMMENDATION ENGINE ({currency})")
        print("=" * 55)
        age_str = f"last {args.max_age_hours}h" if args.max_age_hours else "all-time"
        print(f"\n--- Market Overview ({stats.competitor_count} Competitors active in {age_str}) ---")

        print(f"  Best Competitor Buy : {stats.best_buy:.4f}")
        print(f"  Best Competitor Sell: {stats.best_sell:.4f}")
        print(f"  Market Avg Buy      : {stats.avg_buy:.4f}")
        print(f"  Market Avg Sell     : {stats.avg_sell:.4f}")

        print("\n--- Current Own Office Rate & Market Rank ---")
        if own_rank.own_buy is not None and own_rank.own_sell is not None:
            print(f"  Posted Buy          : {own_rank.own_buy:.4f} ({own_rank.buy_rank_text})")
            print(f"  Posted Sell         : {own_rank.own_sell:.4f} ({own_rank.sell_rank_text})")
        else:
            print("  Posted Rates        : No active rates posted yet for this currency.")

        print("\n--- Recommendation ---")
        print(f"  Target Strategy     : {args.strategy} (Margin: {args.margin:.4f})")
        if rec.is_fallback:
            print("  [SAFETY ALERT]    : Beating best rate would shrink spread below MIN_SPREAD.")
            print(f"                       Falling back to strategy: '{rec.strategy_used}'.")

        else:
            print(f"  Strategy Applied    : {rec.strategy_used}")
        print(f"  Recommended Buy     : {rec.recommended_buy:.4f}")
        print(f"  Recommended Sell    : {rec.recommended_sell:.4f}")
        print(f"  Resulting Spread    : {rec.spread:.4f}")
        print("=" * 55)

    except ValueError as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Unexpected error: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
