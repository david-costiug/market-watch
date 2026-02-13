from app.models.entity import Entity


def get_entity_id(conn, entity: Entity):
    """Check if an entity exists and return its ID, or None if it doesn't exist."""
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM entities
        WHERE platform_source = ?
        AND name = ?
        AND (city = ? OR (city IS NULL AND ? IS NULL))
        """,
        (entity.platform_source, entity.name, entity.city, entity.city),
    )

    result = cursor.fetchone()
    return result[0] if result else None


def insert_entity(conn, entity: Entity):
    """Insert a new entity and return its ID."""
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO entities (platform_source, name, city, type)
        VALUES (?, ?, ?, ?)
        """,
        (entity.platform_source, entity.name, entity.city, entity.type),
    )

    return cursor.lastrowid
