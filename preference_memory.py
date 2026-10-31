import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


DB_PATH = Path(__file__).parent / "preferences.sqlite"


@contextmanager
def open_database():
    connection = sqlite3.connect(str(DB_PATH))

    try:
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS traveller_preferences (
                    traveller_id TEXT PRIMARY KEY,
                    soft_preferences_json TEXT NOT NULL
                )
                """
            )

            yield connection
    finally:
        connection.close()


def save_preferences(
    traveller_id: str,
    soft_preferences: list[str],
    *,
    consent: bool = False,
) -> None:
    if not consent:
        raise ValueError("Explicit consent is required to save preferences.")

    if not traveller_id.strip():
        raise ValueError("Traveller ID cannot be empty.")

    with open_database() as connection:
        connection.execute(
            """
            INSERT INTO traveller_preferences (
                traveller_id,
                soft_preferences_json
            )
            VALUES (?, ?)
            ON CONFLICT(traveller_id)
            DO UPDATE SET
                soft_preferences_json = excluded.soft_preferences_json
            """,
            (
                traveller_id,
                json.dumps(soft_preferences),
            ),
        )


def load_preferences(traveller_id: str) -> list[str]:
    with open_database() as connection:
        row = connection.execute(
            """
            SELECT soft_preferences_json
            FROM traveller_preferences
            WHERE traveller_id = ?
            """,
            (traveller_id,),
        ).fetchone()

    if row is None:
        return []

    return json.loads(row[0])


def delete_preferences(traveller_id: str) -> None:
    with open_database() as connection:
        connection.execute(
            """
            DELETE FROM traveller_preferences
            WHERE traveller_id = ?
            """,
            (traveller_id,),
        )