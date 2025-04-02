import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException
from jwt.exceptions import InvalidTokenError
from schemas.authentication_schemas import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    Token,
    TokenData,
    TokenPayload,
    TokenResponse
)

# Test constants
TEST_SECRET_KEY = "test_secret_key"
TEST_ALGORITHM = "HS256"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_ID = "test_user_id"

@pytest.fixture
def user_data():
    return {"sub": TEST_USER_EMAIL, "user_id": TEST_USER_ID}

@patch("schemas.authentication_schemas.settings.secret_key", TEST_SECRET_KEY)
@patch("schemas.authentication_schemas.settings.algorithm", TEST_ALGORITHM)
@patch("schemas.authentication_schemas.settings.access_token_expire_minutes", 30)
def test_create_access_token(user_data):
    """Test access token creation."""
    token = create_access_token(user_data)
    
    # Decode the token to verify its contents
    payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    
    assert payload["sub"] == TEST_USER_EMAIL
    assert payload["user_id"] == TEST_USER_ID
    assert "exp" in payload
    # Check that expiration is about 30 minutes in the future (with a small margin)
    exp_delta = datetime.fromtimestamp(payload["exp"]) - datetime.utcnow()
    assert timedelta(minutes=29) < exp_delta < timedelta(minutes=31)

@patch("schemas.authentication_schemas.settings.secret_key", TEST_SECRET_KEY)
@patch("schemas.authentication_schemas.settings.algorithm", TEST_ALGORITHM)
@patch("schemas.authentication_schemas.settings.refresh_token_expire_days", 7)
def test_create_refresh_token(user_data):
    """Test refresh token creation."""
    token = create_refresh_token(user_data)
    
    # Decode the token to verify its contents
    payload = jwt.decode(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    
    assert payload["sub"] == TEST_USER_EMAIL
    assert payload["user_id"] == TEST_USER_ID
    assert "exp" in payload
    # Check that expiration is about 7 days in the future (with a small margin)
    exp_delta = datetime.fromtimestamp(payload["exp"]) - datetime.utcnow()
    assert timedelta(days=6, hours=23) < exp_delta < timedelta(days=7, hours=1)

@pytest.mark.asyncio
@patch("schemas.authentication_schemas.settings.secret_key", TEST_SECRET_KEY)
@patch("schemas.authentication_schemas.settings.algorithm", TEST_ALGORITHM)
@patch("schemas.authentication_schemas.jwt.decode")
@patch("schemas.authentication_schemas.get_user_by_email")
async def test_get_current_user_valid(mock_get_user, mock_jwt_decode):
    """Test getting current user with valid token."""
    # Setup
    token = "valid_token"
    payload = {"sub": TEST_USER_EMAIL}
    mock_jwt_decode.return_value = payload
    mock_user = MagicMock()
    mock_get_user.return_value = mock_user
    
    # Execute
    result = await get_current_user(token)
    
    # Assert
    assert result == mock_user
    mock_jwt_decode.assert_called_once_with(token, TEST_SECRET_KEY, algorithms=[TEST_ALGORITHM])
    mock_get_user.assert_called_once_with(TEST_USER_EMAIL)

@pytest.mark.asyncio
@patch("schemas.authentication_schemas.jwt.decode")
async def test_get_current_user_no_email(mock_jwt_decode):
    """Test getting current user when email is missing from token."""
    # Setup
    token = "invalid_token"
    payload = {}  # No sub field
    mock_jwt_decode.return_value = payload
    
    # Execute & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail

@pytest.mark.asyncio
@patch("schemas.authentication_schemas.jwt.decode")
async def test_get_current_user_invalid_token(mock_jwt_decode):
    """Test getting current user with invalid token."""
    # Setup
    token = "invalid_token"
    mock_jwt_decode.side_effect = InvalidTokenError()
    
    # Execute & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail

@pytest.mark.asyncio
@patch("schemas.authentication_schemas.jwt.decode")
@patch("schemas.authentication_schemas.get_user_by_email")
async def test_get_current_user_not_found(mock_get_user, mock_jwt_decode):
    """Test getting current user when user doesn't exist."""
    # Setup
    token = "valid_token"
    payload = {"sub": TEST_USER_EMAIL}
    mock_jwt_decode.return_value = payload
    mock_get_user.return_value = None  # User not found
    
    # Execute & Assert
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token)
    
    assert exc_info.value.status_code == 401
    assert "Could not validate credentials" in exc_info.value.detail

def test_token_model():
    """Test the Token model."""
    token_data = {
        "access_token": "access_token_value",
        "refresh_token": "refresh_token_value"
    }
    token = Token(**token_data)
    
    assert token.access_token == "access_token_value"
    assert token.refresh_token == "refresh_token_value"

def test_token_data_model():
    """Test the TokenData model."""
    token_data = TokenData(user_email=TEST_USER_EMAIL)
    
    assert token_data.user_email == TEST_USER_EMAIL

def test_token_payload_model():
    """Test the TokenPayload model."""
    payload_data = {
        "sub": TEST_USER_EMAIL,
        "exp": int(datetime.utcnow().timestamp()) + 3600,
        "iat": int(datetime.utcnow().timestamp()),
        "nbf": int(datetime.utcnow().timestamp()),
        "jti": "random_id",
        "iss": "issuer",
        "aud": "audience",
        "user_id": TEST_USER_ID
    }
    
    payload = TokenPayload(**payload_data)
    
    assert payload.sub == TEST_USER_EMAIL
    assert payload.user_id == TEST_USER_ID
    assert payload.exp == payload_data["exp"]

def test_token_response_model():
    """Test the TokenResponse model."""
    response_data = {
        "access_token": "access_token_value",
        "refresh_token": "refresh_token_value"
    }
    
    response = TokenResponse(**response_data)
    
    assert response.access_token == "access_token_value"
    assert response.refresh_token == "refresh_token_value" 