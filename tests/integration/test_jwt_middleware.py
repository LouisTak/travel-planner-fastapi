import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import JSONResponse
import jwt

from main import app
from middleware.jwt_auth import JWTBearer

# Create a test app with protected routes
test_app = FastAPI()
router = APIRouter()

# Create different JWT bearer instances for different role requirements
auth_bearer = JWTBearer()  # Basic authentication
admin_bearer = JWTBearer(allowed_roles=["admin"])  # Admin only
premium_bearer = JWTBearer(allowed_roles=["premium", "admin"])  # Premium and admin

@router.get("/protected")
async def protected_route(token = Depends(auth_bearer)):
    """Example of a protected route that requires any valid JWT token."""
    return {"message": "This is a protected route", "token": token}

@router.get("/admin-only")
async def admin_route(token = Depends(admin_bearer)):
    """Example of a route that requires admin role."""
    return {"message": "This is an admin-only route", "token": token}

@router.get("/premium-feature")
async def premium_route(token = Depends(premium_bearer)):
    """Example of a route that requires premium role."""
    return {"message": "This is a premium feature", "token": token}

@router.get("/public")
async def public_route():
    """Example of a public route that doesn't require authentication."""
    return {"message": "This is a public route"}

test_app.include_router(router, prefix="/api/v1/test")

# Test client
client = TestClient(test_app)

# Test public routes
def test_public_route():
    """Test accessing a public route without authentication."""
    response = client.get("/api/v1/test/public")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a public route"}

# Test protected routes without authentication
def test_protected_route_no_auth():
    """Test accessing a protected route without authentication."""
    response = client.get("/api/v1/test/protected")
    assert response.status_code == 403
    assert "detail" in response.json()

# Test with valid authentication token
@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
@patch("middleware.jwt_auth.get_user_by_email")
def test_protected_route_with_auth(mock_get_user, mock_verify_jwt, auth_headers):
    """Test accessing a protected route with valid authentication."""
    # Setup
    mock_verify_jwt.return_value = True
    mock_get_user.return_value = {"id": "user_id", "email": "test@example.com"}
    
    # Execute
    response = client.get("/api/v1/test/protected", headers=auth_headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "This is a protected route"

# Test role-based permissions
@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
@patch("middleware.jwt_auth.JWTBearer._decode_token")
@patch("middleware.jwt_auth.get_user_by_email")
def test_admin_route_with_user_auth(mock_get_user, mock_decode_token, mock_verify_jwt, auth_headers):
    """Test accessing an admin-only route with regular user authentication."""
    # Setup
    mock_verify_jwt.return_value = True
    mock_get_user.return_value = {"id": "user_id", "email": "test@example.com"}
    mock_decode_token.return_value = {"role": "user"}
    
    # Execute
    response = client.get("/api/v1/test/admin-only", headers=auth_headers)
    
    # Assert
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]

@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
@patch("middleware.jwt_auth.JWTBearer._decode_token")
@patch("middleware.jwt_auth.get_user_by_email")
def test_admin_route_with_admin_auth(mock_get_user, mock_decode_token, mock_verify_jwt, admin_headers):
    """Test accessing an admin-only route with admin authentication."""
    # Setup
    mock_verify_jwt.return_value = True
    mock_get_user.return_value = {"id": "admin_id", "email": "admin@example.com"}
    mock_decode_token.return_value = {"role": "admin"}
    
    # Execute
    response = client.get("/api/v1/test/admin-only", headers=admin_headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "This is an admin-only route"

@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
@patch("middleware.jwt_auth.JWTBearer._decode_token")
@patch("middleware.jwt_auth.get_user_by_email")
def test_premium_route_with_user_auth(mock_get_user, mock_decode_token, mock_verify_jwt, auth_headers):
    """Test accessing a premium route with regular user authentication."""
    # Setup
    mock_verify_jwt.return_value = True
    mock_get_user.return_value = {"id": "user_id", "email": "test@example.com"}
    mock_decode_token.return_value = {"role": "user"}
    
    # Execute
    response = client.get("/api/v1/test/premium-feature", headers=auth_headers)
    
    # Assert
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]

@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
@patch("middleware.jwt_auth.JWTBearer._decode_token")
@patch("middleware.jwt_auth.get_user_by_email")
def test_premium_route_with_admin_auth(mock_get_user, mock_decode_token, mock_verify_jwt, admin_headers):
    """Test accessing a premium route with admin authentication."""
    # Setup
    mock_verify_jwt.return_value = True
    mock_get_user.return_value = {"id": "admin_id", "email": "admin@example.com"}
    mock_decode_token.return_value = {"role": "admin"}
    
    # Execute
    response = client.get("/api/v1/test/premium-feature", headers=admin_headers)
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "This is a premium feature"

# Test invalid tokens
def test_invalid_token_format(invalid_headers):
    """Test with invalid token format."""
    response = client.get("/api/v1/test/protected", headers=invalid_headers)
    assert response.status_code == 403
    assert "detail" in response.json()

@patch("middleware.jwt_auth.jwt.decode")
def test_expired_token(mock_jwt_decode, expired_headers):
    """Test with expired token."""
    mock_jwt_decode.side_effect = jwt.ExpiredSignatureError
    
    response = client.get("/api/v1/test/protected", headers=expired_headers)
    assert response.status_code == 403
    assert "detail" in response.json()

@patch("middleware.jwt_auth.JWTBearer._verify_jwt")
def test_non_existent_user(mock_verify_jwt, auth_headers):
    """Test with token for non-existent user."""
    # Setup
    mock_verify_jwt.return_value = False
    
    # Execute
    response = client.get("/api/v1/test/protected", headers=auth_headers)
    
    # Assert
    assert response.status_code == 403
    assert "detail" in response.json()

# Test invalid authentication scheme
def test_invalid_auth_scheme():
    """Test with invalid authentication scheme."""
    headers = {"Authorization": "Basic dGVzdEB0ZXN0LmNvbTpwYXNzd29yZA=="}
    response = client.get("/api/v1/test/protected", headers=headers)
    assert response.status_code == 403
    assert "detail" in response.json() 