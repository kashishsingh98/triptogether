from uuid import uuid4

import streamlit as st

from activity_data import load_activities
from checkpoint_storage import open_checkpointer
from destinations_data import load_destinations
from models import TripRequest
from plan_comparison import compare_plans
from sample_trip import trip as sample_trip
from workflow import build_workflow
import hashlib
import json

from models import TravellerVote
from voting import summarize_votes


st.set_page_config(
    page_title="TripTogether",
    page_icon="🧳",
    layout="wide",
)

st.title("🧳 TripTogether")
st.write("Different travel styles. One shared plan.")

st.info(
    "Demo: prices, activities, and travel times are fictional samples. "
    "Packages currently support Delhi departures only."
)

st.caption(
    "Local group-planning demo: everyone’s entries are visible "
    "to the person using this screen."
)

if "trip_thread_id" not in st.session_state:
    st.session_state.trip_thread_id = str(uuid4())


def split_preferences(text: str) -> list[str]:
    return [
        value.strip()
        for value in text.split(";")
        if value.strip()
    ]

def render_voting_panel(result):
    trip = result["effective_trip"]
    planner_report = result["planner_report"]
    mediator_report = result["mediator_report"]

    # Identify the exact proposal being voted on.
    proposal_data = {
        "thread_id": st.session_state.trip_thread_id,
        "trip": trip.model_dump(mode="json"),
        "itineraries": planner_report.model_dump(mode="json"),
        "recommended_destination_id": (
            mediator_report.recommended_destination_id
        ),
    }

    proposal_json = json.dumps(
        proposal_data,
        sort_keys=True,
        ensure_ascii=False,
    )

    proposal_id = hashlib.sha256(
        proposal_json.encode("utf-8")
    ).hexdigest()

    votes_key = f"votes_{proposal_id}"

    if votes_key not in st.session_state:
        st.session_state[votes_key] = []

    st.divider()
    st.subheader("Does this proposal work for everyone?")

    st.caption(
        "Record each traveller’s response to the recommended plan. "
        "This shared-screen demo does not verify who submits a vote."
    )

    choices = {
        "Not voted yet": None,
        "Works for me": "accept",
        "I accept with a compromise": "compromise",
        "Doesn’t work for me": "reject",
    }

    vote_inputs = []

    with st.form(f"voting_form_{proposal_id}"):
        for traveller in trip.travellers:
            st.write(f"**{traveller.name}**")

            choice_label = st.radio(
                "Response",
                options=list(choices),
                key=f"choice_{proposal_id}_{traveller.id}",
            )

            reason = st.text_area(
                "Reason or trade-off",
                help="Required when rejecting the proposal.",
                max_chars=1000,
                key=f"reason_{proposal_id}_{traveller.id}",
            )

            vote_inputs.append(
                {
                    "traveller_id": traveller.id,
                    "choice": choices[choice_label],
                    "reason": reason,
                }
            )

        votes_submitted = st.form_submit_button(
            "Record group responses"
        )

    if votes_submitted:
        try:
            votes = [
                TravellerVote.model_validate(vote)
                for vote in vote_inputs
                if vote["choice"] is not None
            ]

            # Validate the complete submission before saving it.
            summarize_votes(
                [traveller.id for traveller in trip.travellers],
                votes,
            )

            st.session_state[votes_key] = votes
            st.success("Responses recorded.")

        except ValueError as error:
            st.error(f"Responses were not updated: {error}")

    recorded_votes = st.session_state[votes_key]

    summary = summarize_votes(
        [traveller.id for traveller in trip.travellers],
        recorded_votes,
    )

    names = {
        traveller.id: traveller.name
        for traveller in trip.travellers
    }

    st.write("**Recorded responses for this proposal**")

    if summary["status"] == "agreed":
        st.success(
            "All travellers have a recorded acceptance for this proposal."
        )

    elif summary["status"] == "needs_changes":
        st.warning("The proposal needs changes.")

        for rejection in summary["rejections"]:
            name = names[rejection["traveller_id"]]
            st.write(f"{name}: {rejection['reason']}")

    else:
        st.info("Waiting for everyone’s response.")

    if summary["pending_traveller_ids"]:
        pending_names = [
            names[traveller_id]
            for traveller_id in summary["pending_traveller_ids"]
        ]

        st.write("Still waiting for: " + ", ".join(pending_names))

    if summary["compromise_traveller_ids"]:
        compromise_names = [
            names[traveller_id]
            for traveller_id in summary["compromise_traveller_ids"]
        ]

        st.write(
            "Accepted with a compromise: "
            + ", ".join(compromise_names)
        )
    if summary["status"] == "needs_changes":
        st.caption(
            "Ask the agents to consider the recorded rejection reasons. "
            "Existing budgets and hard constraints remain in force."
        )

        if st.button(
            "Ask the agents to revise",
            key=f"revise_{proposal_id}",
        ):
            revised_data = result["trip"].model_dump()

            new_notes = [
                (
                    f"{names[rejection['traveller_id']]} "
                    f"({rejection['traveller_id']}) requests: "
                    f"{rejection['reason']}"
                )
                for rejection in summary["rejections"]
            ]

            # Preserve earlier feedback without duplicating identical notes.
            revised_data["revision_notes"] = list(
                dict.fromkeys(
                    revised_data["revision_notes"] + new_notes
                )
            )

            try:
                revised_trip = TripRequest.model_validate(revised_data)

                config = {
                    "configurable": {
                        "thread_id": st.session_state.trip_thread_id,
                    },
                    "recursion_limit": 20,
                }

                with st.spinner("The agents are reviewing your feedback..."):
                    with open_checkpointer() as checkpointer:
                        workflow = build_workflow(
                            checkpointer=checkpointer
                        )

                        revised_result = workflow.invoke(
                            {
                                "trip": revised_trip,
                                "planner_report": None,
                                "mediator_report": None,
                            },
                            config=config,
                        )

                st.session_state.planning_result = revised_result

            except Exception as error:
                st.error(
                    "Revision could not complete. "
                    f"The previous proposal is still displayed. {error}"
                )

            else:
                st.rerun()
