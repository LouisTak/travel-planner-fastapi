from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import date

from models.travel_plan import TravelPlan
from models.travel_plan_day import TravelPlanDay
from models.activity import Activity


async def get_travel_plan_by_id(db: Session, travel_plan_id: str) -> Optional[TravelPlan]:
    """
    Get a travel plan by ID.
    
    Args:
        db: Database session
        travel_plan_id: ID of the travel plan
        
    Returns:
        Travel plan if found, None otherwise
    """
    return db.query(TravelPlan).filter(TravelPlan.id == travel_plan_id).first()


async def get_travel_plans_by_user_id(db: Session, user_id: str) -> List[TravelPlan]:
    """
    Get all travel plans for a user.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        List of travel plans
    """
    return db.query(TravelPlan).filter(TravelPlan.user_id == user_id).all()


async def get_travel_plan_days(db: Session, travel_plan_id: str) -> List[TravelPlanDay]:
    """
    Get all days for a travel plan.
    
    Args:
        db: Database session
        travel_plan_id: ID of the travel plan
        
    Returns:
        List of travel plan days
    """
    return db.query(TravelPlanDay).filter(TravelPlanDay.travel_plan_id == travel_plan_id).order_by(TravelPlanDay.day_number).all()


async def get_activities_by_day_id(db: Session, travel_plan_day_id: str) -> List[Activity]:
    """
    Get all activities for a travel plan day.
    
    Args:
        db: Database session
        travel_plan_day_id: ID of the travel plan day
        
    Returns:
        List of activities
    """
    return db.query(Activity).filter(Activity.travel_plan_day_id == travel_plan_day_id).order_by(Activity.start_at).all()


async def delete_travel_plan(db: Session, travel_plan_id: str) -> bool:
    """
    Delete a travel plan and all related data.
    
    Args:
        db: Database session
        travel_plan_id: ID of the travel plan
        
    Returns:
        True if deleted, False otherwise
    """
    # Get the travel plan
    travel_plan = await get_travel_plan_by_id(db, travel_plan_id)
    if not travel_plan:
        return False
    
    # Get all days
    days = await get_travel_plan_days(db, travel_plan_id)
    
    # Delete all activities for each day
    for day in days:
        activities = await get_activities_by_day_id(db, day.id)
        for activity in activities:
            db.delete(activity)
    
    # Delete all days
    for day in days:
        db.delete(day)
    
    # Delete the travel plan
    db.delete(travel_plan)
    db.commit()
    
    return True 