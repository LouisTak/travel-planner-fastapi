import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from uuid import UUID

from repositories.travel_plan_repository import (
    get_travel_plan_by_id,
    get_travel_plans_by_user_id,
    get_travel_plan_days,
    get_activities_by_day_id,
    delete_travel_plan,
    create_travel_plan
)
from models.travel_plan import TravelPlan
from models.travel_plan_day import TravelPlanDay
from models.activity import Activity
from schemas.ai_schemas import TravelPlanDBCreate

# Test constants
TEST_PLAN_ID = "123e4567-e89b-12d3-a456-426614174000"
TEST_USER_ID = "user123"
TEST_DAY_ID = "123e4567-e89b-12d3-a456-426614174001"
TEST_ACTIVITY_ID = "123e4567-e89b-12d3-a456-426614174002"

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    db = MagicMock(spec=Session)
    return db

@pytest.fixture
def mock_travel_plan():
    """Create a mock travel plan."""
    plan = MagicMock(spec=TravelPlan)
    plan.id = TEST_PLAN_ID
    plan.user_id = TEST_USER_ID
    plan.title = "Test Trip"
    plan.destination = "Test Destination"
    plan.start_at = datetime.now()
    plan.end_at = datetime.now()
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
def travel_plan_create():
    """Create a travel plan creation object."""
    return TravelPlanDBCreate(
        title="Test Trip",
        destination="Test Destination",
        start_at=datetime.now().date(),
        end_at=datetime.now().date(),
        remarks="Test Remarks",
        days=[
            {
                "day_number": 1,
                "description": "Test Day 1",
                "reminder": "Test Reminder 1",
                "activities": [
                    {
                        "location": "Test Location 1",
                        "activity": "Test Activity 1",
                        "tips": "Test Tips 1",
                        "start_at": "09:00",
                        "end_at": "11:00"
                    }
                ]
            }
        ]
    )

@pytest.mark.asyncio
async def test_get_travel_plan_by_id_found(mock_db, mock_travel_plan):
    """Test retrieving a travel plan by ID when it exists."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_travel_plan
    
    # Execute
    result = await get_travel_plan_by_id(TEST_PLAN_ID)
    
    # Assert
    assert result == mock_travel_plan
    mock_db.query.assert_called_once_with(TravelPlan)
    mock_db.query.return_value.filter.assert_called_once()

@pytest.mark.asyncio
async def test_get_travel_plan_by_id_not_found(mock_db):
    """Test retrieving a travel plan by ID when it doesn't exist."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Execute
    result = await get_travel_plan_by_id(TEST_PLAN_ID)
    
    # Assert
    assert result is None
    mock_db.query.assert_called_once_with(TravelPlan)
    mock_db.query.return_value.filter.assert_called_once()

@pytest.mark.asyncio
async def test_get_travel_plans_by_user_id(mock_db, mock_travel_plan):
    """Test retrieving all travel plans for a user."""
    # Setup
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_travel_plan]
    
    # Execute
    result = await get_travel_plans_by_user_id(TEST_USER_ID)
    
    # Assert
    assert len(result) == 1
    assert result[0] == mock_travel_plan
    mock_db.query.assert_called_once_with(TravelPlan)
    mock_db.query.return_value.filter.assert_called_once()
    mock_db.query.return_value.filter.return_value.all.assert_called_once()

@pytest.mark.asyncio
async def test_get_travel_plan_days(mock_db, mock_travel_plan_day):
    """Test retrieving days for a travel plan."""
    # Setup
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_travel_plan_day]
    
    # Execute
    result = await get_travel_plan_days(TEST_PLAN_ID)
    
    # Assert
    assert len(result) == 1
    assert result[0] == mock_travel_plan_day
    mock_db.query.assert_called_once_with(TravelPlanDay)
    mock_db.query.return_value.filter.assert_called_once()
    mock_db.query.return_value.filter.return_value.order_by.assert_called_once()
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.assert_called_once()

@pytest.mark.asyncio
async def test_get_activities_by_day_id(mock_db, mock_activity):
    """Test retrieving activities for a day."""
    # Setup
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [mock_activity]
    
    # Execute
    result = await get_activities_by_day_id(TEST_DAY_ID)
    
    # Assert
    assert len(result) == 1
    assert result[0] == mock_activity
    mock_db.query.assert_called_once_with(Activity)
    mock_db.query.return_value.filter.assert_called_once()
    mock_db.query.return_value.filter.return_value.order_by.assert_called_once()
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.assert_called_once()

@pytest.mark.asyncio
async def test_delete_travel_plan_success(mock_db, mock_travel_plan):
    """Test successful travel plan deletion."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_travel_plan
    
    # Execute
    result = await delete_travel_plan(TEST_PLAN_ID)
    
    # Assert
    assert result == mock_travel_plan
    mock_db.query.assert_called_with(TravelPlan)
    mock_db.delete.assert_called_once_with(mock_travel_plan)
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_travel_plan_not_found(mock_db):
    """Test deleting a non-existent travel plan."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Execute
    result = await delete_travel_plan(TEST_PLAN_ID)
    
    # Assert
    assert result is None
    mock_db.delete.assert_not_called()
    mock_db.commit.assert_not_called()

@pytest.mark.asyncio
@patch("repositories.travel_plan_repository.TravelPlan")
@patch("repositories.travel_plan_repository.TravelPlanDay")
@patch("repositories.travel_plan_repository.Activity")
async def test_create_travel_plan_success(mock_activity_class, mock_day_class, 
                                    mock_plan_class, mock_db, travel_plan_create):
    """Test successful travel plan creation."""
    # Setup
    mock_plan = MagicMock()
    mock_plan.id = TEST_PLAN_ID
    mock_plan_class.return_value = mock_plan
    
    mock_day = MagicMock()
    mock_day.id = TEST_DAY_ID
    mock_day_class.return_value = mock_day
    
    mock_activity = MagicMock()
    mock_activity.id = TEST_ACTIVITY_ID
    mock_activity_class.return_value = mock_activity
    
    # Execute
    result = await create_travel_plan(travel_plan_create, TEST_USER_ID)
    
    # Assert
    assert result["id"] == mock_plan.id
    assert result["title"] == travel_plan_create.title
    assert result["destination"] == travel_plan_create.destination
    mock_plan_class.assert_called_once()
    mock_day_class.assert_called_once()
    mock_activity_class.assert_called_once()
    assert mock_db.add.call_count == 3  # Plan, day, and activity
    mock_db.commit.assert_called_once()
    assert mock_db.refresh.call_count == 3  # Plan, day, and activity

@pytest.mark.asyncio
@patch("repositories.travel_plan_repository.TravelPlan")
async def test_create_travel_plan_error(mock_plan_class, mock_db, travel_plan_create):
    """Test travel plan creation with database error."""
    # Setup
    mock_plan = MagicMock()
    mock_plan_class.return_value = mock_plan
    mock_db.commit.side_effect = SQLAlchemyError("Database error")
    
    # Execute & Assert
    with pytest.raises(SQLAlchemyError):
        await create_travel_plan(travel_plan_create, TEST_USER_ID)
    
    mock_plan_class.assert_called_once()
    mock_db.add.assert_called_once_with(mock_plan)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_not_called() 