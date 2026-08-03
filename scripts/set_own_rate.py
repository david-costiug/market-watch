import argparse
from datetime import datetime

from app.core.config import TIMEZONE, TIMESTAMP_FORMAT
from app.database.connection import get_connection
from app.models.exchange_rate import ExchangeRate
from app.services.own_office_service import get_own_office_entity_id
from app.services.rate_service import create_exchange_rate


def main():
    parser = argparse.ArgumentParser(description="Set exchange rate for own office.")
    parser.add_argument("currency", type=str, help="Currency code (e.g. EUR)")
    parser.add_argument("buy", type=float, help="Buy rate")
    parser.add_argument("sell", type=float, help="Sell rate")

    args = parser.parse_args()

    timestamp = datetime.now(TIMEZONE).strftime(TIMESTAMP_FORMAT)
    rate = ExchangeRate(
        currency=args.currency.upper(),
        buy=args.buy,
        sell=args.sell,
        timestamp=timestamp,
    )

    with get_connection() as conn:
        entity_id = get_own_office_entity_id(conn)
        create_exchange_rate(conn, entity_id, rate)
        conn.commit()

    print(
        f"Successfully set exchange rate for {rate.currency} (buy={rate.buy}, sell={rate.sell}) at {timestamp}"
    )


if __name__ == "__main__":
    main()
