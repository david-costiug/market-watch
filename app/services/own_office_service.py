from app.core.config import OWN_OFFICE_CITY, OWN_OFFICE_NAME, OWN_OFFICE_SOURCE
from app.models.entity import Entity
from app.services.entity_service import get_or_create_entity


def get_own_office_entity_id(conn):
    """Build an Entity for own office and get or create its ID in the database."""
    entity = Entity(
        platform_source=OWN_OFFICE_SOURCE,
        name=OWN_OFFICE_NAME,
        city=OWN_OFFICE_CITY,
        type="own_office",
    )
    return get_or_create_entity(conn, entity)
