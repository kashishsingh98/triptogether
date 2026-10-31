from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from models import TripRequest
from sample_trip import trip
from workflow import build_workflow


if __name__ == "__main__":
    serializer = JsonPlusSerializer(
        allowed_msgpack_modules=[
            ("models", "TripRequest"),
            ("models", "Traveller"),
            ("models", "ScoutReport"),
            ("models", "DestinationRecommendation"),
            ("models", "PlannerReport"),
            ("models", "DestinationItinerary"),
            ("models", "ItineraryDay"),
        ]
    )

    memory = InMemorySaver(serde=serializer)
    workflow = build_workflow(checkpointer=memory)

    config = {
        "configurable": {
            "thread_id": "friends-delhi-trip-001",
        },
        "recursion_limit": 20,
    }

    # First execution: plan the original trip.
    print("\n=== Original trip ===")

    first_result = workflow.invoke(
        {
            "trip": trip,
            "planner_report": None,
        },
        config=config,
    )

    print(
        "Original shortlist:",
        [
            option.destination_id
            for option in first_result["scout_report"].shortlist
        ],
    )

    # Retrieve the saved state using the same trip ID.
    snapshot = workflow.get_state(config)
    saved_trip = snapshot.values["trip"]

    # Build a revised trip from the saved data.
    updated_data = saved_trip.model_dump()

    for traveller in updated_data["travellers"]:
        if traveller["id"] == "traveller_2":
            traveller["budget_inr"] = 10000

    # Validate the revised data before using it.
    updated_trip = TripRequest.model_validate(updated_data)

    print("\n=== Rahul's budget changed to ₹10,000 ===")

    second_result = workflow.invoke(
        {
            "trip": updated_trip,
            "planner_report": None,
        },
        config=config,
    )

    print(
        "Updated shortlist:",
        [
            option.destination_id
            for option in second_result["scout_report"].shortlist
        ],
    )

    if not second_result["scout_report"].shortlist:
        print("\nNo destinations pass the revised constraints.")
        print(second_result["scout_report"].summary)

    # Confirm that the revised budget is now in saved state.
    latest_snapshot = workflow.get_state(config)
    latest_trip = latest_snapshot.values["trip"]

    rahul = next(
        traveller
        for traveller in latest_trip.travellers
        if traveller.id == "traveller_2"
    )

    print(f"\nSaved budget for Rahul: ₹{rahul.budget_inr:,}")