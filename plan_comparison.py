from activity_data import load_activities
from cost_calculator import calculate_cost
from destinations_data import load_destinations
from models import PlannerReport, ScoutReport, TripRequest
from planner_validator import validate_planner_report


def compare_plans(
    trip: TripRequest,
    scout_report: ScoutReport,
    planner_report: PlannerReport,
) -> list[dict]:
    validate_planner_report(trip, scout_report, planner_report)

    activities = {
        activity.id: activity
        for activity in load_activities()
    }

    destinations = {
        destination.id: destination
        for destination in load_destinations()
    }

    comparisons = []

    for itinerary in planner_report.itineraries:
        destination = destinations[itinerary.destination_id]

        covered_interests = {
            interest.strip().casefold()
            for day in itinerary.days
            for activity_id in day.activity_ids
            for interest in activities[activity_id].interests
        }

        traveller_results = []
        coverage_scores = []

        for traveller in trip.travellers:
            requested = {
                interest.strip().casefold()
                for interest in traveller.interests
                if interest.strip()
            }

            matched = requested & covered_interests
            unmatched = requested - covered_interests

            if requested:
                coverage = len(matched) / len(requested)
                coverage_scores.append(coverage)
                coverage_percent = round(coverage * 100, 1)
            else:
                coverage_percent = None

            traveller_results.append(
                {
                    "traveller_id": traveller.id,
                    "name": traveller.name,
                    "matched_interests": sorted(matched),
                    "unmatched_interests": sorted(unmatched),
                    "interest_coverage_percent": coverage_percent,
                }
            )

        comparisons.append(
            {
                "destination_id": destination.id,
                "estimated_cost_per_person_inr": calculate_cost(
                    trip, destination
                )["total"],
                "travellers": traveller_results,
                "lowest_interest_coverage_percent": (
                    round(min(coverage_scores) * 100, 1)
                    if coverage_scores
                    else None
                ),
            }
        )

    return comparisons