from app.models.entity import Entity
from app.repositories.entity_repository import get_entity_id, insert_entity


def get_or_create_entity(conn, entity: Entity):
    """Check if an entity exists and return its ID, or create it and return the new ID."""

    entity_id = get_entity_id(conn, entity)
    if entity_id is None:
        entity_id = insert_entity(conn, entity)
        if entity_id is None:
            entity_id = get_entity_id(conn, entity)
    return entity_id
