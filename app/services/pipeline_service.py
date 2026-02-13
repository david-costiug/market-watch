from app.database.connection import get_connection
from app.services.entity_service import get_or_create_entity
from app.services.rate_service import create_exchange_rate
from app.models.scraped_record import ScrapedRecord


def process_scraped_data(scraped_records: list[ScrapedRecord]):
    with get_connection() as conn:
        for record in scraped_records:
            entity_id = get_or_create_entity(conn, record.entity)

            create_exchange_rate(conn, entity_id, record.rate)
        print(f"Processed {len(scraped_records)} records.")
        conn.commit()
