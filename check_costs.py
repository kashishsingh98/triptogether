from cost_calculator import calculate_cost
from destinations_data import load_destinations
from sample_trip import trip


if __name__ == "__main__":
    destinations = load_destinations()

    for destination in destinations:
        costs = calculate_cost(trip, destination)

        print(f"\n{destination.name}")
        print(f"  Transport:     ₹{costs['transport']:,}")
        print(f"  Accommodation: ₹{costs['accommodation']:,}")
        print(f"  Food:          ₹{costs['food']:,}")
        print(f"  Activities:    ₹{costs['activities']:,}")
        print(f"  Total/person:  ₹{costs['total']:,}")

        for traveller in trip.travellers:
            remaining = traveller.budget_inr - costs["total"]

            if remaining >= 0:
                print(
                    f"  {traveller.name}: within budget "
                    f"(₹{remaining:,} remaining)"
                )
            else:
                print(
                    f"  {traveller.name}: over budget "
                    f"by ₹{abs(remaining):,}"
                )