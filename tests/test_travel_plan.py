import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
import uuid

class TestTravelPlanController:
    @pytest.fixture
    def travel_plan_data(self):
        """Fixture for travel plan test data."""
        return {
            "title": "Paris Trip",
            "destination": "Paris, France",
            "description": "A test trip to Paris",
            "start_date": str(date(2025, 4, 19)),
            "end_date": str(date(2025, 4, 26)),
            "interests": ["art", "food", "history"]
        }
    
    @pytest.fixture
    def created_travel_plan(self, authenticated_client: TestClient, travel_plan_data, test_db):
        """Fixture to create a travel plan and return its data."""
        response = authenticated_client.post("/api/v1/travel-plans", json=travel_plan_data)
        return response.json()
    
    @pytest.mark.skip(reason="Travel plan endpoints not implemented yet")
    def test_create_travel_plan(self, authenticated_client: TestClient, travel_plan_data):
        """Test creating a new travel plan."""
        response = authenticated_client.post("/api/v1/travel-plans", json=travel_plan_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["title"] == travel_plan_data["title"]
        assert data["destination"] == travel_plan_data["destination"]
        
    @pytest.mark.skip(reason="Travel plan endpoints not implemented yet")
    def test_create_travel_plan_unauthorized(self, client: TestClient, travel_plan_data):
        """Test creating a travel plan without authentication."""
        response = client.post("/api/v1/travel-plans", json=travel_plan_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.skip(reason="Travel plan endpoints not implemented yet")
    def test_get_user_travel_plans(self, authenticated_client: TestClient, created_travel_plan):
        """Test retrieving all travel plans for a user."""
        response = authenticated_client.get("/api/v1/travel-plans")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    @pytest.mark.skip(reason="Travel plan endpoints not implemented yet")
    def test_get_travel_plan_details(self, authenticated_client: TestClient, created_travel_plan):
        """Test retrieving details of a specific travel plan."""
        response = authenticated_client.get(f"/api/v1/travel-plans/{created_travel_plan['id']}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created_travel_plan["id"]
        assert data["title"] == created_travel_plan["title"]
    
    @pytest.mark.skip(reason="Travel plan endpoints not implemented yet")
    def test_get_travel_plan_details_not_found(self, authenticated_client: TestClient):
        """Test retrieving a non-existent travel plan."""
        non_existent_id = str(uuid.uuid4())
        response = authenticated_client.get(f"/api/v1/travel-plans/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.skip(reason="Travel plan endpoints not implemented yet")
    def test_delete_travel_plan(self, authenticated_client: TestClient, created_travel_plan):
        """Test deleting a travel plan."""
        response = authenticated_client.delete(f"/api/v1/travel-plans/{created_travel_plan['id']}")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify plan is deleted
        response = authenticated_client.get(f"/api/v1/travel-plans/{created_travel_plan['id']}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.skip(reason="Travel plan endpoints not implemented yet")
    def test_delete_travel_plan_not_found(self, authenticated_client: TestClient):
        """Test deleting a non-existent travel plan."""
        non_existent_id = str(uuid.uuid4())
        response = authenticated_client.delete(f"/api/v1/travel-plans/{non_existent_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.skip(reason="Travel plan endpoints not implemented yet")
    def test_export_travel_plan(self, authenticated_client: TestClient, created_travel_plan):
        """Test exporting a travel plan (premium feature)."""
        response = authenticated_client.post(f"/api/v1/travel-plans/{created_travel_plan['id']}/export")
        
        # Status depends on user role
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]
        
        if response.status_code == status.HTTP_200_OK:
            # This should be a PDF or similar export
            assert "Content-Disposition" in response.headers
            assert "attachment" in response.headers["Content-Disposition"]
    
    @pytest.mark.skip(reason="Admin endpoints not implemented yet")
    def test_travel_plan_stats_as_admin(self, admin_client: TestClient, created_travel_plan):
        """Test getting travel plan stats as admin."""
        response = admin_client.get("/api/v1/admin/travel-plans/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_plans" in data
        assert "plans_per_user" in data
    
    @pytest.mark.skip(reason="Admin endpoints not implemented yet")
    def test_travel_plan_stats_as_non_admin(self, authenticated_client: TestClient):
        """Test getting travel plan stats as non-admin user."""
        response = authenticated_client.get("/api/v1/admin/travel-plans/stats")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN 