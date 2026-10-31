from datetime import date
from typing import Literal
from pydantic import BaseModel, Field, model_validator


class Traveller(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)

    budget_inr: int = Field(
        gt=0,
        description="Maximum total trip budget for this traveller, in INR.",
    )

    interests: list[str] = Field(default_factory=list)

    hard_constraints: list[str] = Field(
        default_factory=list,
        description="Requirements the plan must satisfy.",
    )

    soft_preferences: list[str] = Field(
        default_factory=list,
        description="Preferences that can be negotiated.",
    )
    avoid_overnight_buses: bool = False
    requires_accommodation_wifi: bool = False
    use_saved_preferences: bool = False

class TripRequest(BaseModel):
    departure_city: str = Field(min_length=1)
    start_date: date
    return_date: date
    travellers: list[Traveller] = Field(min_length=1)
    revision_notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_trip(self):
        if self.return_date <= self.start_date:
            raise ValueError("Return date must be after the start date.")

        traveller_ids = [traveller.id for traveller in self.travellers]

        if len(traveller_ids) != len(set(traveller_ids)):
            raise ValueError("Every traveller must have a unique ID.")

        return self

    @property
    def nights(self) -> int:
        return (self.return_date - self.start_date).days

    @property
    def calendar_days(self) -> int:
        return self.nights + 1

class Destination(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    interests: list[str] = Field(default_factory=list)

    return_transport_per_person_inr: int = Field(ge=0)
    accommodation_per_person_per_night_inr: int = Field(ge=0)
    food_per_person_per_day_inr: int = Field(ge=0)
    activities_per_person_per_day_inr: int = Field(ge=0)

    travel_hours_each_way: float = Field(gt=0)
    transport_mode: Literal["train", "flight", "bus", "car"]
    overnight_travel: bool
    accommodation_has_wifi: bool

class DestinationRecommendation(BaseModel):
    destination_id: str = Field(
        description="Exact destination ID returned by assess_destinations."
    )
    match_summary: str = Field(
        description="Explain matches supported by the destination interests."
    )
    unverified_preferences: list[str] = Field(
        description="Preferences that the available data cannot establish."
    )


class ScoutReport(BaseModel):
    shortlist: list[DestinationRecommendation]
    excluded_destination_ids: list[str]
    summary: str

class Activity(BaseModel):
    id: str = Field(min_length=1)
    destination_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    interests: list[str] = Field(min_length=1)
    duration_hours: float = Field(gt=0)

class ItineraryDay(BaseModel):
    day_number: int = Field(ge=1)
    activity_ids: list[str] = Field(
        description="Activity IDs from the tool. May be empty for a free day."
    )
    explanation: str = Field(
        description="Brief explanation of the day, including travel or free time."
    )


class DestinationItinerary(BaseModel):
    destination_id: str
    days: list[ItineraryDay]
    trade_offs: list[str]
    unverified_details: list[str]


class PlannerReport(BaseModel):
    itineraries: list[DestinationItinerary]

class MediatorReport(BaseModel):
    recommended_destination_id: str
    explanation: str
    compromises: list[str]
    questions_for_group: list[str]
    limitations: list[str]

class TravellerVote(BaseModel):
    traveller_id: str = Field(min_length=1)
    choice: Literal["accept", "compromise", "reject"]
    reason: str = Field(default="", max_length=1000)

    @model_validator(mode="after")
    def require_rejection_reason(self):
        if self.choice == "reject" and not self.reason.strip():
            raise ValueError("Please explain why the plan does not work.")

        return self