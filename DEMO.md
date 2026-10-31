# TripTogether demo recording

Aim for 90–120 seconds. Rehearse the cases first. If you trim model waiting time, label the video as edited for time.

## Opening: the human problem

Show the three traveller cards.

Suggested narration:

“Planning a trip is easy until three friends have different budgets and interests. I built TripTogether to make those compromises visible.”

Keep the fictional-data notice visible. Use the sample dates for consistent package costs, or update them before recording and verify the resulting totals.

## Scene 1: explain the options

Generate the default four-day, three-night trip. Show the comparison table and recommended plan.

“Three agents assess destinations, build itineraries, and explain the trade-offs. Python checks the budgets, activity IDs, and schedule limits.”

If the sample activities are all scheduled, point out the difference between Rishikesh’s minimum individual interest coverage and Jaipur’s uneven coverage. Use the actual displayed result; do not script a guaranteed model choice.

## Scene 2: make the group decision visible

Record Aisha’s acceptance, Rahul’s rejection, and Neha’s acceptance. Use this reason for Rahul:

“Please keep arrival day free of scheduled activities.”

Record responses, then show “needs changes.”

“The recommendation is only a proposal. A rejection blocks agreement.”

## Scene 3: revise

Click “Ask the agents to revise.” Verify that arrival day actually has no activity IDs. Point out the considered feedback and new voting form.

“The agents can reconsider the plan using the feedback. The revised proposal needs new responses.”

If the model does not honor the request, do not present it as fixed. Show it as a limitation or repeat after improving executable revision validation.

## Scene 4: the budget plot twist

Change Rahul’s main-form budget to ₹10,000 and submit. Show that no sample package qualifies.

“When the budget changes, the system reports that none of its options fit. It does not invent a cheaper quote.”

## Closing

“Built with Python, OpenAI, LangGraph, Pydantic, SQLite, and Streamlit. It demonstrates tool-using agents, scoped memory, validation, and human decisions. The code and limitations are documented on GitHub.”

Only say the final sentence after the repository is available.

## Optional technical clip

Run `restore_trip.py` in a new terminal to show persistent trip state. Run the preference demo to show cross-trip preferences. Keep the distinction clear: current UI votes are session-local, and the browser does not yet reopen saved trips.

## Recording checklist

- No API keys, environment-file contents, or personal data on screen.
- Show actual results, including unresolved requests.
- Do not claim real booking prices, production readiness, perfect safety, or measured improvements without evidence.
- End on the recommendation or readable comparison rather than a long JSON dump.
