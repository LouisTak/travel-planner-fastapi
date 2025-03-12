import json
from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from langchain_xai import ChatXAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from config import settings

from schemas.ai_schemas import (
    TravelPlanInput, 
    TravelSuggestionInput,
    TravelPlanResponse,
    TravelSuggestionResponse
)

# Initialize the AI model
xai_api_key = settings.xai_api_key
if not xai_api_key:
    raise ValueError("XAI_API_KEY is not set")

llm = ChatXAI(
    xai_api_key=xai_api_key,
    model="grok-2",
    temperature=0.7
)

# Create the output parser
output_parser = JsonOutputParser()

# Create the prompt template for travel planning
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an expert travel planner. Create a travel itinerary as a JSON object. 
    Return a VALID JSON object with this structure: {jsonFormat}
    DO NOT include any markdown formatting, indentation, or explanations outside the JSON."""),
    ("human", "Plan a {duration}-day trip to {destination}. Consider that I'm interested in {interests}.")
])

# JSON format specification
specific_json_format = '{"days":[{"day":1,"activities":[{"time":"09:00-11:00","location":"Location name","activity":"Description","tips":"Tip"}]}],"summary":"Brief overview","tips":["Tip1","Tip2"]}'

router = APIRouter(tags=["Travel Planning"])


@router.post("/plan", response_model=TravelPlanResponse, status_code=status.HTTP_200_OK)
async def ai_plan(input_data: TravelPlanInput) -> Dict[str, Any]:
    """
    Generate a travel plan using AI.
    
    This endpoint creates a detailed day-by-day itinerary for a trip based on
    the destination, duration, and interests provided.
    """
    # Development mode mock response
    if settings.env == "development":
        return {
            "destination": "Tokyo,Japan",
            "duration": 3,
            "plan": {
                "days": [
                    {
                        "day": 1,
                        "activities": [
                            {
                                "time": "09:00-11:00",
                                "location": "Tsukiji Fish Market",
                                "activity": "Explore the famous market and enjoy a sushi breakfast",
                                "tips": "Arrive early to avoid crowds and try fresh sashimi at one of the sushi stalls."
                            },
                            {
                                "time": "12:00-14:00",
                                "location": "Roppongi Hills",
                                "activity": "Visit the Mori Art Museum and enjoy lunch at the food court",
                                "tips": "Try the ramen at the food court, it's highly recommended."
                            },
                            {
                                "time": "18:00-20:00",
                                "location": "Shinjuku",
                                "activity": "Dine at Omoide Yokocho, known for its yakitori",
                                "tips": "Explore different stalls to find your favorite yakitori."
                            }
                        ]
                    },
                    {
                        "day": 2,
                        "activities": [
                            {
                                "time": "10:00-12:00",
                                "location": "Yanaka Ginza",
                                "activity": "Stroll through this traditional shopping street and taste local snacks",
                                "tips": "Try senbei (rice crackers) and taiyaki (fish-shaped cakes filled with sweet red bean paste)."
                            },
                            {
                                "time": "13:00-15:00",
                                "location": "Ueno",
                                "activity": "Visit Ameya-Yokocho market and sample street food",
                                "tips": "Don't miss the chance to try takoyaki (octopus balls)."
                            },
                            {
                                "time": "19:00-21:00",
                                "location": "Ginza",
                                "activity": "Enjoy a high-end dining experience at Sukiyabashi Jiro",
                                "tips": "Make reservations well in advance as it's very popular."
                            }
                        ]
                    },
                    {
                        "day": 3,
                        "activities": [
                            {
                                "time": "09:00-11:00",
                                "location": "Asakusa",
                                "activity": "Visit Senso-ji Temple and explore Nakamise-dori for traditional sweets",
                                "tips": "Try ningyo-yaki, a sweet cake filled with red bean paste."
                            },
                            {
                                "time": "12:00-14:00",
                                "location": "Harajuku",
                                "activity": "Lunch at a themed cafe and explore Takeshita Street",
                                "tips": "Visit a maid cafe for a unique dining experience."
                            },
                            {
                                "time": "18:00-20:00",
                                "location": "Shibuya",
                                "activity": "Dine at a conveyor belt sushi restaurant",
                                "tips": "Watch for special dishes that pass by on the conveyor belt."
                            }
                        ]
                    }
                ],
                "summary": "A 3-day culinary journey through Tokyo, exploring famous food markets, traditional snacks, and high-end dining.",
                "tips": [
                    "Always carry cash as some smaller food stalls might not accept cards.",
                    "Be adventurous with your food choices to fully experience Japanese cuisine."
                ]
            }
        }

    try:
        # Format the prompt with user input
        prompt = prompt_template.format_messages(
            jsonFormat=specific_json_format,
            destination=input_data.destination,
            duration=input_data.duration,
            interests=input_data.interests
        )
        
        # Get response from AI
        response = llm.invoke(prompt)
        
        # Parse the response
        try:
            # Clean the response to handle formatting issues
            cleaned_response = response.content.strip()
            # Find the first { and last } to extract just the JSON portion
            first_brace = cleaned_response.find('{')
            last_brace = cleaned_response.rfind('}')
            if first_brace >= 0 and last_brace > first_brace:
                cleaned_response = cleaned_response[first_brace:last_brace+1]
            
            plan = json.loads(cleaned_response)
            
            # Validate the required structure
            if not isinstance(plan, dict) or 'days' not in plan:
                raise ValueError("Response missing required structure")
            
        except Exception as e:
            # Log and return the error with the raw response for debugging
            print(f"Parsing error: {str(e)}")
            print(f"Raw response: {response.content}")
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "raw_response": response.content,
                    "error": str(e)
                }
            )

        # If start_date is provided, add actual dates to the plan
        if input_data.start_date:
            start_date = input_data.start_date
            # Uncomment if you want to add dates to each day
            # for day in plan['days']:
            #     day['date'] = (start_date + timedelta(days=day['day']-1)).strftime('%Y-%m-%d')

        return {
            "destination": input_data.destination,
            "duration": input_data.duration,
            "plan": plan
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plan: {str(e)}"
        )


@router.post("/suggest", response_model=TravelSuggestionResponse, status_code=status.HTTP_200_OK)
async def ai_suggest(input_data: TravelSuggestionInput) -> Dict[str, Any]:
    """
    Get specific travel suggestions or answers about a destination.
    
    This endpoint provides targeted information and recommendations about
    a specific destination based on the user's query.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a knowledgeable travel advisor. Provide specific, accurate information about destinations."),
        ("human", "Regarding {destination}: {query}")
    ])

    try:
        messages = prompt.format_messages(
            destination=input_data.destination,
            query=input_data.query
        )
        response = llm.invoke(messages)
        
        return {
            "destination": input_data.destination,
            "query": input_data.query,
            "suggestion": response.content
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get suggestion: {str(e)}"
        )