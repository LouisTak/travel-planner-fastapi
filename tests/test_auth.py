import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json
from sqlalchemy.orm import Session

class TestAuthenticationController:
    def test_register_success(self, client: TestClient):
        """Test successful user registration."""
        response = client.post(
            "/api/v1/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "nickname": "New User",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "id" in data
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with an email that's already in use."""
        response = client.post(
            "/api/v1/register",
            json={
                "email": "test@example.com",  # Same as test_user fixture
                "username": "anotheruser",
                "nickname": "Another User",
                "password": "password123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_login_success(self, client: TestClient, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/login",
            json={
                "email": "test@example.com",
                "password": "password"  # Matches the hashed password in test_user fixture
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]

    def test_me_endpoint(self, authenticated_client: TestClient):
        """Test the /me endpoint for getting user info."""
        response = authenticated_client.post("/api/v1/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"
        assert data["role"] == "SUBSCRIBER"

    def test_me_endpoint_unauthorized(self, client: TestClient):
        """Test the /me endpoint without authentication."""
        response = client.post("/api/v1/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED 