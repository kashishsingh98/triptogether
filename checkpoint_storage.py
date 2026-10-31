import sqlite3
from contextlib import contextmanager
from pathlib import Path

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.checkpoint.sqlite import SqliteSaver


DB_PATH = Path(__file__).parent / "triptogether.sqlite"


@contextmanager
def open_checkpointer():
    serializer = JsonPlusSerializer(
        allowed_msgpack_modules=[
            ("models", "TripRequest"),
            ("models", "Traveller"),
            ("models", "ScoutReport"),
            ("models", "DestinationRecommendation"),
            ("models", "PlannerReport"),
            ("models", "DestinationItinerary"),
            ("models", "ItineraryDay"),
            ("models", "MediatorReport"),
        ]
    )

    connection = sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False,
    )

    try:
        yield SqliteSaver(connection, serde=serializer)
    finally:
        connection.close()