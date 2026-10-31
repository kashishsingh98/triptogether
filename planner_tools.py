from langchain_core.tools import tool

from activity_data import load_activities
from destinations_data import load_destinations
from models import ScoutReport, TripRequest
from scout_validator import validate_scout_report


def build_planner_tool(
    trip: TripRequest,
    scout_report: ScoutReport,
):
    # Reject an invalid shortlist before creating the tool.
    validate_scout_report(trip, scout_report)

    shortlisted_ids = {
        recommendation.destination_id
        for recommendation in scout_report.shortlist
    }

    calendar_days = trip.calendar_days

    @tool
    def get_planning_options() -> dict:
        """Get sample activities for the validated destination shortlist.

        Includes estimated activity durations and travel hours each way.
        These are fictional planning examples, not verified availability.
        Opening hours, local transfers, and Wi-Fi quality are unknown.
        """
        destinations = load_destinations()
        activities = load_activities()

        options = []

        for destination in destinations:
            if destination.id not in shortlisted_ids:
                continue

            destination_activities = [
                activity.model_dump()
                for activity in activities
                if activity.destination_id == destination.id
            ]

            options.append(
                {
                    "destination_id": destination.id,
                    "destination_name": destination.name,
                    "travel_hours_each_way": destination.travel_hours_each_way,
                    "activities": destination_activities,
                }
            )

        return {
            "calendar_days": calendar_days,
            "data_source": "Fictional sample activities and travel estimates.",
            "destinations": options,
            "limitations": [
                "Opening hours and availability are not verified.",
                "Local transfer times are not included.",
                "Activity costs are not itemized.",
            ],
        }

    return get_planning_options