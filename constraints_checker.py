from cost_calculator import calculate_cost
from models import Destination, TripRequest


def check_constraints(
    trip: TripRequest,
    destination: Destination,
) -> list[str]:
    violations = []
    total_cost = calculate_cost(trip, destination)["total"]

    for traveller in trip.travellers:
        if total_cost > traveller.budget_inr:
            excess = total_cost - traveller.budget_inr

            violations.append(
                f"{traveller.name}: exceeds budget by ₹{excess:,}."
            )

        is_overnight_bus = (
            destination.transport_mode == "bus"
            and destination.overnight_travel
        )

        if traveller.avoid_overnight_buses and is_overnight_bus:
            violations.append(
                f"{traveller.name}: overnight buses are not allowed."
            )

        if (
            traveller.requires_accommodation_wifi
            and not destination.accommodation_has_wifi
        ):
            violations.append(
                f"{traveller.name}: accommodation must have Wi-Fi."
            )

    return violations