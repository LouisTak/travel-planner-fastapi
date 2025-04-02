import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

from main import app
from config import settings
from models.user import User

# Test client
client = TestClient(app)

# Test constants
TEST_USER_ID = "test_user_id"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "TestPassword123!"
TEST_FIRSTNAME = "Test"
TEST_LASTNAME = "User"
TEST_ROLE = "user"

@pytest.fixture
def mock_user():
    """Create a mock user object."""
    user = MagicMock(spec=User)
    user.id = TEST_USER_ID
    user.email = TEST_EMAIL
    user.hashed_password = "hashed_password"
    user.firstname = TEST_FIRSTNAME
    user.lastname = TEST_LASTNAME
    user.role = TEST_ROLE
    return user

@pytest.fixture
def mock_token():
    """Create a mock JWT token."""
    payload = {
        "sub": TEST_EMAIL,
        "user_id": TEST_USER_ID,
        "exp": (datetime.utcnow() + timedelta(minutes=30)).timestamp()
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

@patch("controllers.authentication_controller.get_user_by_email")
@patch("controllers.authentication_controller.verify_password")
@patch("controllers.authentication_controller.create_access_token")
@patch("controllers.authentication_controller.create_refresh_token")
def test_login_success(mock_create_refresh, mock_create_access, 
                      mock_verify, mock_get_user, mock_user):
    """Test successful login."""
    # Setup
    mock_get_user.return_value = mock_user
    mock_verify.return_value = True
    mock_create_access.return_value = "access_token"
    mock_create_refresh.return_value = "refresh_token"
    
    # Execute
    response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] == "access_token"
    assert data["refresh_token"] == "refresh_token"
    mock_get_user.assert_called_once_with(TEST_EMAIL)
    mock_verify.assert_called_once()
    mock_create_access.assert_called_once()
    mock_create_refresh.assert_called_once()

@patch("controllers.authentication_controller.get_user_by_email")
def test_login_invalid_credentials(mock_get_user):
    """Test login with invalid credentials."""
    # Setup
    mock_get_user.return_value = None
    
    # Execute
    response = client.post(
        "/api/v1/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Invalid credentials" in data["detail"]
    mock_get_user.assert_called_once_with(TEST_EMAIL)

@patch("controllers.authentication_controller.get_user_by_email")
@patch("controllers.authentication_controller.hash_password")
@patch("controllers.authentication_controller.create_user")
@patch("controllers.authentication_controller.create_access_token")
@patch("controllers.authentication_controller.create_refresh_token")
def test_register_success(mock_create_refresh, mock_create_access, 
                         mock_create_user, mock_hash, mock_get_user, mock_user):
    """Test successful user registration."""
    # Setup
    mock_get_user.return_value = None
    mock_hash.return_value = "hashed_password"
    mock_create_user.return_value = mock_user
    mock_create_access.return_value = "access_token"
    mock_create_refresh.return_value = "refresh_token"
    
    # Execute
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "firstname": TEST_FIRSTNAME,
            "lastname": TEST_LASTNAME
        }
    )
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert "user" in data
    assert "tokens" in data
    assert data["user"]["email"] == TEST_EMAIL
    assert data["tokens"]["access_token"] == "access_token"
    assert data["tokens"]["refresh_token"] == "refresh_token"
    mock_get_user.assert_called_once_with(TEST_EMAIL)
    mock_hash.assert_called_once_with(TEST_PASSWORD)
    mock_create_user.assert_called_once()
    mock_create_access.assert_called_once()
    mock_create_refresh.assert_called_once()

@patch("controllers.authentication_controller.get_user_by_email")
def test_register_email_exists(mock_get_user, mock_user):
    """Test registration with existing email."""
    # Setup
    mock_get_user.return_value = mock_user
    
    # Execute
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "firstname": TEST_FIRSTNAME,
            "lastname": TEST_LASTNAME
        }
    )
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "Email already registered" in data["detail"]
    mock_get_user.assert_called_once_with(TEST_EMAIL)

@patch("controllers.authentication_controller.jwt.decode")
@patch("controllers.authentication_controller.create_access_token")
@patch("controllers.authentication_controller.create_refresh_token")
def test_refresh_token_success(mock_create_refresh, mock_create_access, mock_jwt_decode):
    """Test successful token refresh."""
    # Setup
    payload = {"sub": TEST_EMAIL, "user_id": TEST_USER_ID}
    mock_jwt_decode.return_value = payload
    mock_create_access.return_value = "new_access_token"
    mock_create_refresh.return_value = "new_refresh_token"
    
    # Execute
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "valid_refresh_token"}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["access_token"] == "new_access_token"
    assert data["refresh_token"] == "new_refresh_token"
    mock_jwt_decode.assert_called_once()
    mock_create_access.assert_called_once_with(payload)
    mock_create_refresh.assert_called_once_with(payload)

@patch("controllers.authentication_controller.jwt.decode")
def test_refresh_token_invalid(mock_jwt_decode):
    """Test refresh with invalid token."""
    # Setup
    mock_jwt_decode.side_effect = Exception("Invalid token")
    
    # Execute
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_refresh_token"}
    )
    
    # Assert
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "Invalid refresh token" in data["detail"]
    mock_jwt_decode.assert_called_once() 