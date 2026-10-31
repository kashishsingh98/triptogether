from datetime import date

from models import Traveller, TripRequest

travellers = [
    Traveller(
        id="traveller_1",
        name="Aisha",
        budget_inr=20000,
        interests=["beaches", "cafés"],
        hard_constraints=["No overnight buses"],
        soft_preferences=["Prefer relaxed mornings"],
        avoid_overnight_buses=True,
    ),
    Traveller(
        id="traveller_2",
        name="Rahul",
        budget_inr=15000,
        interests=["adventure", "nightlife"],
        soft_preferences=["Prefer staying near activity spots"],
    ),
    Traveller(
        id="traveller_3",
        name="Neha",
        budget_inr=18000,
        interests=["relaxation", "sightseeing"],
        hard_constraints=["Accommodation must have Wi-Fi"],
        soft_preferences=["Prefer quiet accommodation"],
        requires_accommodation_wifi=True,
    ),
]

trip = TripRequest(
    departure_city="Delhi",
    start_date=date(2026, 11, 20),
    return_date=date(2026, 11, 23),
    travellers=travellers,
)


if __name__ == "__main__":
    print(trip.model_dump_json(indent=2))
    print(f"Duration: {trip.calendar_days} calendar days, {trip.nights} nights")


# if __name__ == "__main__":
#     for traveller in travellers:
#         print(traveller.model_dump_json(indent=2))