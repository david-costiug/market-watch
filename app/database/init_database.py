from pathlib import Path

import psycopg2

from app.database.connection import get_connection


def init_db():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                schema_path = Path(__file__).resolve().parent / "schema.sql"
                with open(schema_path, "r") as f:
                    cur.execute(f.read())
            conn.commit()
            print("Connected to PostgreSQL database successfully. Schema initialised.")
    except psycopg2.OperationalError as e:
        print("Failed to connect to database: ", e)


if __name__ == "__main__":
    init_db()
