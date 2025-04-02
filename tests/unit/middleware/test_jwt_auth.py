import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from middleware.jwt_auth import JWTBearer
from datetime import datetime, timedelta
import jwt
from jose import JWTError
from sqlalchemy.orm import Session
from config import settings

# Test constants
TEST_TOKEN = "test_token"
TEST_VALID_PAYLOAD = {
    "sub": "test@example.com",
    "exp": (datetime.utcnow() + timedelta(minutes=30)).timestamp(),
    "role": "user"
}
TEST_EXPIRED_PAYLOAD = {
    "sub": "test@example.com",
    "exp": (datetime.utcnow() - timedelta(minutes=30)).timestamp(),
    "role": "user"
}
TEST_ADMIN_PAYLOAD = {
    "sub": "admin@example.com",
    "exp": (datetime.utcnow() + timedelta(minutes=30)).timestamp(),
    "role": "admin"
}

@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_request():
    request = MagicMock()
    request.url.path = "/api/v1/protected"
    return request

@pytest.fixture
def mock_credentials():
    credentials = MagicMock()
    credentials.scheme = "Bearer"
    credentials.credentials = TEST_TOKEN
    return credentials

@pytest.fixture
def jwt_bearer():
    return JWTBearer()

@pytest.fixture
def admin_jwt_bearer():
    return JWTBearer(allowed_roles=["admin"])

@pytest.mark.asyncio
@patch("middleware.jwt_auth.HTTPBearer.__call__")
async def test_jwt_bearer_public_path(mock_super_call, jwt_bearer, mock_db):
    """Test that public paths are skipped."""
    mock_request = MagicMock()
    mock_request.url.path = "/api/v1/auth/login"
    
    result = await jwt_bearer(mock_request, mock_db)
    
    assert result is None
    mock_super_call.assert_not_called()

@pytest.mark.asyncio
@patch("middleware.jwt_auth.HTTPBearer.__call__")
@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
async def test_jwt_bearer_valid_token(mock_verify_jwt, mock_super_call, jwt_bearer, mock_request, mock_credentials, mock_db):
    """Test that valid tokens pass authentication."""
    mock_super_call.return_value = mock_credentials
    mock_verify_jwt.return_value = True
    
    result = await jwt_bearer(mock_request, mock_db)
    
    assert result == TEST_TOKEN
    mock_super_call.assert_called_once_with(mock_request)
    mock_verify_jwt.assert_called_once_with(TEST_TOKEN, mock_db)

