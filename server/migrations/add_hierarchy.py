import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "sentinel.db"


def column_exists(cursor, table_name, column_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def run_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if not table_exists(cursor, "posts"):
        cursor.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                title VARCHAR NOT NULL UNIQUE,
                level INTEGER NOT NULL,
                can_monitor INTEGER DEFAULT 0,
                can_manage_hierarchy INTEGER DEFAULT 0
            )
        """)

    if not column_exists(cursor, "users", "post_id"):
        cursor.execute("ALTER TABLE users ADD COLUMN post_id INTEGER")

    conn.commit()
    conn.close()

    print("Hierarchy migration completed successfully.")


if __name__ == "__main__":
    run_migration()