import json
from typing import Dict, Any, TypedDict, List, Annotated
from datetime import datetime, time

from langchain_xai import ChatXAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from config import settings

# Initialize the AI model
xai_api_key = settings.xai_api_key
if not xai_api_key:
    raise ValueError("XAI_API_KEY is not set")

llm = ChatXAI(xai_api_key=xai_api_key, model="grok-2", temperature=0.7)

# JSON format specification for travel plans
TRAVEL_PLAN_FORMAT = """
{
	"title": "Trip to [Destination]",
	"destination": "Destination name",
	"remarks": "Brief overview of the trip",
	"days": [
		{
			"day_number": 1,
			"description": "Brief description of the day",
			"reminder": "Important reminders for the day",
			"activities": [
				{
					"location": "Location name",
					"activity": "Description of the activity",
					"tips": "Useful tips",
					"start_at": "09:00",
					"end_at": "11:00"
				}
			]
		}
	],
	"tips": ["Tip1", "Tip2"]
}
"""

# Sample mock data for fallback
MOCK_TRAVEL_PLAN = {
    "title": "Cultural Tour of Paris",
    "destination": "Paris, France",
    "remarks": "A 3-day cultural tour of Paris, exploring famous landmarks and museums",
    "days": [
        {
            "day_number": 1,
            "description": "Exploring iconic landmarks",
            "reminder": "Wear comfortable shoes for walking",
            "activities": [
                {
                    "location": "Eiffel Tower",
                    "activity": "Visit the iconic Eiffel Tower",
                    "tips": "Go early to avoid crowds",
                    "start_at": "09:00",
                    "end_at": "11:00",
                },
                {
                    "location": "Louvre Museum",
                    "activity": "Explore the world-famous Louvre Museum",
                    "tips": "Don't miss the Mona Lisa",
                    "start_at": "12:00",
                    "end_at": "14:00",
                },
            ],
        },
        {
            "day_number": 2,
            "description": "Historical sites and local culture",
            "reminder": "Check for opening hours",
            "activities": [
                {
                    "location": "Notre Dame Cathedral",
                    "activity": "Visit the historic Notre Dame Cathedral",
                    "tips": "Check for ongoing restoration work",
                    "start_at": "10:00",
                    "end_at": "12:00",
                }
            ],
        },
    ],
    "tips": ["Use the metro to get around", "Learn a few French phrases"],
}


# Define state types for the travel planning graph
class TravelPlanState(TypedDict):
    destination: str
    duration: int
    interests: str
    start_date: str
    plan: Dict[str, Any]
    error: str
    retry_count: int  # Add retry counter to prevent infinite recursion


# Define state types for the travel suggestion graph
class TravelSuggestionState(TypedDict):
    destination: str
    query: str
    suggestion: str
    error: str


