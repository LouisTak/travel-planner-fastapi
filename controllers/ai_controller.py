import json
from datetime import timedelta
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from config import settings
from schemas.authentication_schemas import oauth2_scheme, get_current_user
from utils.ai_graph import travel_plan_graph, travel_suggestion_graph
from database.database import get_db
from services.travel_plan_service import create_travel_plan_from_ai_response
from models.user import User
from typing import Annotated
from utils.response_wrapper import api_response


from schemas.ai_schemas import (
    TravelPlanInput, 
    TravelSuggestionInput,
    TravelPlanResponse,
    TravelSuggestionResponse
)

router = APIRouter(tags=["Travel Planning"])


@router.post("/plan", response_model=TravelPlanResponse, status_code=status.HTTP_200_OK)
async def ai_plan(
    token: Annotated[str, Depends(oauth2_scheme)], 
    input_data: TravelPlanInput, 
    save_to_db: Optional[bool] = Query(False, description="Whether to save the plan to the database"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Generate a travel plan using AI.
    
    This endpoint creates a detailed day-by-day itinerary for a trip based on
    the destination, duration, and interests provided.
    
    Args:
        input_data: Input data for the travel plan
        save_to_db: Whether to save the plan to the database
        token: JWT token for authentication
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Travel plan response
    """
    # Development mode mock response
    if settings.env == "development":
        mock_response = {
            "destination": "Tokyo,Japan",
            "duration": 3,
            "plan": {
                "title": "Tokyo Food and Culture Tour",
                "destination": "Tokyo, Japan",
                "remarks": "A 3-day culinary journey through Tokyo, exploring famous food markets, traditional snacks, and high-end dining.",
                "days": [
                    {
                        "day_number": 1,
                        "description": "Exploring Tokyo's famous food markets",
                        "reminder": "Bring cash as some smaller stalls don't accept cards",
                        "activities": [
                            {
                                "location": "Tsukiji Fish Market",
                                "activity": "Explore the famous market and enjoy a sushi breakfast",
                                "tips": "Arrive early to avoid crowds and try fresh sashimi at one of the sushi stalls.",
                                "start_at": "09:00",
                                "end_at": "11:00"
                            },
                            {
                                "location": "Roppongi Hills",
                                "activity": "Visit the Mori Art Museum and enjoy lunch at the food court",
                                "tips": "Try the ramen at the food court, it's highly recommended.",
                                "start_at": "12:00",
                                "end_at": "14:00"
                            },
                            {
                                "location": "Shinjuku",
                                "activity": "Dine at Omoide Yokocho, known for its yakitori",
                                "tips": "Explore different stalls to find your favorite yakitori.",
                                "start_at": "18:00",
                                "end_at": "20:00"
                            }
                        ]
                    },
                    {
                        "day_number": 2,
                        "description": "Traditional Japanese snacks and street food",
                        "reminder": "Wear comfortable shoes as there will be a lot of walking",
                        "activities": [
                            {
                                "location": "Yanaka Ginza",
                                "activity": "Stroll through this traditional shopping street and taste local snacks",
                                "tips": "Try senbei (rice crackers) and taiyaki (fish-shaped cakes filled with sweet red bean paste).",
                                "start_at": "10:00",
                                "end_at": "12:00"
                            },
                            {
                                "location": "Ueno",
                                "activity": "Visit Ameya-Yokocho market and sample street food",
                                "tips": "Don't miss the chance to try takoyaki (octopus balls).",
                                "start_at": "13:00",
                                "end_at": "15:00"
                            },
                            {
                                "location": "Ginza",
                                "activity": "Enjoy a high-end dining experience at Sukiyabashi Jiro",
                                "tips": "Make reservations well in advance as it's very popular.",
                                "start_at": "19:00",
                                "end_at": "21:00"
                            }
                        ]
                    },
                    {
                        "day_number": 3,
                        "description": "Cultural sites and themed dining",
                        "reminder": "Check opening hours for temples and attractions",
                        "activities": [
                            {
                                "location": "Asakusa",
                                "activity": "Visit Senso-ji Temple and explore Nakamise-dori for traditional sweets",
                                "tips": "Try ningyo-yaki, a sweet cake filled with red bean paste.",
                                "start_at": "09:00",
                                "end_at": "11:00"
                            },
                            {
                                "location": "Harajuku",
                                "activity": "Lunch at a themed cafe and explore Takeshita Street",
                                "tips": "Visit a maid cafe for a unique dining experience.",
                                "start_at": "12:00",
                                "end_at": "14:00"
                            },
                            {
                                "location": "Shibuya",
                                "activity": "Dine at a conveyor belt sushi restaurant",
                                "tips": "Watch for special dishes that pass by on the conveyor belt.",
                                "start_at": "18:00",
                                "end_at": "20:00"
                            }
                        ]
                    }
                ],
                "tips": [
                    "Always carry cash as some smaller food stalls might not accept cards.",
                    "Be adventurous with your food choices to fully experience Japanese cuisine."
                ]
            }
        }

        
        return mock_response

    try:
        # Prepare the initial state for the graph
        initial_state = {
            "destination": input_data.destination,
            "duration": input_data.duration,
            "interests": input_data.interests or "general sightseeing and local culture",
            "start_date": input_data.start_date.isoformat() if input_data.start_date else "",
            "plan": {},
            "error": "",
            "retry_count": 0  # Initialize retry count
        }
        
        # Execute the graph
        result = travel_plan_graph.invoke(initial_state)
        
        # Check for errors
        if result["error"]:
            raise ValueError(f"Failed after {result['retry_count']} retries: {result['error']}")
        
        # Prepare the response
        response = {
            "destination": input_data.destination,
            "duration": input_data.duration,
            "plan": result["plan"]
        }
        
        current_user = await get_current_user(token, db)

        # Save to database if requested
        if save_to_db:
            try:
                await create_travel_plan_from_ai_response(
                    db=db,
                    user_id=current_user.id,
                    ai_response=response,
                    start_date=input_data.start_date
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to save travel plan to database: {str(e)}"
                )
        
        # Return the result
        return response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}"
        )


@router.post("/suggest", response_model=TravelSuggestionResponse, status_code=status.HTTP_200_OK)
async def ai_suggest(input_data: TravelSuggestionInput, token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Get specific travel suggestions or answers about a destination.
    
    This endpoint provides targeted information and recommendations about
    a specific destination based on the user's query.
    """
    try:
        # Prepare the initial state for the graph
        initial_state = {
            "destination": input_data.destination,
            "query": input_data.query,
            "suggestion": "",
            "error": ""
        }
        
        # Execute the graph
        result = travel_suggestion_graph.invoke(initial_state)
        
        # Check for errors
        if result["error"]:
            raise ValueError(result["error"])
        
        # Return the result
        return {
            "destination": input_data.destination,
            "query": input_data.query,
            "suggestion": result["suggestion"]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestion: {str(e)}"
        )