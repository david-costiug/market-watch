from db import get_connection
import sqlite3


def init_db():

    try:
        with get_connection() as conn:
            with open("database/schema.sql", "r") as f:
                conn.executescript(f.read())
            conn.commit()
            print(
                f"Opened SQLite database with version {sqlite3.sqlite_version} successfully."
            )
    except sqlite3.OperationalError as e:
        print("Failed to open database: ", e)


if __name__ == "__main__":
    init_db()