with st.form("trip_form"):
    st.subheader("Your trip")

    departure_city = st.selectbox("Departure city", ["Delhi"])

    date_columns = st.columns(2)

    with date_columns[0]:
        start_date = st.date_input(
            "Start date",
            value=sample_trip.start_date,
        )

    with date_columns[1]:
        return_date = st.date_input(
            "Return date",
            value=sample_trip.return_date,
        )

    st.subheader("Who’s coming?")

    traveller_inputs = []

    for index, default in enumerate(sample_trip.travellers):
        with st.expander(
            f"Traveller {index + 1}: {default.name}",
            expanded=True,
        ):
            name = st.text_input(
                "Name",
                value=default.name,
                key=f"name_{index}",
            )

            budget = st.number_input(
                "Maximum total budget per person (₹)",
                min_value=1,
                value=default.budget_inr,
                step=500,
                key=f"budget_{index}",
            )

            interests = st.multiselect(
                "Interests",
                options=[
                    "adventure",
                    "beaches",
                    "cafés",
                    "nightlife",
                    "relaxation",
                    "sightseeing",
                ],
                default=default.interests,
                key=f"interests_{index}",
            )

            preferences = st.text_area(
                "Flexible preferences — separate with semicolons",
                value="; ".join(default.soft_preferences),
                key=f"preferences_{index}",
            )

            avoid_buses = st.checkbox(
                "Avoid overnight buses",
                value=default.avoid_overnight_buses,
                key=f"avoid_buses_{index}",
            )

            requires_wifi = st.checkbox(
                "Accommodation must have Wi-Fi",
                value=default.requires_accommodation_wifi,
                key=f"wifi_{index}",
            )

            use_saved = st.checkbox(
                "Use this demo traveller’s saved preferences "
                "if the preferences above are empty",
                value=False,
                key=f"use_saved_{index}",
            )

            traveller_inputs.append(
                {
                    "id": default.id,
                    "name": name.strip(),
                    "budget_inr": int(budget),
                    "interests": interests,
                    "soft_preferences": split_preferences(preferences),
                    "avoid_overnight_buses": avoid_buses,
                    "requires_accommodation_wifi": requires_wifi,
                    "use_saved_preferences": use_saved,
                }
            )

    submitted = st.form_submit_button("Find our trip")
