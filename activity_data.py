import json
from pathlib import Path

from destinations_data import load_destinations
from models import Activity


DATA_PATH = Path(__file__).parent / "activities.json"


def load_activities() -> list[Activity]:
    with DATA_PATH.open(encoding="utf-8") as file:
        records = json.load(file)

    activities = [
        Activity.model_validate(record)
        for record in records
    ]

    activity_ids = [activity.id for activity in activities]

    if len(activity_ids) != len(set(activity_ids)):
        raise ValueError("Activity IDs must be unique.")

    known_destination_ids = {
        destination.id
        for destination in load_destinations()
    }

    for activity in activities:
        if activity.destination_id not in known_destination_ids:
            raise ValueError(
                f"Activity {activity.id} references an unknown destination."
            )

    return activities


if __name__ == "__main__":
    for activity in load_activities():
        print(
            f"{activity.destination_id}: "
            f"{activity.name} "
            f"({activity.duration_hours} hours)"
        )