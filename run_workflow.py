from sample_trip import trip
from workflow import build_workflow
import json

from plan_comparison import compare_plans


if __name__ == "__main__":
    workflow = build_workflow()

    result = workflow.invoke(
        {"trip": trip},
        config={"recursion_limit": 20},
    )

    if not result["scout_report"].shortlist:
        print("\nNo destinations passed the implemented checks.")
        print(result["scout_report"].summary)
    else:
        print("\n--- Validated itinerary report ---")
        print(
            result["planner_report"].model_dump_json(indent=2)
        )
        comparisons = compare_plans(
            trip=result["effective_trip"],
            scout_report=result["scout_report"],
            planner_report=result["planner_report"],
        )

        print("\n--- Group interest coverage ---")
        print(
            json.dumps(
                comparisons,
                indent=2,
                ensure_ascii=False,
            )
        )
        print("\n--- Group Mediator recommendation ---")
        print(result["mediator_report"].model_dump_json(indent=2))