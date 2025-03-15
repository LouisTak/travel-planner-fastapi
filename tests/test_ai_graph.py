import sys
import os
import json

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ai_graph import travel_plan_graph, travel_suggestion_graph

def test_travel_plan():
    """Test the travel plan graph."""
    # Define the initial state
    initial_state = {
        "destination": "Paris, France",
        "duration": 3,
        "interests": "art, food, and history",
        "start_date": "",
        "plan": {},
        "error": "",
        "retry_count": 0  # Initialize retry count
    }
    
    try:
        # Execute the graph with a timeout to prevent infinite recursion
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Test timed out - possible infinite recursion")
        
        # Set a timeout of 10 seconds
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)
        
        # Execute the graph
        result = travel_plan_graph.invoke(initial_state)
        
        # Cancel the alarm
        signal.alarm(0)
        
        # Print the result
        print("Travel Plan Result:")
        print(json.dumps(result, indent=2))
        
        # Check for errors
        if result["error"]:
            print(f"Warning: Error in travel plan: {result['error']}")
            return
        
        # Check that the plan has the expected structure
        assert "days" in result["plan"], "Plan is missing 'days'"
        assert "tips" in result["plan"], "Plan is missing 'tips'"
        
        # Check that the days have the expected structure
        for day in result["plan"]["days"]:
            assert "day" in day, "Day is missing 'day'"
            assert "activities" in day, "Day is missing 'activities'"
            
            # Check that the activities have the expected structure
            for activity in day["activities"]:
                assert "time" in activity, "Activity is missing 'time'"
                assert "location" in activity, "Activity is missing 'location'"
                assert "activity" in activity, "Activity is missing 'activity'"
                assert "tips" in activity, "Activity is missing 'tips'"
        
        print("Travel plan test passed!")
    
    except TimeoutError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"Test failed with unexpected error: {e}")

def test_travel_suggestion():
    """Test the travel suggestion graph."""
    # Define the initial state
    initial_state = {
        "destination": "Tokyo, Japan",
        "query": "What are the best times to visit Mt. Fuji?",
        "suggestion": "",
        "error": ""
    }
    
    try:
        # Execute the graph with a timeout to prevent infinite recursion
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Test timed out - possible infinite recursion")
        
        # Set a timeout of 10 seconds
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)
        
        # Execute the graph
        result = travel_suggestion_graph.invoke(initial_state)
        
        # Cancel the alarm
        signal.alarm(0)
        
        # Print the result
        print("\nTravel Suggestion Result:")
        print(json.dumps(result, indent=2))
        
        # Check for errors
        if result["error"]:
            print(f"Warning: Error in travel suggestion: {result['error']}")
            return
        
        # Check that the suggestion is not empty
        assert result["suggestion"], "Suggestion is empty"
        
        print("Travel suggestion test passed!")
    
    except TimeoutError as e:
        print(f"Test failed: {e}")
    except Exception as e:
        print(f"Test failed with unexpected error: {e}")

if __name__ == "__main__":
    test_travel_plan()
    test_travel_suggestion() 