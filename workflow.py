from typing import Literal, NotRequired, TypedDict

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from destination_scout import build_destination_scout
from itinerary_planner import build_itinerary_planner
from models import PlannerReport, ScoutReport, TripRequest
from planner_validator import validate_planner_report
from scout_validator import validate_scout_report
from resolve_preferences import resolve_trip_preferences
from group_mediator import build_group_mediator
from models import MediatorReport


class TripState(TypedDict):
    trip: TripRequest
    effective_trip: NotRequired[TripRequest]
    scout_report: NotRequired[ScoutReport]
    planner_report: NotRequired[PlannerReport | None]
    mediator_report: NotRequired[MediatorReport | None]


def require_tool_result(messages, tool_name: str) -> None:
    tool_used = any(
        isinstance(message, ToolMessage)
        and message.name == tool_name
        for message in messages
    )

    if not tool_used:
        raise RuntimeError(f"Required tool was not executed: {tool_name}")


def run_scout_node(state: TripState, config: RunnableConfig):
    print("\n[1] Running Destination Scout...")

    trip = state["effective_trip"]
    scout = build_destination_scout(trip)

    request = (
        "Assess every available destination. Shortlist those that pass "
        "the implemented checks and explain exclusions.\n\n"
        f"Trip data:\n{trip.model_dump_json(indent=2)}"
    )

    result = scout.invoke(
        {"messages": [{"role": "user", "content": request}]},
        config={**config, "recursion_limit": 10},
    )

    require_tool_result(result["messages"], "assess_destinations")

    return {"scout_report": result["structured_response"]}


def validate_scout_node(state: TripState):
    print("\n[2] Validating Scout report...")

    validate_scout_report(
        state["effective_trip"],
        state["scout_report"],
    )

    return {}


def route_after_scout(
    state: TripState,
) -> Literal["plan", "finish"]:
    if state["scout_report"].shortlist:
        return "plan"

    return "finish"


def run_planner_node(state: TripState, config: RunnableConfig):
    print("\n[3] Running Itinerary Planner...")

    trip = state["effective_trip"]
    scout_report = state["scout_report"]
    planner = build_itinerary_planner(trip, scout_report)

    request = (
        "Create an itinerary for every shortlisted destination. "
        "Retrieve activities and durations using your tool.\n\n"
        f"Trip data:\n{trip.model_dump_json(indent=2)}\n\n"
        f"Scout report:\n{scout_report.model_dump_json(indent=2)}"
    )

    result = planner.invoke(
        {"messages": [{"role": "user", "content": request}]},
        config={**config, "recursion_limit": 10},
    )

    require_tool_result(result["messages"], "get_planning_options")

    return {"planner_report": result["structured_response"]}


def validate_planner_node(state: TripState):
    print("\n[4] Validating Planner report...")

    validate_planner_report(
        state["effective_trip"],
        state["scout_report"],
        state["planner_report"],
    )

    return {}

def load_preferences_node(state: TripState):
    print("\n[Memory] Resolving traveller preferences...")

    effective_trip = resolve_trip_preferences(state["trip"])

    return {
        "effective_trip": effective_trip,
        "planner_report": None,
        "mediator_report": None,
    }

def run_mediator_node(state: TripState, config: RunnableConfig):
    print("\n[5] Running Group Mediator...")

    trip = state["effective_trip"]

    mediator = build_group_mediator(
        trip,
        state["scout_report"],
        state["planner_report"],
    )

    request = (
        "Compare the validated plans. Recommend one option, "
        "explain the compromises, and ask what the group needs "
        "to decide before agreeing.\n\n"
        f"Trip data:\n{trip.model_dump_json(indent=2)}"
    )

    result = mediator.invoke(
        {"messages": [{"role": "user", "content": request}]},
        config={**config, "recursion_limit": 10},
    )

    require_tool_result(result["messages"], "get_plan_comparison")

    report = result["structured_response"]

    allowed_ids = {
        itinerary.destination_id
        for itinerary in state["planner_report"].itineraries
    }

    if report.recommended_destination_id not in allowed_ids:
        raise ValueError(
            "Mediator recommended a destination outside the validated plans."
        )

    return {"mediator_report": report}


def build_workflow(checkpointer=None):
    graph = StateGraph(TripState)

    graph.add_node("scout", run_scout_node)
    graph.add_node("validate_scout", validate_scout_node)
    graph.add_node("planner", run_planner_node)
    graph.add_node("validate_planner", validate_planner_node)
    graph.add_node("load_preferences", load_preferences_node)
    graph.add_node("mediator", run_mediator_node)

    graph.add_edge(START, "load_preferences")
    graph.add_edge("load_preferences", "scout")
    graph.add_edge("scout", "validate_scout")

    graph.add_conditional_edges(
        "validate_scout",
        route_after_scout,
        {
            "plan": "planner",
            "finish": END,
        },
    )

    graph.add_edge("planner", "validate_planner")
    graph.add_edge("validate_planner", "mediator")
    graph.add_edge("mediator", END)

    return graph.compile(checkpointer=checkpointer)