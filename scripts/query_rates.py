from app.database.connection import get_connection
from app.repositories.rate_repository import get_rates


def main():
    conn = get_connection()
    try:
        records = get_rates(conn)
        for record in records:
            print(record)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
