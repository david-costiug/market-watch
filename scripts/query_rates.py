from app.database.connection import get_connection
from app.repositories.rate_repository import get_rates


def main():
    with get_connection() as conn:
        records = get_rates(conn)
        for record in records:
            print(record)


if __name__ == "__main__":
    main()
