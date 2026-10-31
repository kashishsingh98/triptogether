from constraints_checker import check_constraints
from destinations_data import load_destinations
from models import ScoutReport, TripRequest


def validate_scout_report(
    trip: TripRequest,
    report: ScoutReport,
) -> None:
    if trip.departure_city.strip().casefold() != "delhi":
        raise ValueError(
            "This validator currently supports Delhi sample packages only."
        )

    destinations = load_destinations()
    known_ids = {destination.id for destination in destinations}

    shortlisted_ids = [
        recommendation.destination_id
        for recommendation in report.shortlist
    ]
    excluded_ids = report.excluded_destination_ids

    # Reject repeated entries.
    if len(shortlisted_ids) != len(set(shortlisted_ids)):
        raise ValueError("The shortlist contains duplicate destination IDs.")

    if len(excluded_ids) != len(set(excluded_ids)):
        raise ValueError("The exclusions contain duplicate destination IDs.")

    shortlisted = set(shortlisted_ids)
    excluded = set(excluded_ids)

    # Reject invented IDs.
    unknown_ids = (shortlisted | excluded) - known_ids

    if unknown_ids:
        raise ValueError(
            f"Unknown destination IDs: {sorted(unknown_ids)}"
        )

    # A destination cannot be both accepted and rejected.
    if shortlisted & excluded:
        raise ValueError(
            "A destination appears in both shortlist and exclusions."
        )

    # Independently calculate the expected classification.
    expected_shortlist = {
        destination.id
        for destination in destinations
        if not check_constraints(trip, destination)
    }

    expected_exclusions = known_ids - expected_shortlist

    if shortlisted != expected_shortlist:
        raise ValueError(
            "Incorrect shortlist. "
            f"Expected {sorted(expected_shortlist)}, "
            f"received {sorted(shortlisted)}."
        )

    if excluded != expected_exclusions:
        raise ValueError(
            "Incorrect exclusions. "
            f"Expected {sorted(expected_exclusions)}, "
            f"received {sorted(excluded)}."
        )