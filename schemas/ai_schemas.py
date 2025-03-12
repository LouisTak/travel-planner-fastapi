from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class TravelPlanInput(BaseModel):
    """Schema for travel plan input data."""
    destination: str = Field(..., description="Destination city and country")
    duration: int = Field(..., description="Number of days for the trip", gt=0)
    interests: Optional[str] = Field(default="general sightseeing and local culture", 
                                    description="Interests to consider for the trip")
    start_date: Optional[date] = Field(default=None, description="Start date of the trip")


class TravelSuggestionInput(BaseModel):
    """Schema for travel suggestion input data."""
    destination: str = Field(..., description="Destination city and country")
    query: str = Field(..., description="Question about the destination")


class Activity(BaseModel):
    """Schema for a single activity in a travel plan."""
    time: str
    location: str
    activity: str
    tips: str


class Day(BaseModel):
    """Schema for a single day in a travel plan."""
    day: int
    activities: List[Activity]


class TravelPlan(BaseModel):
    """Schema for the travel plan output."""
    days: List[Day]
    summary: str
    tips: List[str]


class TravelPlanResponse(BaseModel):
    """Schema for the travel plan response."""
    destination: str
    duration: int
    plan: TravelPlan


class TravelSuggestionResponse(BaseModel):
    """Schema for the travel suggestion response."""
    destination: str
    query: str
    suggestion: str 