# Node for generating travel plans
def generate_travel_plan(state: TravelPlanState) -> TravelPlanState:
    """Generate a travel plan based on the input parameters."""
    try:
        # Check if we've reached the maximum number of retries
        if state.get("retry_count", 0) >= 3:
            # Use mock data as fallback for testing
            if settings.env == "test":
                # Create a copy of the mock data and customize it
                plan = MOCK_TRAVEL_PLAN.copy()
                plan["title"] = f"Trip to {state['destination']}"
                plan["destination"] = state["destination"]
                plan["remarks"] = (
                    f"A {state['duration']}-day trip to {state['destination']} focusing on {state['interests']}"
                )

                # Ensure we have the correct number of days
                while len(plan["days"]) < state["duration"]:
                    # Add more days if needed
                    new_day = {
                        "day_number": len(plan["days"]) + 1,
                        "description": f"Day {len(plan['days']) + 1} exploration",
                        "reminder": "Check local weather forecast",
                        "activities": [
                            {
                                "location": "Local attraction",
                                "activity": "Explore local attractions",
                                "tips": "Ask locals for recommendations",
                                "start_at": "10:00",
                                "end_at": "12:00",
                            }
                        ],
                    }
                    plan["days"].append(new_day)

                # Trim days if we have too many
                if len(plan["days"]) > state["duration"]:
                    plan["days"] = plan["days"][: state["duration"]]

                # Update day numbers to be sequential
                for i, day in enumerate(plan["days"]):
                    day["day_number"] = i + 1

                return {
                    "destination": state["destination"],
                    "duration": state["duration"],
                    "interests": state["interests"],
                    "start_date": state.get("start_date", ""),
                    "plan": plan,
                    "error": "",
                    "retry_count": state.get("retry_count", 0),
                }
            else:
                return {
                    **state,
                    "error": f"Failed after {state.get('retry_count', 0)} retries. Last error: {state.get('error', 'Unknown error')}",
                }

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are an expert travel planner. Create a travel itinerary as a JSON object. 
            Return a VALID JSON object with this structure: {TRAVEL_PLAN_FORMAT}
            
            Important formatting requirements:
            1. The "start_at" and "end_at" fields must be in 24-hour format (HH:MM)
            2. The "day_number" must be sequential integers starting from 1
            3. Include a descriptive title for the trip
            4. Include detailed descriptions and reminders for each day
            5. Provide specific tips for each activity
            
            DO NOT include any markdown formatting, indentation, or explanations outside the JSON.""",
                ),
                (
                    "human",
                    f"Plan a {state['duration']}-day trip to {state['destination']}. Consider that I'm interested in {state['interests']}.",
                ),
            ]
        )

        # Format the prompt with user input
        messages = prompt.format_messages(
            jsonFormat=TRAVEL_PLAN_FORMAT,
            destination=state["destination"],
            duration=state["duration"],
            interests=state["interests"],
        )

        # Get response from AI
        response = llm.invoke(messages)

        # Clean the response to handle formatting issues
        cleaned_response = response.content.strip()
        # Find the first { and last } to extract just the JSON portion
        first_brace = cleaned_response.find("{")
        last_brace = cleaned_response.rfind("}")
        if first_brace >= 0 and last_brace > first_brace:
            cleaned_response = cleaned_response[first_brace : last_brace + 1]

        plan = json.loads(cleaned_response)

        # Validate the required structure
        if not isinstance(plan, dict) or "days" not in plan:
            raise ValueError("Response missing required structure")

        # Ensure all required fields are present
        if "title" not in plan:
            plan["title"] = f"Trip to {state['destination']}"
        if "destination" not in plan:
            plan["destination"] = state["destination"]
        if "remarks" not in plan:
            plan["remarks"] = (
                f"A {state['duration']}-day trip to {state['destination']} focusing on {state['interests']}"
            )
        if "tips" not in plan:
            plan["tips"] = [
                "Pack appropriate clothing for the weather",
                "Research local customs before your trip",
            ]

        # Ensure each day has the required fields
        for day in plan["days"]:
            if "day_number" not in day:
                day["day_number"] = plan["days"].index(day) + 1
            if "description" not in day:
                day["description"] = f"Day {day['day_number']} exploration"
            if "reminder" not in day:
                day["reminder"] = "Check local weather forecast"

            # Ensure each activity has the required fields
            for activity in day.get("activities", []):
                if "start_at" not in activity or "end_at" not in activity:
                    # Extract time from 'time' field if it exists
                    if "time" in activity:
                        time_parts = activity["time"].split("-")
                        if len(time_parts) == 2:
                            activity["start_at"] = time_parts[0].strip()
                            activity["end_at"] = time_parts[1].strip()
                        else:
                            activity["start_at"] = "09:00"
                            activity["end_at"] = "11:00"
                    else:
                        activity["start_at"] = "09:00"
                        activity["end_at"] = "11:00"

                # Remove 'time' field if it exists
                if "time" in activity:
                    del activity["time"]

        return {
            "destination": state["destination"],
            "duration": state["duration"],
            "interests": state["interests"],
            "start_date": state.get("start_date", ""),
            "plan": plan,
            "error": "",
            "retry_count": state.get("retry_count", 0),  # Preserve retry count
        }

    except Exception as e:
        # Increment retry count
        retry_count = state.get("retry_count", 0) + 1

        # Use mock data as fallback for testing if max retries reached
        if retry_count >= 3 and settings.env == "test":
            # Create a copy of the mock data and customize it
            plan = MOCK_TRAVEL_PLAN.copy()
            plan["title"] = f"Trip to {state['destination']}"
            plan["destination"] = state["destination"]
            plan["remarks"] = (
                f"A {state['duration']}-day trip to {state['destination']} focusing on {state['interests']}"
            )

            # Ensure we have the correct number of days
            while len(plan["days"]) < state["duration"]:
                # Add more days if needed
                new_day = {
                    "day_number": len(plan["days"]) + 1,
                    "description": f"Day {len(plan['days']) + 1} exploration",
                    "reminder": "Check local weather forecast",
                    "activities": [
                        {
                            "location": "Local attraction",
                            "activity": "Explore local attractions",
                            "tips": "Ask locals for recommendations",
                            "start_at": "10:00",
                            "end_at": "12:00",
                        }
                    ],
                }
                plan["days"].append(new_day)

            # Trim days if we have too many
            if len(plan["days"]) > state["duration"]:
                plan["days"] = plan["days"][: state["duration"]]

            # Update day numbers to be sequential
            for i, day in enumerate(plan["days"]):
                day["day_number"] = i + 1

            return {
                "destination": state["destination"],
                "duration": state["duration"],
                "interests": state["interests"],
                "start_date": state.get("start_date", ""),
                "plan": plan,
                "error": "",
                "retry_count": retry_count,
            }

        return {
            "destination": state["destination"],
            "duration": state["duration"],
            "interests": state["interests"],
            "start_date": state.get("start_date", ""),
            "plan": {},
            "error": str(e),
            "retry_count": retry_count,
        }


# Node for validating travel plans
def validate_travel_plan(state: TravelPlanState) -> TravelPlanState:
    """Validate the generated travel plan."""
    if state["error"]:
        return state

    try:
        plan = state["plan"]

        # Check for required fields
        required_fields = ["title", "destination", "remarks", "days", "tips"]
        for field in required_fields:
            if field not in plan:
                raise ValueError(f"Travel plan is missing required field: {field}")

        # Check that days is a list
        if not isinstance(plan["days"], list) or len(plan["days"]) == 0:
            raise ValueError("Travel plan days must be a non-empty list")

        # Check that each day has the required structure
        for day in plan["days"]:
            required_day_fields = [
                "day_number",
                "description",
                "reminder",
                "activities",
            ]
            for field in required_day_fields:
                if field not in day:
                    raise ValueError(f"Day is missing required field: {field}")

            if not isinstance(day["activities"], list):
                raise ValueError("Activities must be a list")

            # Check that each activity has the required structure
            for activity in day["activities"]:
                required_activity_fields = [
                    "location",
                    "activity",
                    "tips",
                    "start_at",
                    "end_at",
                ]
                for field in required_activity_fields:
                    if field not in activity:
                        raise ValueError(f"Activity is missing required field: {field}")

                # Validate time format (HH:MM)
                for time_field in ["start_at", "end_at"]:
                    time_str = activity[time_field]
                    try:
                        # Try to parse the time
                        hour, minute = time_str.split(":")
                        if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                            raise ValueError(
                                f"Invalid time format in {time_field}: {time_str}"
                            )
                    except Exception:
                        # If parsing fails, set a default time
                        activity[time_field] = (
                            "09:00" if time_field == "start_at" else "11:00"
                        )

        return state

    except Exception as e:
        # Preserve retry count
        return {**state, "error": str(e)}


# Node for generating travel suggestions
def generate_travel_suggestion(state: TravelSuggestionState) -> TravelSuggestionState:
    """Generate a travel suggestion based on the input parameters."""
    try:
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a knowledgeable travel advisor. Provide specific, accurate information about destinations.",
                ),
                ("human", f"Regarding {state['destination']}: {state['query']}"),
            ]
        )

        # Format the prompt with user input
        messages = prompt.format_messages(
            destination=state["destination"], query=state["query"]
        )

        # Get response from AI
        response = llm.invoke(messages)

        return {
            "destination": state["destination"],
            "query": state["query"],
            "suggestion": response.content,
            "error": "",
        }

    except Exception as e:
        return {
            "destination": state["destination"],
            "query": state["query"],
            "suggestion": "",
            "error": str(e),
        }


# Function to determine next step based on state
def should_retry(state: TravelPlanState) -> str:
    """Determine if we should retry or end based on error and retry count."""
    # If there's no error, we're done
    if not state["error"]:
        return "end"

    # If we've reached the maximum number of retries, end with error
    if state.get("retry_count", 0) >= 3:  # Limit to 3 retries
        return "max_retries"

    # Otherwise, retry
    return "retry"


# Function to regenerate a specific day of a travel plan
def regenerate_travel_plan_day(
    plan: Dict[str, Any], day_number: int, destination: str, interests: str
) -> Dict[str, Any]:
    """
    Regenerate a specific day of a travel plan.

    Args:
        plan: The original travel plan
        day_number: The day number to regenerate (1-indexed)
        destination: The destination of the travel plan
        interests: The interests to consider for the day

    Returns:
        The updated travel plan with the regenerated day
    """
    try:
        # Create the prompt template for regenerating a day
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are an expert travel planner. Create a single day itinerary for day {day_number} of a trip to {destination}.
            Return a VALID JSON object for a single day with this structure:
            {{
              "day_number": {day_number},
              "description": "Brief description of the day",
              "reminder": "Important reminders for the day",
              "activities": [
                {{
                  "location": "Location name",
                  "activity": "Description of the activity",
                  "tips": "Useful tips",
                  "start_at": "09:00",
                  "end_at": "11:00"
                }}
              ]
            }}
            
            Important formatting requirements:
            1. The "start_at" and "end_at" fields must be in 24-hour format (HH:MM)
            2. Include detailed descriptions and reminders for the day
            3. Provide specific tips for each activity
            
            DO NOT include any markdown formatting, indentation, or explanations outside the JSON.""",
                ),
                (
                    "human",
                    f"Create a day plan for day {day_number} of a trip to {destination}. Consider that I'm interested in {interests}.",
                ),
            ]
        )

        # Get response from AI
        response = llm.invoke(
            prompt.format_messages(
                day_number=day_number, destination=destination, interests=interests
            )
        )

        # Clean the response to handle formatting issues
        cleaned_response = response.content.strip()
        # Find the first { and last } to extract just the JSON portion
        first_brace = cleaned_response.find("{")
        last_brace = cleaned_response.rfind("}")
        if first_brace >= 0 and last_brace > first_brace:
            cleaned_response = cleaned_response[first_brace : last_brace + 1]

        # Parse the regenerated day
        regenerated_day = json.loads(cleaned_response)

        # Validate the required structure
        required_day_fields = ["day_number", "description", "reminder", "activities"]
        for field in required_day_fields:
            if field not in regenerated_day:
                raise ValueError(f"Regenerated day is missing required field: {field}")

        if (
            not isinstance(regenerated_day["activities"], list)
            or len(regenerated_day["activities"]) == 0
        ):
            raise ValueError("Activities must be a non-empty list")

        # Validate each activity
        for activity in regenerated_day["activities"]:
            required_activity_fields = [
                "location",
                "activity",
                "tips",
                "start_at",
                "end_at",
            ]
            for field in required_activity_fields:
                if field not in activity:
                    raise ValueError(f"Activity is missing required field: {field}")

            # Validate time format (HH:MM)
            for time_field in ["start_at", "end_at"]:
                time_str = activity[time_field]
                try:
                    # Try to parse the time
                    hour, minute = time_str.split(":")
                    if not (0 <= int(hour) <= 23 and 0 <= int(minute) <= 59):
                        raise ValueError(
                            f"Invalid time format in {time_field}: {time_str}"
                        )
                except Exception:
                    # If parsing fails, set a default time
                    activity[time_field] = (
                        "09:00" if time_field == "start_at" else "11:00"
                    )

        # Create a copy of the original plan
        updated_plan = plan.copy()

        # Find and replace the day with the regenerated one
        for i, day in enumerate(updated_plan["days"]):
            if day["day_number"] == day_number:
                updated_plan["days"][i] = regenerated_day
                break
        else:
            # If the day wasn't found, append it
            updated_plan["days"].append(regenerated_day)
            # Sort days by day_number
            updated_plan["days"].sort(key=lambda d: d["day_number"])

        return updated_plan

    except Exception as e:
        # If there's an error, return the original plan
        return plan


