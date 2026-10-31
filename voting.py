from models import TravellerVote


def summarize_votes(
    traveller_ids: list[str],
    votes: list[TravellerVote],
) -> dict:
    if not traveller_ids:
        raise ValueError("At least one traveller is required.")

    if len(traveller_ids) != len(set(traveller_ids)):
        raise ValueError("Traveller IDs must be unique.")

    expected_ids = set(traveller_ids)
    voted_ids = [vote.traveller_id for vote in votes]

    if len(voted_ids) != len(set(voted_ids)):
        raise ValueError("Each traveller can have only one current vote.")

    unknown_ids = set(voted_ids) - expected_ids

    if unknown_ids:
        raise ValueError(
            f"Votes contain unknown travellers: {sorted(unknown_ids)}"
        )

    pending_ids = sorted(expected_ids - set(voted_ids))

    rejections = [
        {
            "traveller_id": vote.traveller_id,
            "reason": vote.reason.strip(),
        }
        for vote in votes
        if vote.choice == "reject"
    ]

    compromise_ids = [
        vote.traveller_id
        for vote in votes
        if vote.choice == "compromise"
    ]

    if rejections:
        status = "needs_changes"
    elif pending_ids:
        status = "waiting_for_votes"
    else:
        status = "agreed"

    return {
        "status": status,
        "pending_traveller_ids": pending_ids,
        "rejections": rejections,
        "compromise_traveller_ids": compromise_ids,
    }