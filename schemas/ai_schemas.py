from datetime import date, time
from typing import Optional, List
from pydantic import BaseModel, Field


class TravelPlanInput(BaseModel):
    """Schema for travel plan input data."""
    destination: str = Field(..., description="Destination city and country")
    duration: int = Field(..., description="Number of days for the trip", gt=0)
    interests: str = Field(default="general sightseeing and local culture", 
                                    description="Interests to consider for the trip")
    start_date: date = Field(default=None, description="Start date of the trip")


class TravelSuggestionInput(BaseModel):
    """Schema for travel suggestion input data."""
    destination: str = Field(..., description="Destination city and country")
    query: str = Field(..., description="Question about the destination")


class RegenerateDayInput(BaseModel):
    """Schema for regenerating a day in a travel plan."""
    day_number: int = Field(..., description="Day number to regenerate (1-indexed)", gt=0)
    interests: Optional[str] = Field(default=None, description="Specific interests for this day")


class Activity(BaseModel):
    """Schema for a single activity in a travel plan."""
    location: str
    activity: str
    tips: str
    start_at: str
    end_at: str


class Day(BaseModel):
    """Schema for a single day in a travel plan."""
    day_number: int
    description: str
    reminder: str
    activities: List[Activity]


class TravelPlan(BaseModel):
    """Schema for the travel plan output."""
    title: str
    destination: str
    remarks: str
    days: List[Day]
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


class TravelPlanDBCreate(BaseModel):
    """Schema for creating a travel plan in the database."""
    title: str
    destination: str
    remarks: Optional[str] = None
    start_at: date
    end_at: date


class TravelPlanDayDBCreate(BaseModel):
    """Schema for creating a travel plan day in the database."""
    travel_plan_id: str
    day_number: int
    description: str
    reminder: str


class ActivityDBCreate(BaseModel):
    """Schema for creating an activity in the database."""
    travel_plan_day_id: str
    location: str
    activity: str
    tips: str
    start_at: str
    end_at: str 