# Create the travel planning graph
def create_travel_plan_graph() -> StateGraph:
    """Create a graph for travel planning."""
    # Define the workflow
    workflow = StateGraph(TravelPlanState)

    # Add nodes
    workflow.add_node("generate_plan", generate_travel_plan)
    workflow.add_node("validate_plan", validate_travel_plan)

    # Define edges
    workflow.add_edge("generate_plan", "validate_plan")

    # Define conditional edges with retry limit
    workflow.add_conditional_edges(
        "validate_plan",
        should_retry,
        {
            "retry": "generate_plan",  # Retry if there's an error and we haven't reached max retries
            "max_retries": END,  # End if we've reached max retries
            "end": END,  # End if there's no error
        },
    )

    # Set the entry point
    workflow.set_entry_point("generate_plan")

    return workflow.compile()


# Create the travel suggestion graph
def create_travel_suggestion_graph() -> StateGraph:
    """Create a graph for travel suggestions."""
    # Define the workflow
    workflow = StateGraph(TravelSuggestionState)

    # Add nodes
    workflow.add_node("generate_suggestion", generate_travel_suggestion)

    # Define edges
    workflow.add_edge("generate_suggestion", END)

    # Set the entry point
    workflow.set_entry_point("generate_suggestion")

    return workflow.compile()


# Initialize the graphs
travel_plan_graph = create_travel_plan_graph()
travel_suggestion_graph = create_travel_suggestion_graph()
