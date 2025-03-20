import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import uuid

# Mock the AI graph responses
@pytest.fixture
def mock_travel_plan_response():
    return {
        "title": "Wonderful Paris Trip",
        "destination": "Paris, France",
        "remarks": "A beautiful journey through the city of lights",
        "days": [
            {
                "day_number": 1,
                "description": "Exploring central Paris",
                "reminder": "Bring comfortable walking shoes",
                "activities": [
                    {
                        "location": "Eiffel Tower",
                        "activity": "Visit the iconic Eiffel Tower",
                        "tips": "Go early to avoid crowds",
                        "start_at": "09:00",
                        "end_at": "11:00"
                    },
                    {
                        "location": "Louvre Museum",
                        "activity": "Explore world-famous art",
                        "tips": "Don't miss the Mona Lisa",
                        "start_at": "13:00",
                        "end_at": "16:00"
                    }
                ]
            }
        ],
        "tips": ["Learn basic French phrases", "Use the metro for transportation"]
    }

@pytest.fixture
def mock_travel_suggestion_response():
    return {
        "destination": "Paris, France",
        "query": "Best cafes in Paris",
        "suggestion": "Paris is famous for its cafe culture. Some of the best cafes include Cafe de Flore, Les Deux Magots, and Angelina. These historic establishments offer excellent coffee, pastries, and a quintessential Parisian atmosphere."
    }

class TestAIController:
    
    @patch('utils.ai_graph.travel_plan_graph.invoke')
    def test_ai_plan(self, mock_invoke, authenticated_client: TestClient, mock_travel_plan_response):
        """Test generating a travel plan using AI."""
        mock_invoke.return_value = mock_travel_plan_response
        
        # Skip this test because the endpoint is not implemented yet
        pytest.skip("AI Plan endpoint not implemented yet")
        
        response = authenticated_client.post(
            "/api/v1/ai/plan",
            json={
                "destination": "Paris, France",
                "duration": 7,
                "interests": ["art", "history", "food"],
                "start_date": "2024-07-01"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Basic validation of response structure
        assert "days" in data
        assert isinstance(data["days"], list)
        assert len(data["days"]) == 7  # 7 days as requested
        
        for day in data["days"]:
            assert "day_number" in day
            assert "activities" in day
            assert isinstance(day["activities"], list)
            
            for activity in day["activities"]:
                assert "location" in activity
                assert "activity" in activity
                assert "start_at" in activity
                assert "end_at" in activity
        
        # Verify that our mock was called correctly
        mock_invoke.assert_called_once()
    
    @patch('utils.ai_graph.travel_suggestion_graph.invoke')
    def test_ai_suggest(self, mock_invoke, authenticated_client: TestClient, mock_travel_suggestion_response):
        """Test getting travel suggestions using AI."""
        mock_invoke.return_value = mock_travel_suggestion_response
        
        # Skip this test because the endpoint is not implemented yet
        pytest.skip("AI Suggest endpoint not implemented yet")
        
        response = authenticated_client.post(
            "/api/v1/ai/suggest",
            json={
                "destination": "Paris, France",
                "query": "Best cafes in Paris"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Basic validation of response structure
        assert "suggestion" in data
        assert data["destination"] == "Paris, France"
        assert data["query"] == "Best cafes in Paris"
        
        # Verify that our mock was called correctly
        mock_invoke.assert_called_once()
    
    @pytest.mark.skip(reason="Missing created_travel_plan fixture")
    @patch('utils.ai_graph.travel_plan_graph.invoke')
    def test_regenerate_day(self, mock_invoke, authenticated_client: TestClient, mock_travel_plan_response, created_travel_plan):
        """Test regenerating a specific day in a travel plan."""
        # Configure mock response
        mock_invoke.return_value = {"days": [mock_travel_plan_response["days"][0]]}
        
        response = authenticated_client.post(
            f"/api/v1/travel-plans/{created_travel_plan['id']}/regenerate-day",
            json={
                "day_number": 1,
                "interests": ["shopping", "nightlife"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Basic validation of response structure
        assert "day" in data
        assert "day_number" in data["day"]
        assert data["day"]["day_number"] == 1
        assert "activities" in data["day"]
        
        # Verify that our mock was called correctly
        mock_invoke.assert_called_once()
    
    def test_ai_plan_unauthorized(self, client: TestClient):
        """Test generating a travel plan without authentication."""
        # Skip this test because the endpoint is not implemented yet
        pytest.skip("AI Plan endpoint not implemented yet")
        
        response = client.post(
            "/api/v1/ai/plan",
            json={
                "destination": "Paris, France",
                "duration": 7,
                "interests": ["art", "history", "food"],
                "start_date": "2024-07-01"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.skip(reason="Missing created_travel_plan fixture")
    @pytest.mark.parametrize("feature_endpoint", [
        "/api/v1/ai/optimize-plan",
        "/api/v1/ai/personalize"
    ])
    def test_premium_ai_features(self, authenticated_client: TestClient, created_travel_plan, feature_endpoint):
        """Test premium AI features."""
        response = authenticated_client.post(
            f"{feature_endpoint}",
            json={
                "travel_plan_id": created_travel_plan["id"]
            }
        )
        
        # Premium features should be restricted based on role
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "role" in response.json()["detail"].lower() 