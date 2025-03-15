import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to be mocked
import utils.ai_graph
from utils.ai_graph import TravelPlanState, TravelSuggestionState

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

MOCK_TRAVEL_SUGGESTION = "The best time to visit Mt. Fuji is during July and August when the weather is mild and the mountain is usually free of snow."

def mock_generate_travel_plan(state: TravelPlanState) -> TravelPlanState:
    """Mock implementation of generate_travel_plan."""
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

def mock_generate_travel_suggestion(state: TravelSuggestionState) -> TravelSuggestionState:
    """Mock implementation of generate_travel_suggestion."""
    return {
        "destination": state["destination"],
        "query": state["query"],
        "suggestion": MOCK_TRAVEL_SUGGESTION,
        "error": ""
    }

def mock_validate_travel_plan(state: TravelPlanState) -> TravelPlanState:
    """Mock implementation of validate_travel_plan."""
    # Always return the state without errors
    return state

@patch('utils.ai_graph.generate_travel_plan', mock_generate_travel_plan)
@patch('utils.ai_graph.validate_travel_plan', mock_validate_travel_plan)
@patch('utils.ai_graph.generate_travel_suggestion', mock_generate_travel_suggestion)
def test_travel_plan_graph():
    """Test the travel plan graph with mocked functions."""
    # Re-import to get the patched version
    from utils.ai_graph import travel_plan_graph
    
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
    print("Travel Plan Result (Mocked):")
    print(json.dumps(result, indent=2))
    
    # Check for errors
    assert not result["error"], f"Error in travel plan: {result['error']}"
    
    # Check that the plan has the expected structure
    assert "days" in result["plan"], "Plan is missing 'days'"
    assert "tips" in result["plan"], "Plan is missing 'tips'"
    
    print("Travel plan test passed!")

@patch('utils.ai_graph.generate_travel_plan', mock_generate_travel_plan)
@patch('utils.ai_graph.validate_travel_plan', mock_validate_travel_plan)
@patch('utils.ai_graph.generate_travel_suggestion', mock_generate_travel_suggestion)
def test_travel_suggestion_graph():
    """Test the travel suggestion graph with mocked functions."""
    # Re-import to get the patched version
    from utils.ai_graph import travel_suggestion_graph
    
    # Define the initial state
    initial_state = {
        "destination": "Tokyo, Japan",
        "query": "What are the best times to visit Mt. Fuji?",
        "suggestion": "",
        "error": ""
    }
    
    # Execute the graph
    result = travel_suggestion_graph.invoke(initial_state)
    
    # Print the result
    print("\nTravel Suggestion Result (Mocked):")
    print(json.dumps(result, indent=2))
    
    # Check for errors
    assert not result["error"], f"Error in travel suggestion: {result['error']}"
    
    # Check that the suggestion is not empty
    assert result["suggestion"], "Suggestion is empty"
    
    print("Travel suggestion test passed!")

if __name__ == "__main__":
    test_travel_plan_graph()
    test_travel_suggestion_graph() 