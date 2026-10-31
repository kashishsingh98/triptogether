import os

from dotenv import load_dotenv
from openai import OpenAI


def main():
    load_dotenv()

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing. Add it to your .env file.")

    client = OpenAI()

    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        instructions=(
            "You are TripTogether, a friendly group travel assistant. "
            "Explain travel trade-offs clearly. "
            "Do not invent current prices or availability."
        ),
        input=(
            "Three friends are planning a trip. "
            "One wants adventure, one wants relaxation, "
            "and one has a strict budget. "
            "In three short sentences, explain how you would help them agree."
        ),
        max_output_tokens=250,
    )

    print(response.output_text)


if __name__ == "__main__":
    main()