from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends, Path, Query
from sqlalchemy.orm import Session

from database.database import get_db
from schemas.authentication_schemas import oauth2_scheme, get_current_user
from models.user import User
from repositories.travel_plan_repository import (
    get_travel_plan_by_id,
    get_travel_plans_by_user_id,
    get_travel_plan_days,
    get_activities_by_day_id,
    delete_travel_plan
)
from utils.response_wrapper import api_response
from middleware.jwt_auth import JWTBearer

router = APIRouter(tags=["Travel Plans"])

from schemas.ai_schemas import TravelPlanResponse

auth_bearer = JWTBearer()  # Basic authentication

@router.get("/travel-plans", status_code=status.HTTP_200_OK, response_model=None)
async def get_user_travel_plans(
    credentials: str = Depends(auth_bearer)
) -> List[Dict[str, Any]]:
    """
    Get all travel plans for the current user.
    
    Args:
        db: Database session
        current_user: Current authenticated user
        token: JWT token for authentication
        
    Returns:
        List of travel plans
    """
    # Get all travel plans for the user    
    current_user = await get_current_user(credentials.credentials)

    if(not current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    travel_plans = await get_travel_plans_by_user_id(current_user.id)
    
    # Format the response
    result = []
    for plan in travel_plans:
        result.append({
            "id": plan.id,
            "title": plan.title,
            "destination": plan.destination,
            "start_at": plan.start_at,
            "end_at": plan.end_at,
            "created_at": plan.created_at
        })
    
    return api_response(data=result)


@router.get("/travel-plans/{travel_plan_id}", status_code=status.HTTP_200_OK, response_model=None)
async def get_travel_plan_details(
    travel_plan_id: str = Path(..., description="ID of the travel plan"),
    credentials: str = Depends(auth_bearer)
) -> Dict[str, Any]:
    """
    Get details of a specific travel plan.
    
    Args:
        travel_plan_id: ID of the travel plan
        db: Database session
        current_user: Current authenticated user
        token: JWT token for authentication
        
    Returns:
        Travel plan details
    """
    # Get the travel plan
    current_user = await get_current_user(credentials.credentials)
    travel_plan = await get_travel_plan_by_id(travel_plan_id)
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel plan not found"
        )
    
    # Check if the travel plan belongs to the user
    if travel_plan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this travel plan"
        )
    
    # Get all days for the travel plan
    days = await get_travel_plan_days(travel_plan_id)
    
    # Format the days and activities
    formatted_days = []
    for day in days:
        # Get activities for the day
        activities = await get_activities_by_day_id(day.id)
        
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
        "days": formatted_days
    }
    
    return api_response(data=result)


@router.delete("/travel-plans/{travel_plan_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_user_travel_plan(
    travel_plan_id: str = Path(..., description="ID of the travel plan"),
    credentials: str = Depends(auth_bearer)
):
    """
    Delete a travel plan.
    
    Args:
        travel_plan_id: ID of the travel plan
        db: Database session
        current_user: Current authenticated user
        token: JWT token for authentication
    """
    # Get the travel plan
    current_user = await get_current_user(credentials.credentials)
    travel_plan = await get_travel_plan_by_id(travel_plan_id)
    if not travel_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Travel plan not found"
        )
    
    # Check if the travel plan belongs to the user
    if travel_plan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this travel plan"
        )
    
    # Delete the travel plan
    success = await delete_travel_plan(travel_plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete travel plan"
        ) 