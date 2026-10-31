from preference_memory import load_preferences, save_preferences


if __name__ == "__main__":
    save_preferences(
        traveller_id="traveller_1",
        soft_preferences=[
            "Prefer relaxed mornings",
            "Prefer time for cafés",
        ],
        consent=True,
    )

    print("Saved preferences:")
    print(load_preferences("traveller_1"))