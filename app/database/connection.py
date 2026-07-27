from contextlib import contextmanager
import psycopg2.pool

from app.core.config import DATABASE_URL

_pool = None


def _get_pool():
    """Lazily initialise and return the connection pool."""
    global _pool
    if _pool is None or _pool.closed:
        _pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dsn=DATABASE_URL,
        )
    return _pool


@contextmanager
def get_connection():
    """Context manager to acquire and automatically release a connection to the pool."""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def close_pool():
    """Close all connections in the pool."""
    global _pool
    if _pool is not None and not _pool.closed:
        _pool.closeall()
        _pool = None
