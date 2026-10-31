from activity_data import load_activities
from destinations_data import load_destinations
from models import PlannerReport, ScoutReport, TripRequest
from scout_validator import validate_scout_report


def validate_planner_report(
    trip: TripRequest,
    scout_report: ScoutReport,
    planner_report: PlannerReport,
) -> None:
    validate_scout_report(trip, scout_report)

    destinations = {
        destination.id: destination
        for destination in load_destinations()
    }

    activities = {
        activity.id: activity
        for activity in load_activities()
    }

    expected_ids = {
        recommendation.destination_id
        for recommendation in scout_report.shortlist
    }

    actual_ids = [
        itinerary.destination_id
        for itinerary in planner_report.itineraries
    ]

    if len(actual_ids) != len(set(actual_ids)):
        raise ValueError("Duplicate destination itineraries.")

    if set(actual_ids) != expected_ids:
        raise ValueError(
            "Itinerary destinations must exactly match the shortlist."
        )

    for itinerary in planner_report.itineraries:
        destination = destinations[itinerary.destination_id]

        expected_days = list(range(1, trip.calendar_days + 1))
        actual_days = [day.day_number for day in itinerary.days]

        if actual_days != expected_days:
            raise ValueError(
                f"{destination.name}: days must be {expected_days}, "
                f"in that order."
            )

        used_activity_ids = set()

        for day in itinerary.days:
            available_hours = 10.0

            if day.day_number == 1:
                available_hours -= destination.travel_hours_each_way

            if day.day_number == trip.calendar_days:
                available_hours -= destination.travel_hours_each_way

            scheduled_hours = 0.0

            for activity_id in day.activity_ids:
                if activity_id not in activities:
                    raise ValueError(
                        f"Unknown activity ID: {activity_id}"
                    )

                activity = activities[activity_id]

                if activity.destination_id != destination.id:
                    raise ValueError(
                        f"{activity_id} does not belong to "
                        f"{destination.name}."
                    )

                if activity_id in used_activity_ids:
                    raise ValueError(
                        f"Repeated activity: {activity_id}"
                    )

                used_activity_ids.add(activity_id)
                scheduled_hours += activity.duration_hours

            if available_hours < 0:
                raise ValueError(
                    f"{destination.name}: travel alone exceeds "
                    f"the allowance on day {day.day_number}."
                )

            if scheduled_hours > available_hours:
                raise ValueError(
                    f"{destination.name}, day {day.day_number}: "
                    f"{scheduled_hours} activity hours exceed "
                    f"the {available_hours}-hour allowance."
                )