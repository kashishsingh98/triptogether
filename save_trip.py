from checkpoint_storage import open_checkpointer
from models import TripRequest
from sample_trip import trip
from workflow import build_workflow


if __name__ == "__main__":
    trip_data = trip.model_dump()

    for traveller in trip_data["travellers"]:
        if traveller["id"] == "traveller_2":
            traveller["budget_inr"] = 10000

    updated_trip = TripRequest.model_validate(trip_data)

    config = {
        "configurable": {
            "thread_id": "friends-delhi-trip-001",
        },
        "recursion_limit": 20,
    }

    with open_checkpointer() as checkpointer:
        workflow = build_workflow(checkpointer=checkpointer)

        result = workflow.invoke(
            {
                "trip": updated_trip,
                "planner_report": None,
            },
            config=config,
        )

        print("\nTrip saved to SQLite.")
        print(result["scout_report"].summary)