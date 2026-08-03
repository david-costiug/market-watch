import logging
from app.repositories.rate_repository import get_latest_rate_for_entity
from app.models.exchange_rate import ExchangeRate

logger = logging.getLogger(__name__)

def validate_rate(conn, entity_id: int, rate: ExchangeRate, max_deviation_pct: float = 0.03) -> bool:
    """
    Validates that a new exchange rate does not deviate excessively from the previously known rate.
    
    If there is no prior rate for the entity/currency, it is allowed and logged as unvalidated.
    Otherwise, if the new rate's buy or sell value differs from the previous one by more than
    `max_deviation_pct`, it is rejected.
    """
    latest = get_latest_rate_for_entity(conn, entity_id, rate.currency)
    
    if not latest:
        logger.info(f"First-ever rate for entity {entity_id} currency {rate.currency}, unvalidated")
        return True
        
    prev_buy = latest['buy_rate']
    prev_sell = latest['sell_rate']
    
    # Calculate percentage deviation
    buy_diff = abs(rate.buy - prev_buy) / prev_buy if prev_buy else 0
    sell_diff = abs(rate.sell - prev_sell) / prev_sell if prev_sell else 0
    
    if buy_diff > max_deviation_pct or sell_diff > max_deviation_pct:
        return False
        
    return True
