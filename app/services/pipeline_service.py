import logging

from app.database.connection import get_connection
from app.models.scraped_record import ScrapedRecord
from app.services.entity_service import get_or_create_entity
from app.services.rate_service import create_exchange_rate
from app.services.validation_service import validate_rate

logger = logging.getLogger(__name__)

def process_scraped_data(scraped_records: list[ScrapedRecord]):
    with get_connection() as conn:
        for record in scraped_records:
            entity_id = get_or_create_entity(conn, record.entity)

            is_valid = validate_rate(conn, entity_id, record.rate)
            if not is_valid:
                logger.warning(
                    f"REJECTED_RATE: Rate {record.rate.buy}/{record.rate.sell} for entity {entity_id} "
                    f"currency {record.rate.currency} deviates too much from previous rate."
                )
                continue

            create_exchange_rate(conn, entity_id, record.rate)
        conn.commit()
