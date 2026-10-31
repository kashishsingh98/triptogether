from constraints_checker import check_constraints
from destinations_data import load_destinations
from sample_trip import trip


def show_result(destination):
    violations = check_constraints(trip, destination)

    print(f"\n{destination.name}")

    if violations:
        for violation in violations:
            print(f"  FAIL: {violation}")
    else:
        print("  PASS: all implemented checks passed.")


if __name__ == "__main__":
    destinations = load_destinations()

    for destination in destinations:
        show_result(destination)

    # Create a separate sample without changing the original object.
    overnight_bus_sample = destinations[0].model_copy(
        update={
            "name": "Rishikesh — overnight bus, no Wi-Fi sample",
            "transport_mode": "bus",
            "overnight_travel": True,
            "accommodation_has_wifi": False,
        }
    )

    show_result(overnight_bus_sample)