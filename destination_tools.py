from langchain_core.tools import tool

from constraints_checker import check_constraints
from cost_calculator import calculate_cost
from destinations_data import load_destinations
from models import TripRequest


def build_destination_tool(trip: TripRequest):
    # Capture a separate copy of this trip for the tool.
    trip_snapshot = trip.model_copy(deep=True)

    @tool
    def assess_destinations() -> dict:
        """Assess sample Delhi departure packages for the current trip.

        Returns destination interests, estimated costs, and violations
        of the implemented budget, overnight-bus, and Wi-Fi checks.
        Prices and travel times are fictional sample estimates.
        Passing these checks does not verify other requirements.
        """
        if trip_snapshot.departure_city.strip().casefold() != "delhi":
            return {
                "status": "unsupported_departure",
                "message": "The sample dataset only supports Delhi departures.",
                "destinations": [],
            }

        results = []

        for destination in load_destinations():
            costs = calculate_cost(trip_snapshot, destination)
            violations = check_constraints(trip_snapshot, destination)

            results.append(
                {
                    "id": destination.id,
                    "name": destination.name,
                    "interests": destination.interests,
                    "estimated_cost_per_person_inr": costs,
                    "passes_implemented_checks": not violations,
                    "violations": violations,
                }
            )

        return {
            "status": "ok",
            "data_source": "Fictional sample packages; not live travel data.",
            "destinations": results,
        }

    return assess_destinations