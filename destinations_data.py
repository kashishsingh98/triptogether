import json
from pathlib import Path

from models import Destination


DATA_PATH = Path(__file__).parent / "destinations.json"


def load_destinations() -> list[Destination]:
    with DATA_PATH.open(encoding="utf-8") as file:
        records = json.load(file)

    return [Destination.model_validate(record) for record in records]


if __name__ == "__main__":
    destinations = load_destinations()

    for destination in destinations:
        print(f"{destination.name}: {', '.join(destination.interests)}")