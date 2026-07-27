from app.models.entity import Entity


def get_entity_id(conn, entity: Entity):
    """Check if an entity exists and return its ID, or None if it doesn't exist."""
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM entities
        WHERE platform_source = %s
        AND name = %s
        AND (city = %s OR (city IS NULL AND %s IS NULL))
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
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (platform_source, name, city) DO NOTHING
        RETURNING id
        """,
        (entity.platform_source, entity.name, entity.city, entity.type),
    )

    result = cursor.fetchone()
    return result[0] if result else None
