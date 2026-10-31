from models import TripRequest
from preference_memory import load_preferences


def resolve_trip_preferences(trip: TripRequest) -> TripRequest:
    trip_data = trip.model_dump()

    for traveller in trip_data["travellers"]:
        if not traveller["use_saved_preferences"]:
            continue

        # Explicit current preferences take priority.
        if traveller["soft_preferences"]:
            continue

        traveller["soft_preferences"] = load_preferences(
            traveller["id"]
        )

    return TripRequest.model_validate(trip_data)