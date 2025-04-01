from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date

from models.travel_plan import TravelPlan
from models.travel_plan_day import TravelPlanDay
from models.activity import Activity
from database.database import get_db
from schemas.ai_schemas import TravelPlanDBCreate
async def get_travel_plan_by_id(travel_plan_id: str) -> Optional[TravelPlan]:
    """
    Get a travel plan by ID.
    
    Args:
        travel_plan_id: ID of the travel plan
        
    Returns:
        Travel plan if found, None otherwise
    """
    db = next(get_db())
    return db.query(TravelPlan).filter(TravelPlan.id == travel_plan_id).first()


async def get_travel_plans_by_user_id(user_id: str) -> List[TravelPlan]:
    """
    Get all travel plans for a user.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of travel plans
    """
    db = next(get_db())
    return db.query(TravelPlan).filter(TravelPlan.user_id == user_id).all()


async def get_travel_plan_days( travel_plan_id: str) -> List[TravelPlanDay]:
    """
    Get all days for a travel plan.
    
    Args:
        travel_plan_id: ID of the travel plan
        
    Returns:
        List of travel plan days
    """
    db = next(get_db())
    return db.query(TravelPlanDay).filter(TravelPlanDay.travel_plan_id == travel_plan_id).order_by(TravelPlanDay.day_number).all()


async def get_activities_by_day_id(travel_plan_day_id: str) -> List[Activity]:
    """
    Get all activities for a travel plan day.
    
    Args:
        travel_plan_day_id: ID of the travel plan day
        
    Returns:
        List of activities
    """
    db = next(get_db())
    return db.query(Activity).filter(Activity.travel_plan_day_id == travel_plan_day_id).order_by(Activity.start_at).all()


async def delete_travel_plan(travel_plan_id: str) -> bool:
    """
    Delete a travel plan and all related data.
    
    Args:
        travel_plan_id: ID of the travel plan
        
    Returns:
        True if deleted, False otherwise
    """
    # Get the travel plan
    db = next(get_db())
    travel_plan = await get_travel_plan_by_id(db, travel_plan_id)
    if not travel_plan:
        return False
    
    # Get all days
    days = await get_travel_plan_days(travel_plan_id)
    
    # Delete all activities for each day
    for day in days:
        activities = await get_activities_by_day_id(day.id)
        for activity in activities:
            db.delete(activity)
    
    # Delete all days
    for day in days:
        db.delete(day)
    
    # Delete the travel plan
    db.delete(travel_plan)
    db.commit()
    
    return True 

async def create_travel_plan(travel_plan: TravelPlanDBCreate, user_id: str) -> TravelPlan:
    """
    Create a new travel plan.
    
    Args:
        travel_plan: Travel plan data
        
    Returns:
        Created travel plan
    """
    db = next(get_db())
    travel_plan = TravelPlan(**travel_plan.model_dump())
    travel_plan.user_id = user_id
    db.add(travel_plan)
    db.commit()
    db.refresh(travel_plan)
    return travel_plan

