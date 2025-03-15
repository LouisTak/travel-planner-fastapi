import sys
import os
import json
from typing import Dict, Any, TypedDict

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph.graph import StateGraph, END

# Define state types for the travel planning graph
class TravelPlanState(TypedDict):
    destination: str
    duration: int
    interests: str
    start_date: str
    plan: Dict[str, Any]
    error: str
    retry_count: int

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
    # Check if we've reached the maximum number of retries
    if state.get("retry_count", 0) >= 3:
        return {
            **state,
            "error": f"Failed after {state.get('retry_count', 0)} retries. Last error: {state.get('error', 'Unknown error')}"
        }
        
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
            "max_retries": END,        # End if we've reached max retries
            "end": END                 # End if there's no error
        }
    )
    
    # Set the entry point
    workflow.set_entry_point("generate_plan")
    
    return workflow.compile()

def test_travel_plan_graph():
    """Test the travel plan graph."""
    # Create the graph
    travel_plan_graph = create_travel_plan_graph()
    
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
    
    # Execute the graph
    result = travel_plan_graph.invoke(initial_state)
    
    # Print the result
    print("Travel Plan Graph Result:")
    print(json.dumps(result, indent=2))
    
    # Check for errors
    assert not result["error"], f"Error in travel plan: {result['error']}"
    
    # Check that the plan has the expected structure
    assert "days" in result["plan"], "Plan is missing 'days'"
    assert "tips" in result["plan"], "Plan is missing 'tips'"
    
    print("Travel plan graph test passed!")

if __name__ == "__main__":
    test_travel_plan_graph() 