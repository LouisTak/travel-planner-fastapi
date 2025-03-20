import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json
from sqlalchemy.orm import Session
from unittest.mock import patch
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
        assert data["title"] == mock_travel_plan_response["title"]
        assert data["destination"] == mock_travel_plan_response["destination"]
        assert len(data["days"]) == len(mock_travel_plan_response["days"])
    
    @patch('utils.ai_graph.travel_suggestion_graph.invoke')
    def test_ai_suggest(self, mock_invoke, authenticated_client: TestClient, mock_travel_suggestion_response):
        """Test getting travel suggestions using AI."""
        mock_invoke.return_value = mock_travel_suggestion_response
        
        response = authenticated_client.post(
            "/api/v1/ai/suggest",
            json={
                "destination": "Paris, France",
                "query": "Best cafes in Paris"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["destination"] == mock_travel_suggestion_response["destination"]
        assert data["query"] == mock_travel_suggestion_response["query"]
        assert data["suggestion"] == mock_travel_suggestion_response["suggestion"]
    
    @patch('utils.ai_graph.travel_plan_graph.invoke')
    def test_regenerate_day(self, mock_invoke, authenticated_client: TestClient, mock_travel_plan_response, created_travel_plan):
        """Test regenerating a day in a travel plan using AI."""
        mock_invoke.return_value = mock_travel_plan_response
        
        response = authenticated_client.post(
            "/api/v1/ai/regenerate-day",
            json={
                "travel_plan_id": created_travel_plan["id"],
                "day_number": 1,
                "interests": ["food", "culture"]
            }
        )
        
        # Status code could be 200 OK or 403 Forbidden depending on user role
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        
        if response.status_code == status.HTTP_200_OK:
            data = response.json()
            assert "title" in data
            assert "days" in data
    
    def test_ai_plan_unauthorized(self, client: TestClient):
        """Test generating a travel plan without authentication."""
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
    
    @pytest.mark.parametrize("feature_endpoint", [
        "/api/v1/ai/optimize-plan",
        "/api/v1/ai/personalize"
    ])
    def test_premium_ai_features(self, authenticated_client: TestClient, created_travel_plan, feature_endpoint):
        """Test premium AI features based on user role."""
        response = authenticated_client.post(
            f"{feature_endpoint}",
            json={
                "plan_id": created_travel_plan["id"],
                "preferences": {"style": "luxury", "pace": "relaxed"}
            }
        )
        
        # Depending on user role, either 200 OK or 403 Forbidden
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN] 