@pytest.mark.asyncio
@patch("middleware.jwt_auth.HTTPBearer.__call__")
async def test_jwt_bearer_no_credentials(mock_super_call, jwt_bearer, mock_request, mock_db):
    """Test that missing credentials raise an exception."""
    mock_super_call.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await jwt_bearer(mock_request, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "Invalid authorization code" in exc_info.value.detail

@pytest.mark.asyncio
@patch("middleware.jwt_auth.HTTPBearer.__call__")
async def test_jwt_bearer_invalid_scheme(mock_super_call, jwt_bearer, mock_request, mock_db):
    """Test that invalid schemes raise an exception."""
    mock_credentials = MagicMock()
    mock_credentials.scheme = "Basic"
    mock_credentials.credentials = TEST_TOKEN
    mock_super_call.return_value = mock_credentials
    
    with pytest.raises(HTTPException) as exc_info:
        await jwt_bearer(mock_request, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "Invalid authentication scheme" in exc_info.value.detail

@pytest.mark.asyncio
@patch("middleware.jwt_auth.HTTPBearer.__call__")
@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
async def test_jwt_bearer_invalid_token(mock_verify_jwt, mock_super_call, jwt_bearer, mock_request, mock_credentials, mock_db):
    """Test that invalid tokens raise an exception."""
    mock_super_call.return_value = mock_credentials
    mock_verify_jwt.return_value = False
    
    with pytest.raises(HTTPException) as exc_info:
        await jwt_bearer(mock_request, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "Invalid token or expired token" in exc_info.value.detail

@pytest.mark.asyncio
@patch("middleware.jwt_auth.HTTPBearer.__call__")
@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
@patch("middleware.jwt_auth.JWTBearer._decode_token")
async def test_jwt_bearer_role_check_valid(mock_decode_token, mock_verify_jwt, mock_super_call, 
                                    admin_jwt_bearer, mock_request, mock_credentials, mock_db):
    """Test that valid roles pass authentication."""
    mock_super_call.return_value = mock_credentials
    mock_verify_jwt.return_value = True
    mock_decode_token.return_value = TEST_ADMIN_PAYLOAD
    
    result = await admin_jwt_bearer(mock_request, mock_db)
    
    assert result == TEST_TOKEN
    mock_super_call.assert_called_once_with(mock_request)
    mock_verify_jwt.assert_called_once_with(TEST_TOKEN, mock_db)
    mock_decode_token.assert_called_once_with(TEST_TOKEN)

@pytest.mark.asyncio
@patch("middleware.jwt_auth.HTTPBearer.__call__")
@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
@patch("middleware.jwt_auth.JWTBearer._decode_token")
async def test_jwt_bearer_role_check_invalid(mock_decode_token, mock_verify_jwt, mock_super_call, 
                                      admin_jwt_bearer, mock_request, mock_credentials, mock_db):
    """Test that invalid roles raise an exception."""
    mock_super_call.return_value = mock_credentials
    mock_verify_jwt.return_value = True
    mock_decode_token.return_value = TEST_VALID_PAYLOAD  # User role, not admin
    
    with pytest.raises(HTTPException) as exc_info:
        await admin_jwt_bearer(mock_request, mock_db)
    
    assert exc_info.value.status_code == 403
    assert "Insufficient permissions" in exc_info.value.detail

@pytest.mark.asyncio
@patch("middleware.jwt_auth.jwt.decode")
@patch("middleware.jwt_auth.get_user_by_email")
async def test_verify_jwt_valid(mock_get_user, mock_jwt_decode, jwt_bearer, mock_db):
    """Test valid JWT verification."""
    mock_jwt_decode.return_value = TEST_VALID_PAYLOAD
    mock_get_user.return_value = MagicMock()  # Return a user
    
    result = await jwt_bearer._verify_jwt(TEST_TOKEN, mock_db)
    
    assert result is True
    mock_jwt_decode.assert_called_once()
    mock_get_user.assert_called_once_with(TEST_VALID_PAYLOAD["sub"])

@pytest.mark.asyncio
@patch("middleware.jwt_auth.jwt.decode")
async def test_verify_jwt_expired(mock_jwt_decode, jwt_bearer, mock_db):
    """Test expired JWT verification."""
    mock_jwt_decode.return_value = TEST_EXPIRED_PAYLOAD
    
    result = await jwt_bearer._verify_jwt(TEST_TOKEN, mock_db)
    
    assert result is False

@pytest.mark.asyncio
@patch("middleware.jwt_auth.jwt.decode")
@patch("middleware.jwt_auth.get_user_by_email")
async def test_verify_jwt_user_not_found(mock_get_user, mock_jwt_decode, jwt_bearer, mock_db):
    """Test JWT verification when user doesn't exist."""
    mock_jwt_decode.return_value = TEST_VALID_PAYLOAD
    mock_get_user.return_value = None  # No user found
    
    result = await jwt_bearer._verify_jwt(TEST_TOKEN, mock_db)
    
    assert result is False

@pytest.mark.asyncio
@patch("middleware.jwt_auth.jwt.decode")
async def test_verify_jwt_exception(mock_jwt_decode, jwt_bearer, mock_db):
    """Test JWT verification with exception."""
    mock_jwt_decode.side_effect = Exception("Test exception")
    
    result = await jwt_bearer._verify_jwt(TEST_TOKEN, mock_db)
    
    assert result is False

@patch("middleware.jwt_auth.jwt.decode")
def test_decode_token_valid(mock_jwt_decode, jwt_bearer):
    """Test token decoding with valid token."""
    mock_jwt_decode.return_value = TEST_VALID_PAYLOAD
    
    result = jwt_bearer._decode_token(TEST_TOKEN)
    
    assert result == TEST_VALID_PAYLOAD
    mock_jwt_decode.assert_called_once()

@patch("middleware.jwt_auth.jwt.decode")
def test_decode_token_expired(mock_jwt_decode, jwt_bearer):
    """Test token decoding with expired token."""
    mock_jwt_decode.side_effect = jwt.ExpiredSignatureError
    
    result = jwt_bearer._decode_token(TEST_TOKEN)
    
    assert result is None

@patch("middleware.jwt_auth.jwt.decode")
def test_decode_token_invalid(mock_jwt_decode, jwt_bearer):
    """Test token decoding with invalid token."""
    mock_jwt_decode.side_effect = JWTError
    
    result = jwt_bearer._decode_token(TEST_TOKEN)
    
    assert result is None

@patch("middleware.jwt_auth.jwt.decode")
def test_decode_token_exception(mock_jwt_decode, jwt_bearer):
    """Test token decoding with generic exception."""
    mock_jwt_decode.side_effect = Exception("Test exception")
    
    result = jwt_bearer._decode_token(TEST_TOKEN)
    
    assert result is None 