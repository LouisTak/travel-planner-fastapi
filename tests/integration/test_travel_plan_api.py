import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

from main import app
from config import settings
from models.user import User
from models.travel_plan import TravelPlan
from models.travel_plan_day import TravelPlanDay
from models.activity import Activity

# Test client
client = TestClient(app)

# Test constants
TEST_USER_ID = "test_user_id"
TEST_EMAIL = "test@example.com"
TEST_PLAN_ID = "123e4567-e89b-12d3-a456-426614174000"
TEST_DAY_ID = "123e4567-e89b-12d3-a456-426614174001"
TEST_ACTIVITY_ID = "123e4567-e89b-12d3-a456-426614174002"

@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = MagicMock(spec=User)
    user.id = TEST_USER_ID
    user.email = TEST_EMAIL
    user.role = "user"
    return user

@pytest.fixture
def mock_travel_plan():
    """Create a mock travel plan."""
    plan = MagicMock(spec=TravelPlan)
    plan.id = TEST_PLAN_ID
    plan.title = "Test Trip"
    plan.destination = "Test Destination"
    plan.user_id = TEST_USER_ID
    plan.start_at = datetime.now().date()
    plan.end_at = datetime.now().date()
    plan.created_at = datetime.now()
    plan.updated_at = datetime.now()
    return plan

@pytest.fixture
def mock_travel_plan_day():
    """Create a mock travel plan day."""
    day = MagicMock(spec=TravelPlanDay)
    day.id = TEST_DAY_ID
    day.travel_plan_id = TEST_PLAN_ID
    day.day_number = 1
    day.description = "Day 1 Description"
    day.reminder = "Day 1 Reminder"
    return day

@pytest.fixture
def mock_activity():
    """Create a mock activity."""
    activity = MagicMock(spec=Activity)
    activity.id = TEST_ACTIVITY_ID
    activity.day_id = TEST_DAY_ID
    activity.location = "Test Location"
    activity.activity = "Test Activity"
    activity.tips = "Test Tips"
    activity.start_at = datetime.now().time()
    activity.end_at = datetime.now().time()
    return activity

