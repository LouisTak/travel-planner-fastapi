from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from models.travel_plan import TravelPlan
from models.travel_plan_day import TravelPlanDay
from models.activity import Activity
from schemas.ai_schemas import TravelPlanDBCreate, TravelPlanDayDBCreate, ActivityDBCreate
from repositories.travel_plan_repository import get_travel_plan_days, get_activities_by_day_id, get_travel_plan_by_id


async def create_travel_plan_from_ai_response(
    db: Session, 
    user_id: str, 
    ai_response: Dict[str, Any], 
    start_date: date = None
) -> TravelPlan:
    """
    Create a travel plan in the database from the AI response.
    
    Args:
        db: Database session
        user_id: ID of the user creating the travel plan
        ai_response: AI response containing the travel plan
        start_date: Start date of the travel plan (optional)
    
    Returns:
        The created travel plan
    """
    # Extract plan data from AI response
    plan_data = ai_response["plan"]
    duration = ai_response["duration"]
    
    # Set start and end dates
    if not start_date:
        start_date = datetime.now().date()
    end_date = start_date + timedelta(days=duration - 1)
    
    # Create travel plan
    travel_plan_data = TravelPlanDBCreate(
        title=plan_data["title"],
        destination=plan_data["destination"],
        remarks=plan_data["remarks"],
        start_at=start_date,
        end_at=end_date,
        user_id=user_id,
        tips=plan_data["tips"]
    )
    
    # Create travel plan in database
    travel_plan = TravelPlan(
        title=travel_plan_data.title,
        destination=travel_plan_data.destination,
        remarks=travel_plan_data.remarks,
        start_at=travel_plan_data.start_at,
        end_at=travel_plan_data.end_at,
        user_id=travel_plan_data.user_id
    )
    db.add(travel_plan)
    db.flush()  # Flush to get the ID
    
    # Create travel plan days
    for day_data in plan_data["days"]:
        travel_plan_day_data = TravelPlanDayDBCreate(
            travel_plan_id=travel_plan.id,
            day_number=day_data["day_number"],
            description=day_data["description"],
            reminder=day_data["reminder"]
        )
        
        # Create travel plan day in database
        travel_plan_day = TravelPlanDay(
            travel_plan_id=travel_plan_day_data.travel_plan_id,
            day_number=travel_plan_day_data.day_number,
            description=travel_plan_day_data.description,
            reminder=travel_plan_day_data.reminder
        )
        db.add(travel_plan_day)
        db.flush()  # Flush to get the ID
        
        # Create activities
        for activity_data in day_data["activities"]:
            activity_db_data = ActivityDBCreate(
                travel_plan_day_id=travel_plan_day.id,
                location=activity_data["location"],
                activity=activity_data["activity"],
                tips=activity_data["tips"],
                start_at=activity_data["start_at"],
                end_at=activity_data["end_at"]
            )
            
            # Create activity in database
            activity = Activity(
                travel_plan_day_id=activity_db_data.travel_plan_day_id,
                location=activity_db_data.location,
                activity=activity_db_data.activity,
                tips=activity_db_data.tips,
                start_at=datetime.strptime(activity_db_data.start_at, "%H:%M").time(),
                end_at=datetime.strptime(activity_db_data.end_at, "%H:%M").time()
            )
            db.add(activity)
    
    # Commit all changes
    db.commit()
    db.refresh(travel_plan)
    
    return travel_plan


async def update_travel_plan_day(
    db: Session,
    travel_plan_id: str,
    day_number: int,
    updated_day: Dict[str, Any]
) -> None:
    """
    Update a specific day in a travel plan.
    
    Args:
        db: Database session
        travel_plan_id: ID of the travel plan
        day_number: Day number to update (1-indexed)
        updated_day: Updated day data from AI
        
    Returns:
        None
    """
    # Get all days for the travel plan
    days = await get_travel_plan_days(db, travel_plan_id)
    
    # Find the day with the matching day number
    target_day = None
    for day in days:
        if day.day_number == day_number:
            target_day = day
            break
    
    # If the day doesn't exist, create it
    if not target_day:
        # Create a new day
        target_day = TravelPlanDay(
            travel_plan_id=travel_plan_id,
            day_number=day_number,
            description=updated_day["description"],
            reminder=updated_day["reminder"]
        )
        db.add(target_day)
        db.flush()  # Flush to get the ID
    else:
        # Update the existing day
        target_day.description = updated_day["description"]
        target_day.reminder = updated_day["reminder"]
        target_day.updated_at = datetime.utcnow()
    
    # Get existing activities for the day
    existing_activities = await get_activities_by_day_id(db, target_day.id)
    
    # Delete existing activities
    for activity in existing_activities:
        db.delete(activity)
    
    # Create new activities
    for activity_data in updated_day["activities"]:
        # Create activity in database
        activity = Activity(
            travel_plan_day_id=target_day.id,
            location=activity_data["location"],
            activity=activity_data["activity"],
            tips=activity_data["tips"],
            start_at=datetime.strptime(activity_data["start_at"], "%H:%M").time(),
            end_at=datetime.strptime(activity_data["end_at"], "%H:%M").time()
        )
        db.add(activity)
    
    # Commit all changes
    db.commit() 


async def get_travel_plan_details_for_ai(
    db: Session,
    travel_plan_id: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Get details of a specific travel plan for AI processing.
    
    Args:
        db: Database session
        travel_plan_id: ID of the travel plan
        user_id: ID of the user requesting the details
        
    Returns:
        Travel plan details formatted for AI processing
    """
    # Get the travel plan
    travel_plan = await get_travel_plan_by_id(db, travel_plan_id)
    if not travel_plan:
        raise ValueError("Travel plan not found")
    
    # Check if the travel plan belongs to the user
    if travel_plan.user_id != user_id:
        raise ValueError("You don't have permission to access this travel plan")
    
    # Get all days for the travel plan
    days = await get_travel_plan_days(db, travel_plan_id)
    
    # Format the days and activities
    formatted_days = []
    for day in days:
        # Get activities for the day
        activities = await get_activities_by_day_id(db, day.id)
        
        # Format activities
        formatted_activities = []
        for activity in activities:
            formatted_activities.append({
                "id": activity.id,
                "location": activity.location,
                "activity": activity.activity,
                "tips": activity.tips,
                "start_at": activity.start_at.strftime("%H:%M") if activity.start_at else None,
                "end_at": activity.end_at.strftime("%H:%M") if activity.end_at else None
            })
        
        # Format day
        formatted_days.append({
            "id": day.id,
            "day_number": day.day_number,
            "description": day.description,
            "reminder": day.reminder,
            "activities": formatted_activities
        })
    
    # Format the response
    result = {
        "id": travel_plan.id,
        "title": travel_plan.title,
        "destination": travel_plan.destination,
        "remarks": travel_plan.remarks,
        "start_at": travel_plan.start_at,
        "end_at": travel_plan.end_at,
        "created_at": travel_plan.created_at,
        "updated_at": travel_plan.updated_at,
        "days": formatted_days,
        "tips": []  # Add empty tips list as it's not stored in the database model
    }
    
    return result 