if submitted:
    # Clear previously displayed results before starting a new request.
    st.session_state.pop("planning_result", None)

    try:
        requested_trip = TripRequest.model_validate(
            {
                "departure_city": departure_city,
                "start_date": start_date,
                "return_date": return_date,
                "travellers": traveller_inputs,
            }
        )

        config = {
            "configurable": {
                "thread_id": st.session_state.trip_thread_id,
            },
            "recursion_limit": 20,
        }

        with st.spinner("Your agent team is comparing the options..."):
            with open_checkpointer() as checkpointer:
                workflow = build_workflow(checkpointer=checkpointer)

                result = workflow.invoke(
                    {
                        "trip": requested_trip,
                        "planner_report": None,
                        "mediator_report": None,
                    },
                    config=config,
                )

        st.session_state.planning_result = result

    except Exception as error:
        st.error(f"Planning could not complete: {error}")

result = st.session_state.get("planning_result")

if result is not None:
    st.divider()
    st.caption("Results reflect the last submitted form.")
    if result["trip"].revision_notes:
        with st.expander("Feedback considered in this revision"):
            for note in result["trip"].revision_notes:
                st.write(f"• {note}")

    if not result["scout_report"].shortlist:
        st.warning("No sample destinations fit everyone’s requirements.")
        st.write(result["scout_report"].summary)

    else:
        destinations = {
            destination.id: destination
            for destination in load_destinations()
        }

        activities = {
            activity.id: activity
            for activity in load_activities()
        }

        comparisons = compare_plans(
            result["effective_trip"],
            result["scout_report"],
            result["planner_report"],
        )

        st.subheader("How the options compare")

        comparison_rows = []

        for comparison in comparisons:
            row = {
                "Destination": destinations[
                    comparison["destination_id"]
                ].name,
                "Estimated cost/person": (
                    f"₹{comparison['estimated_cost_per_person_inr']:,}"
                ),
            }

            for traveller in comparison["travellers"]:
                score = traveller["interest_coverage_percent"]

                column = (
                    f"{traveller['name']} "
                    f"({traveller['traveller_id']})"
                )

                row[column] = (
                    f"{score:g}%" if score is not None else "Not assessed"
                )

            comparison_rows.append(row)

        st.dataframe(comparison_rows, hide_index=True)
        st.caption(
            "Percentages measure interest coverage in scheduled sample "
            "activities—not happiness or agreement."
        )

        mediation = result["mediator_report"]
        recommended = destinations[
            mediation.recommended_destination_id
        ]

        st.subheader(f"Our proposal: {recommended.name}")
        st.write(mediation.explanation)

        st.write("**The compromises**")
        for compromise in mediation.compromises:
            st.write(f"• {compromise}")

        st.write("**Before everyone agrees**")
        for question in mediation.questions_for_group:
            st.write(f"• {question}")

        with st.expander("Assumptions and unverified details"):
            for limitation in mediation.limitations:
                st.write(f"• {limitation}")

        st.subheader("Explore the itineraries")

        for itinerary in result["planner_report"].itineraries:
            destination = destinations[itinerary.destination_id]

            with st.expander(destination.name):
                for day in itinerary.days:
                    st.write(f"**Day {day.day_number}**")

                    if day.activity_ids:
                        for activity_id in day.activity_ids:
                            activity = activities[activity_id]

                            st.write(
                                f"• {activity.name} "
                                f"({activity.duration_hours:g} hours)"
                            )
                    else:
                        st.write("No scheduled activities.")

                    st.write(day.explanation)

                st.write("**Unverified details**")
                for detail in itinerary.unverified_details:
                    st.write(f"• {detail}")
        render_voting_panel(result)
            