@pytest.fixture
def auth_token():
    """Create an authentication token for testing."""
    payload = {
        "sub": TEST_EMAIL,
        "exp": (datetime.utcnow() + timedelta(minutes=30)).timestamp(),
        "user_id": TEST_USER_ID,
        "role": "user"
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

@pytest.fixture
def auth_headers(auth_token):
    """Create authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}

@patch("controllers.travel_plan_controller.get_current_user")
@patch("controllers.travel_plan_controller.get_travel_plans_by_user_id")
def test_get_user_travel_plans(mock_get_plans, mock_get_user, mock_user, 
                              mock_travel_plan, auth_headers):
    """Test retrieving all travel plans for a user."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_get_plans.return_value = [mock_travel_plan]
    
    # Execute
    response = client.get(
        "/api/v1/travel-plans",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["id"] == TEST_PLAN_ID
    assert data["data"][0]["title"] == mock_travel_plan.title
    mock_get_user.assert_called_once()
    mock_get_plans.assert_called_once_with(TEST_USER_ID)

@patch("controllers.travel_plan_controller.get_current_user")
@patch("controllers.travel_plan_controller.create_travel_plan")
def test_create_travel_plan(mock_create_plan, mock_get_user, mock_user, auth_headers):
    """Test creating a new travel plan."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_create_plan.return_value = {
        "id": TEST_PLAN_ID,
        "title": "New Trip",
        "destination": "New Destination",
        "start_at": datetime.now().date().isoformat(),
        "end_at": datetime.now().date().isoformat()
    }
    
    # Execute
    response = client.post(
        "/api/v1/travel-plans",
        headers=auth_headers,
        json={
            "title": "New Trip",
            "destination": "New Destination",
            "start_at": datetime.now().date().isoformat(),
            "end_at": datetime.now().date().isoformat(),
            "remarks": "Test remarks",
            "days": [
                {
                    "day_number": 1,
                    "description": "Day 1",
                    "reminder": "Reminder 1",
                    "activities": [
                        {
                            "location": "Location 1",
                            "activity": "Activity 1",
                            "tips": "Tips 1",
                            "start_at": "09:00",
                            "end_at": "12:00"
                        }
                    ]
                }
            ]
        }
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == TEST_PLAN_ID
    assert data["data"]["title"] == "New Trip"
    mock_get_user.assert_called_once()
    mock_create_plan.assert_called_once()

@patch("controllers.travel_plan_controller.get_current_user")
@patch("controllers.travel_plan_controller.get_travel_plan_by_id")
@patch("controllers.travel_plan_controller.get_travel_plan_days")
@patch("controllers.travel_plan_controller.get_activities_by_day_id")
def test_get_travel_plan_details(mock_get_activities, mock_get_days, 
                               mock_get_plan, mock_get_user, mock_user, 
                               mock_travel_plan, mock_travel_plan_day, 
                               mock_activity, auth_headers):
    """Test retrieving details of a specific travel plan."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_get_plan.return_value = mock_travel_plan
    mock_get_days.return_value = [mock_travel_plan_day]
    mock_get_activities.return_value = [mock_activity]
    
    # Execute
    response = client.get(
        f"/api/v1/travel-plans/{TEST_PLAN_ID}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["id"] == TEST_PLAN_ID
    assert data["data"]["title"] == mock_travel_plan.title
    assert "days" in data["data"]
    assert len(data["data"]["days"]) == 1
    assert data["data"]["days"][0]["id"] == TEST_DAY_ID
    assert "activities" in data["data"]["days"][0]
    assert len(data["data"]["days"][0]["activities"]) == 1
    assert data["data"]["days"][0]["activities"][0]["id"] == TEST_ACTIVITY_ID
    mock_get_user.assert_called_once()
    mock_get_plan.assert_called_once_with(TEST_PLAN_ID)
    mock_get_days.assert_called_once_with(TEST_PLAN_ID)
    mock_get_activities.assert_called_once_with(TEST_DAY_ID)

@patch("controllers.travel_plan_controller.get_current_user")
@patch("controllers.travel_plan_controller.get_travel_plan_by_id")
def test_get_travel_plan_not_found(mock_get_plan, mock_get_user, 
                                 mock_user, auth_headers):
    """Test retrieving a non-existent travel plan."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_get_plan.return_value = None
    
    # Execute
    response = client.get(
        f"/api/v1/travel-plans/{TEST_PLAN_ID}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Travel plan not found" in data["detail"]
    mock_get_user.assert_called_once()
    mock_get_plan.assert_called_once_with(TEST_PLAN_ID)

@patch("controllers.travel_plan_controller.get_current_user")
@patch("controllers.travel_plan_controller.get_travel_plan_by_id")
def test_get_travel_plan_forbidden(mock_get_plan, mock_get_user, 
                                 mock_user, mock_travel_plan, auth_headers):
    """Test retrieving a travel plan that belongs to another user."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_travel_plan.user_id = "another_user_id"  # Different user
    mock_get_plan.return_value = mock_travel_plan
    
    # Execute
    response = client.get(
        f"/api/v1/travel-plans/{TEST_PLAN_ID}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 403
    data = response.json()
    assert "detail" in data
    assert "don't have permission" in data["detail"]
    mock_get_user.assert_called_once()
    mock_get_plan.assert_called_once_with(TEST_PLAN_ID)

@patch("controllers.travel_plan_controller.get_current_user")
@patch("controllers.travel_plan_controller.get_travel_plan_by_id")
@patch("controllers.travel_plan_controller.delete_travel_plan")
def test_delete_travel_plan(mock_delete_plan, mock_get_plan, mock_get_user, 
                          mock_user, mock_travel_plan, auth_headers):
    """Test deleting a travel plan."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_get_plan.return_value = mock_travel_plan
    mock_delete_plan.return_value = mock_travel_plan
    
    # Execute
    response = client.delete(
        f"/api/v1/travel-plans/{TEST_PLAN_ID}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 204
    mock_get_user.assert_called_once()
    mock_get_plan.assert_called_once_with(TEST_PLAN_ID)
    mock_delete_plan.assert_called_once_with(TEST_PLAN_ID)

@patch("controllers.travel_plan_controller.get_current_user")
@patch("controllers.travel_plan_controller.get_travel_plan_by_id")
def test_delete_travel_plan_not_found(mock_get_plan, mock_get_user, 
                                    mock_user, auth_headers):
    """Test deleting a non-existent travel plan."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_get_plan.return_value = None
    
    # Execute
    response = client.delete(
        f"/api/v1/travel-plans/{TEST_PLAN_ID}",
        headers=auth_headers
    )
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Travel plan not found" in data["detail"]
    mock_get_user.assert_called_once()
    mock_get_plan.assert_called_once_with(TEST_PLAN_ID) 