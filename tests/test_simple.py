import sys
import os
import json
from typing import Dict, Any, TypedDict

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define state types for the travel planning graph
class TravelPlanState(TypedDict):
    destination: str
    duration: int
    interests: str
    start_date: str
    plan: Dict[str, Any]
    error: str
    retry_count: int

# Define state types for the travel suggestion graph
class TravelSuggestionState(TypedDict):
    destination: str
    query: str
    suggestion: str
    error: str

# Sample mock data
MOCK_TRAVEL_PLAN = {
    "days": [
        {
            "day": 1,
            "activities": [
                {
                    "time": "09:00-11:00",
                    "location": "Eiffel Tower",
                    "activity": "Visit the iconic Eiffel Tower",
                    "tips": "Go early to avoid crowds"
                },
                {
                    "time": "12:00-14:00",
                    "location": "Louvre Museum",
                    "activity": "Explore the world-famous Louvre Museum",
                    "tips": "Don't miss the Mona Lisa"
                }
            ]
        },
        {
            "day": 2,
            "activities": [
                {
                    "time": "10:00-12:00",
                    "location": "Notre Dame Cathedral",
                    "activity": "Visit the historic Notre Dame Cathedral",
                    "tips": "Check for ongoing restoration work"
                }
            ]
        }
    ],
    "summary": "A cultural tour of Paris",
    "tips": ["Use the metro to get around", "Learn a few French phrases"]
}

# Node for generating travel plans
def generate_travel_plan(state: TravelPlanState) -> TravelPlanState:
    """Generate a travel plan based on the input parameters."""
    # Always return a successful result with the mock plan
    return {
        "destination": state["destination"],
        "duration": state["duration"],
        "interests": state["interests"],
        "start_date": state.get("start_date", ""),
        "plan": MOCK_TRAVEL_PLAN,
        "error": "",
        "retry_count": state.get("retry_count", 0)
    }

# Node for validating travel plans
def validate_travel_plan(state: TravelPlanState) -> TravelPlanState:
    """Validate the generated travel plan."""
    # Always return the state without errors
    return state

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

def test_retry_logic():
    """Test the retry logic function."""
    # Test case 1: No error
    state1 = {
        "destination": "Paris",
        "duration": 3,
        "interests": "art",
        "start_date": "",
        "plan": {},
        "error": "",
        "retry_count": 0
    }
    assert should_retry(state1) == "end", "Should end when there's no error"
    
    # Test case 2: Error but retry count < 3
    state2 = {
        "destination": "Paris",
        "duration": 3,
        "interests": "art",
        "start_date": "",
        "plan": {},
        "error": "Some error",
        "retry_count": 1
    }
    assert should_retry(state2) == "retry", "Should retry when there's an error and retry count < 3"
    
    # Test case 3: Error and retry count >= 3
    state3 = {
        "destination": "Paris",
        "duration": 3,
        "interests": "art",
        "start_date": "",
        "plan": {},
        "error": "Some error",
        "retry_count": 3
    }
    assert should_retry(state3) == "max_retries", "Should end when retry count >= 3"
    
    print("All retry logic tests passed!")

def test_generate_travel_plan():
    """Test the generate_travel_plan function."""
    # Define the initial state
    initial_state = {
        "destination": "Paris, France",
        "duration": 3,
        "interests": "art, food, and history",
        "start_date": "",
        "plan": {},
        "error": "",
        "retry_count": 0
    }
    
    # Execute the function
    result = generate_travel_plan(initial_state)
    
    # Print the result
    print("Travel Plan Result:")
    print(json.dumps(result, indent=2))
    
    # Check for errors
    assert not result["error"], f"Error in travel plan: {result['error']}"
    
    # Check that the plan has the expected structure
    assert "days" in result["plan"], "Plan is missing 'days'"
    assert "tips" in result["plan"], "Plan is missing 'tips'"
    
    print("Travel plan function test passed!")

if __name__ == "__main__":
    test_retry_logic()
    test_generate_travel_plan() 