from models import TripRequest
from resolve_preferences import resolve_trip_preferences
from sample_trip import trip


if __name__ == "__main__":
    data = trip.model_dump()

    aisha = next(
        traveller
        for traveller in data["travellers"]
        if traveller["id"] == "traveller_1"
    )

    aisha["use_saved_preferences"] = True
    aisha["soft_preferences"] = []

    original = TripRequest.model_validate(data)
    resolved = resolve_trip_preferences(original)

    print("Original:", original.travellers[0].soft_preferences)
    print("Resolved:", resolved.travellers[0].soft_preferences)

    aisha["soft_preferences"] = ["Prefer early starts for this trip"]

    current_trip = TripRequest.model_validate(data)
    current_resolved = resolve_trip_preferences(current_trip)

    print(
        "Current preferences win:",
        current_resolved.travellers[0].soft_preferences,
    )