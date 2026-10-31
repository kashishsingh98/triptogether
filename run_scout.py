from langchain_core.messages import AIMessage, ToolMessage
from scout_validator import validate_scout_report
from destination_scout import build_destination_scout
from sample_trip import trip
import json
from planner_tools import build_planner_tool
from itinerary_planner import build_itinerary_planner


if __name__ == "__main__":
    scout = build_destination_scout(trip)

    request = (
        "Assess the available destinations for this group. "
        "Shortlist those that pass the implemented checks, "
        "explain the trade-offs, and explain any exclusions.\n\n"
        "Trip data:\n"
        f"{trip.model_dump_json(indent=2)}"
    )

    result = scout.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": request,
                }
            ]
        },
        config={"recursion_limit": 10},
    )

    tool_results = []

    print("\n--- Tool activity ---")

    for message in result["messages"]:
        if isinstance(message, AIMessage):
            for tool_call in message.tool_calls:
                print(f"Requested tool: {tool_call['name']}")

        elif isinstance(message, ToolMessage):
            tool_results.append(message)
            print(f"Received result from: {message.name}")

    if not any(
        message.name == "assess_destinations"
        for message in tool_results
    ):
        raise RuntimeError(
            "The Scout did not execute its tool. "
            "Do not treat its answer as grounded in the dataset."
        )

    report = result["structured_response"]
    validate_scout_report(trip, report)
    print("\nScout destination classification passed validation.")

    print("\n--- Structured Scout report ---")
    print(report.model_dump_json(indent=2))

    print("\n--- Shortlisted IDs ---")
    for recommendation in report.shortlist:
        print(recommendation.destination_id)

        planner_tool = build_planner_tool(trip, report)
    planning_options = planner_tool.invoke({})

    print("\n--- Planner tool output ---")
    print(
        json.dumps(
            planning_options,
            indent=2,
            ensure_ascii=False,
        )
    )
    if not report.shortlist:
        print("\nNo shortlisted destinations. Skipping the Planner.")
    else:
        planner = build_itinerary_planner(trip, report)

        planner_request = (
            "Create an itinerary for every shortlisted destination. "
            "Use the planning tool for activities and durations.\n\n"
            "Trip data:\n"
            f"{trip.model_dump_json(indent=2)}\n\n"
            "Scout report:\n"
            f"{report.model_dump_json(indent=2)}"
        )

        planner_result = planner.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": planner_request,
                    }
                ]
            },
            config={"recursion_limit": 10},
        )

        planning_tool_used = any(
            isinstance(message, ToolMessage)
            and message.name == "get_planning_options"
            for message in planner_result["messages"]
        )

        if not planning_tool_used:
            raise RuntimeError(
                "The Planner did not execute get_planning_options."
            )

        planner_report = planner_result["structured_response"]

        print("\n--- Planner tool execution confirmed ---")
        print("\n--- Structured itinerary report ---")
        print(planner_report.model_dump_json(indent=2))