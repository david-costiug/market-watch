from database.db import get_connection
from database.entity_service import get_or_create_entity
from database.rate_service import insert_exchange_rate


def process_scraped_data(scraped_records):
    with get_connection() as conn:
        for record in scraped_records:
            entity_id = get_or_create_entity(
                conn,
                record["platform_source"],
                record["name"],
                record["city"],
                record["type"],
            )

            insert_exchange_rate(
                conn,
                entity_id,
                record["currency"],
                record["buy"],
                record["sell"],
                record["timestamp"],
            )

        conn.commit()
