from checkpoint_storage import open_checkpointer
from workflow import build_workflow


if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "friends-delhi-trip-001",
        }
    }

    with open_checkpointer() as checkpointer:
        workflow = build_workflow(checkpointer=checkpointer)
        snapshot = workflow.get_state(config)

        if "trip" not in snapshot.values:
            raise ValueError(
                "No saved trip found. Run save_trip.py first."
            )

        saved_trip = snapshot.values["trip"]

        print(f"Restored trip from: {saved_trip.departure_city}")

        for traveller in saved_trip.travellers:
            print(
                f"{traveller.name}: "
                f"₹{traveller.budget_inr:,}"
            )