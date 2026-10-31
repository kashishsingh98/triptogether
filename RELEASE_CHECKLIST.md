# Local verification and GitHub release

Run these checks in your complete project on your Mac. The documentation pack does not contain the implementation or dependency lockfile; it supplements the existing project.

## 1. Install and check syntax

```bash
uv sync --locked
uv run python -m py_compile app.py models.py workflow.py destination_scout.py destination_tools.py itinerary_planner.py planner_tools.py group_mediator.py checkpoint_storage.py preference_memory.py resolve_preferences.py voting.py plan_comparison.py scout_validator.py planner_validator.py cost_calculator.py constraint_checker.py destination_data.py activity_data.py
```

Compilation checks syntax, not module execution, dependency compatibility, or agent quality.

## 2. Run the local check scripts

```bash
uv run check_voting.py
uv run check_constraints.py
uv run check_preference_resolution.py
```

The preference-resolution example expects preferences to have been saved by `save_preferences_demo.py`. That script writes known sample preferences and makes no API calls.

`check_voting.py` contains assertions. Other demonstration scripts may only print output; inspect those results rather than treating exit status alone as proof of correctness.

## 3. Check the application

```bash
uv run streamlit run app.py
```

Generating and revising plans makes API calls. Record the outcomes below; do not mark a case passed before running it.

| Case | Expected behavior | Actual result |
| --- | --- | --- |
| Default four-day, three-night sample | Rishikesh and Jaipur qualify; schedules validate; Mediator proposes a valid destination | Not recorded |
| Rahul budget ₹10,000 | Empty shortlist; Planner and Mediator skipped; no old proposal displayed | Not recorded |
| Arrival day must be free | Revision considers feedback; inspect actual activity IDs, not only explanation | Not recorded |
| Request nightlife | Explicit dataset limitation; no invented activity or false claim of satisfaction | Not recorded |
| Rejection with blank reason | Rejected vote submission; earlier valid recorded votes remain unchanged | Not recorded |
| Only one traveller accepts | Waiting for remaining responses | Not recorded |
| One rejects and another has not voted | Needs changes, with pending traveller still shown | Not recorded |
| All accept or explicitly compromise | All recorded acceptances shown | Not recorded |
| Trip or itinerary changes | Changed proposal does not inherit previous votes | Not recorded |
| Return date before start | Validation error, without planning | Not recorded |

Natural-language requests such as an empty arrival day are not yet enforced by a dedicated revision validator. A failed manual case is a real limitation to fix or report.

## 4. Check persistence

```bash
uv run save_trip.py
uv run restore_trip.py
```

The first script calls the Scout and writes checkpoints. Run the second in a new process to verify Rahul’s saved ₹10,000 budget without API calls. This demonstrates backend persistence, not UI trip recovery.

## 5. Add the documentation

Copy `README.md`, `ARCHITECTURE.md`, `DEMO.md`, `RELEASE_CHECKLIST.md`, and `.env.example` from this pack into the project root. Merge `.gitignore` entries with your existing file rather than discarding existing rules. Keep the actual `pyproject.toml` and `uv.lock` produced by your working project.

## 6. Review what Git would publish

```bash
git status --short
git check-ignore .env .venv triptogether.sqlite preferences.sqlite
```

Use your local editor to inspect the source and documentation for credentials. Ignore rules do not remove secrets already tracked in Git. If a real API key was committed, remove it from the published history as appropriate and rotate the key before publishing.

Stage only the intended implementation, JSON sample datasets, dependency files, and documentation. Include the existing `.python-version` if used by uv. Exclude `.env`, local databases, virtual environments, and personal screenshots.

Review the staged result:

```bash
git diff --cached --stat
git diff --cached
```

Do not paste a diff containing credentials into a public issue or chat.

## 7. Publish after review

Suggested repository name: `triptogether`.

Suggested description: “A multi-agent group travel planning prototype with explicit constraints, scoped memory, voting, and feedback-driven revisions.”

Confirm whether the project already has a Git repository and remote before initializing or changing them. Publish the complete working project, not this documentation pack alone. Pick a license deliberately before adding a `LICENSE` file; no license has been assumed in this pack.

## 8. Share

Record the demo using `DEMO.md`, add the video or screenshots to the repository, and use the actual repository URL in the LinkedIn post. Report the observed behavior and limitations rather than unmeasured reliability or performance claims.
