import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any

from config import settings
from models.user import User
from models.travel_plan import TravelPlan
from models.travel_plan_day import TravelPlanDay
from models.activity import Activity

# Test constants
TEST_USER_ID = "test_user_id"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_HASHED_PASSWORD = "hashed_password"
TEST_FIRSTNAME = "Test"
TEST_LASTNAME = "User"
TEST_ROLE = "user"

TEST_PLAN_ID = "123e4567-e89b-12d3-a456-426614174000"
TEST_DAY_ID = "123e4567-e89b-12d3-a456-426614174001"
TEST_ACTIVITY_ID = "123e4567-e89b-12d3-a456-426614174002"

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock(spec=Session)
    return db

@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = MagicMock(spec=User)
    user.id = TEST_USER_ID
    user.email = TEST_EMAIL
    user.hashed_password = TEST_HASHED_PASSWORD
    user.firstname = TEST_FIRSTNAME
    user.lastname = TEST_LASTNAME
    user.role = TEST_ROLE
    return user

@pytest.fixture
def mock_travel_plan():
    """Create a mock travel plan."""
    plan = MagicMock(spec=TravelPlan)
    plan.id = TEST_PLAN_ID
    plan.user_id = TEST_USER_ID
    plan.title = "Test Trip"
    plan.destination = "Test Destination"
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
    day.description = "Test Day Description"
    day.reminder = "Test Reminder"
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
def user_data() -> Dict[str, Any]:
    """Return user data for token creation."""
    return {
        "sub": TEST_EMAIL,
        "user_id": TEST_USER_ID,
        "role": TEST_ROLE
    }

@pytest.fixture
def auth_token(user_data):
    """Create an authentication token for testing."""
    payload = user_data.copy()
    payload["exp"] = (datetime.utcnow() + timedelta(minutes=30)).timestamp()
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

@pytest.fixture
def auth_headers(auth_token):
    """Create authentication headers."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def admin_user_data() -> Dict[str, Any]:
    """Return admin user data for token creation."""
    return {
        "sub": "admin@example.com",
        "user_id": "admin_user_id",
        "role": "admin"
    }

@pytest.fixture
def admin_token(admin_user_data):
    """Create an admin authentication token for testing."""
    payload = admin_user_data.copy()
    payload["exp"] = (datetime.utcnow() + timedelta(minutes=30)).timestamp()
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

@pytest.fixture
def admin_headers(admin_token):
    """Create admin authentication headers."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture
def expired_token(user_data):
    """Create an expired authentication token for testing."""
    payload = user_data.copy()
    payload["exp"] = (datetime.utcnow() - timedelta(minutes=30)).timestamp()
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

@pytest.fixture
def expired_headers(expired_token):
    """Create expired authentication headers."""
    return {"Authorization": f"Bearer {expired_token}"}

@pytest.fixture
def invalid_token():
    """Create an invalid authentication token for testing."""
    return "invalid.token.format"

@pytest.fixture
def invalid_headers(invalid_token):
    """Create invalid authentication headers."""
    return {"Authorization": f"Bearer {invalid_token}"} 