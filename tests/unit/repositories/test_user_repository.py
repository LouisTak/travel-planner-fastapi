import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from repositories.user_repository import (
    get_user_by_email,
    get_user_by_id,
    create_user,
    update_user
)
from models.user import User
from models.user_role import UserRole
from schemas.user_schemas import UserCreate, UserUpdate
from fastapi import HTTPException

# Test constants
TEST_USER_ID = "123e4567-e89b-12d3-a456-426614174000"  # UUID format
TEST_EMAIL = "test@example.com"
TEST_USERNAME = "testuser"
TEST_NICKNAME = "Test User"
TEST_HASHED_PASSWORD = "hashed_password"
TEST_ROLE = UserRole.FREE.value

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
    user.username = TEST_USERNAME
    user.nickname = TEST_NICKNAME
    user.hashed_password = TEST_HASHED_PASSWORD
    user.role = TEST_ROLE
    return user

@pytest.fixture
def user_create():
    """Create a user creation model."""
    return UserCreate(
        email=TEST_EMAIL,
        username=TEST_USERNAME,
        nickname=TEST_NICKNAME,
        password="password"  # This would be hashed before storage
    )

@pytest.fixture
def user_update():
    """Create a user update model."""
    return UserUpdate(
        email=None,
        nickname="Updated Nickname"
    )

def test_get_user_by_email_found(mock_db, mock_user):
    """Test retrieving a user by email when the user exists."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Execute
    result = get_user_by_email(mock_user.email)
    
    # Assert
    assert result == mock_user
    mock_db.query.assert_called_once_with(User)
    mock_db.query.return_value.filter.assert_called_once()

def test_get_user_by_email_not_found(mock_db):
    """Test retrieving a user by email when the user doesn't exist."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Execute
    result = get_user_by_email(TEST_EMAIL)
    
    # Assert
    assert result is None
    mock_db.query.assert_called_once_with(User)
    mock_db.query.return_value.filter.assert_called_once()

def test_get_user_by_id_found(mock_db, mock_user):
    """Test retrieving a user by ID when the user exists."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    # Execute
    result = get_user_by_id(TEST_USER_ID)
    
    # Assert
    assert result == mock_user
    mock_db.query.assert_called_once_with(User)
    mock_db.query.return_value.filter.assert_called_once()

def test_get_user_by_id_not_found(mock_db):
    """Test retrieving a user by ID when the user doesn't exist."""
    # Setup
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Execute
    result = get_user_by_id(TEST_USER_ID)
    
    # Assert
    assert result is None
    mock_db.query.assert_called_once_with(User)
    mock_db.query.return_value.filter.assert_called_once()

@patch("repositories.user_repository.User")
def test_create_user_success(mock_user_class, mock_db, user_create):
    """Test successful user creation."""
    # Setup
    new_user = MagicMock()
    mock_user_class.return_value = new_user
    
    # Execute
    with patch('repositories.user_repository.pwd_context.hash') as mock_hash:
        mock_hash.return_value = TEST_HASHED_PASSWORD
        result = create_user(user_create)
    
    # Assert
    assert result == new_user
    mock_user_class.assert_called_once()
    mock_db.add.assert_called_once_with(new_user)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(new_user)

@patch("repositories.user_repository.User")
def test_create_user_error(mock_user_class, mock_db, user_create):
    """Test user creation with database error."""
    # Setup
    new_user = MagicMock()
    mock_user_class.return_value = new_user
    mock_db.commit.side_effect = SQLAlchemyError("Database error")
    
    # Execute & Assert
    with pytest.raises(SQLAlchemyError):
        with patch('repositories.user_repository.pwd_context.hash') as mock_hash:
            mock_hash.return_value = TEST_HASHED_PASSWORD
            create_user(user_create)
    
    mock_db.add.assert_called_once_with(new_user)
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_not_called()

def test_update_user_success(mock_db, mock_user, user_update):
    """Test successful user update."""
    # Setup
    
    # Execute
    with patch('repositories.user_repository.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = mock_user
        result = update_user(user_update, TEST_USER_ID)
    
    # Assert
    assert result == mock_user
    assert mock_user.nickname == "Updated Nickname"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once_with(mock_user)

def test_update_user_not_found(mock_db, user_update):
    """Test updating a non-existent user."""
    # Setup
    
    # Execute
    with patch('repositories.user_repository.get_user_by_id') as mock_get_user:
        mock_get_user.return_value = None
        with pytest.raises(HTTPException) as excinfo:
            update_user(user_update, TEST_USER_ID)
    
    # Assert
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "User not found"
    mock_db.commit.assert_not_called()
    mock_db.refresh.assert_not_called() 