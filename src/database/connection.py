import sqlite3
import os

# Get the absolute path to the directory of the current file (src/database)
SRC_DATABASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Go up two levels to get the project root, then join with the 'data' directory
DB_PATH = os.path.join(SRC_DATABASE_DIR, "..", "..", "data", "cards.db")


def get_db_connection() -> sqlite3.Connection:
    """Establishes and returns a database connection."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database file not found at '{DB_PATH}'. Please ensure it exists."
        )

    conn = sqlite3.connect(DB_PATH)
    # This allows us to access columns by name (e.g., row['title']) which is very helpful.
    conn.row_factory = sqlite3.Row
    return conn
