import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import HTTPException
from schemas.authentication_schemas import Token

from controllers.authentication_controller import (
    login,
    register,
    refresh_token
)
from schemas.user_schemas import UserCreate, UserResponse

# Test data
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_HASHED_PASSWORD = "hashed_password"
TEST_USER_ID = "test_user_id"
TEST_ACCESS_TOKEN = "test_access_token"
TEST_REFRESH_TOKEN = "test_refresh_token"

@pytest.fixture
def user_create():
    return UserCreate(
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
        firstname="Test",
        lastname="User"
    )

@pytest.fixture
def mock_user():
    user = MagicMock()
    user.id = TEST_USER_ID
    user.email = TEST_EMAIL
    user.hashed_password = TEST_HASHED_PASSWORD
    user.firstname = "Test"
    user.lastname = "User"
    user.role = "user"
    return user

@pytest.mark.asyncio
@patch("controllers.authentication_controller.get_user_by_email")
@patch("controllers.authentication_controller.verify_password")
@patch("controllers.authentication_controller.create_access_token")
@patch("controllers.authentication_controller.create_refresh_token")
async def test_login_success(mock_create_refresh, mock_create_access, 
                             mock_verify, mock_get_user, mock_user):
    """Test successful login."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_verify.return_value = True
    mock_create_access.return_value = TEST_ACCESS_TOKEN
    mock_create_refresh.return_value = TEST_REFRESH_TOKEN
    
    # Execute
    result = await login(TEST_EMAIL, TEST_PASSWORD)
    
    # Assert
    assert isinstance(result, Token)
    assert result.access_token == TEST_ACCESS_TOKEN
    assert result.refresh_token == TEST_REFRESH_TOKEN
    mock_get_user.assert_called_once_with(TEST_EMAIL)
    mock_verify.assert_called_once_with(TEST_PASSWORD, TEST_HASHED_PASSWORD)
    mock_create_access.assert_called_once()
    mock_create_refresh.assert_called_once()

@pytest.mark.asyncio
@patch("controllers.authentication_controller.get_user_by_email")
async def test_login_user_not_found(mock_get_user):
    """Test login with non-existent user."""
    # Setup
    mock_get_user.return_value = None
    
    # Execute & Assert
    with pytest.raises(HTTPException) as exc_info:
        await login(TEST_EMAIL, TEST_PASSWORD)
    
    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail

@pytest.mark.asyncio
@patch("controllers.authentication_controller.get_user_by_email")
@patch("controllers.authentication_controller.verify_password")
async def test_login_invalid_password(mock_verify, mock_get_user, mock_user):
    """Test login with invalid password."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_verify.return_value = False
    
    # Execute & Assert
    with pytest.raises(HTTPException) as exc_info:
        await login(TEST_EMAIL, TEST_PASSWORD)
    
    assert exc_info.value.status_code == 401
    assert "Invalid credentials" in exc_info.value.detail

@pytest.mark.asyncio
@patch("controllers.authentication_controller.get_user_by_email")
@patch("controllers.authentication_controller.hash_password")
@patch("controllers.authentication_controller.create_user")
@patch("controllers.authentication_controller.create_access_token")
@patch("controllers.authentication_controller.create_refresh_token")
async def test_register_success(mock_create_refresh, mock_create_access, 
                                mock_create_user, mock_hash, mock_get_user, 
                                user_create, mock_user):
    """Test successful user registration."""
    # Setup
    mock_get_user.return_value = None  # User doesn't exist yet
    mock_hash.return_value = TEST_HASHED_PASSWORD
    mock_create_user.return_value = mock_user
    mock_create_access.return_value = TEST_ACCESS_TOKEN
    mock_create_refresh.return_value = TEST_REFRESH_TOKEN
    
    # Execute
    result = await register(user_create)
    
    # Assert
    assert isinstance(result, dict)
    assert "user" in result
    assert "tokens" in result
    assert result["tokens"].access_token == TEST_ACCESS_TOKEN
    assert result["tokens"].refresh_token == TEST_REFRESH_TOKEN
    mock_get_user.assert_called_once_with(TEST_EMAIL)
    mock_hash.assert_called_once_with(TEST_PASSWORD)
    mock_create_user.assert_called_once()
    mock_create_access.assert_called_once()
    mock_create_refresh.assert_called_once()

@pytest.mark.asyncio
@patch("controllers.authentication_controller.get_user_by_email")
async def test_register_email_exists(mock_get_user, user_create, mock_user):
    """Test registration with existing email."""
    # Setup
    mock_get_user.return_value = mock_user  # User already exists
    
    # Execute & Assert
    with pytest.raises(HTTPException) as exc_info:
        await register(user_create)
    
    assert exc_info.value.status_code == 400
    assert "Email already registered" in exc_info.value.detail

@pytest.mark.asyncio
@patch("controllers.authentication_controller.jwt.decode")
@patch("controllers.authentication_controller.create_access_token")
@patch("controllers.authentication_controller.create_refresh_token")
async def test_refresh_token_success(mock_create_refresh, mock_create_access, mock_jwt_decode):
    """Test successful token refresh."""
    # Setup
    token = "valid_refresh_token"
    payload = {"sub": TEST_EMAIL, "user_id": TEST_USER_ID}
    mock_jwt_decode.return_value = payload
    mock_create_access.return_value = "new_access_token"
    mock_create_refresh.return_value = "new_refresh_token"
    
    # Execute
    result = await refresh_token(token)
    
    # Assert
    assert isinstance(result, Token)
    assert result.access_token == "new_access_token"
    assert result.refresh_token == "new_refresh_token"
    mock_create_access.assert_called_once_with(payload)
    mock_create_refresh.assert_called_once_with(payload)

@pytest.mark.asyncio
@patch("controllers.authentication_controller.jwt.decode")
async def test_refresh_token_invalid(mock_jwt_decode):
    """Test refresh with invalid token."""
    # Setup
    token = "invalid_refresh_token"
    mock_jwt_decode.side_effect = Exception("Invalid token")
    
    # Execute & Assert
    with pytest.raises(HTTPException) as exc_info:
        await refresh_token(token)
    
    assert exc_info.value.status_code == 401
    assert "Invalid refresh token" in exc_info.value.detail 