from models import Destination, TripRequest


def calculate_cost(
    trip: TripRequest,
    destination: Destination,
) -> dict[str, int]:
    transport = destination.return_transport_per_person_inr

    accommodation = (
        destination.accommodation_per_person_per_night_inr
        * trip.nights
    )

    food = (
        destination.food_per_person_per_day_inr
        * trip.calendar_days
    )

    activities = (
        destination.activities_per_person_per_day_inr
        * trip.calendar_days
    )

    return {
        "transport": transport,
        "accommodation": accommodation,
        "food": food,
        "activities": activities,
        "total": transport + accommodation + food + activities,
    }