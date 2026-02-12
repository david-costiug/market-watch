def get_or_create_entity(conn, platform_source, name, city, entity_type):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id FROM entities
        WHERE platform_source = ?
        AND name = ?
        AND (city = ? OR (city IS NULL AND ? IS NULL))
        """,
        (platform_source, name, city, city),
    )

    result = cursor.fetchone()

    if result:
        return result[0]

    cursor.execute(
        """
        INSERT INTO entities (platform_source, name, city, type)
        VALUES (?, ?, ?, ?)
        """,
        (platform_source, name, city, entity_type),
    )

    return cursor.lastrowid
