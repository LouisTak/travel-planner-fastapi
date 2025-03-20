import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json
from sqlalchemy.orm import Session

class TestUserController:
    def test_update_profile(self, authenticated_client: TestClient, test_user):
        """Test updating user profile."""
        response = authenticated_client.post(
            "/api/v1/update-profile",
            json={
                "email": "test@example.com",  # Include email to identify the user
                "nickname": "Updated User"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["nickname"] == "Updated User"
        assert data["email"] == "test@example.com"  # Email shouldn't change

    def test_update_profile_unauthorized(self, client: TestClient):
        """Test updating profile without authentication."""
        response = client.post(
            "/api/v1/update-profile",
            json={
                "email": "test@example.com",
                "nickname": "Updated User"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password(self, authenticated_client: TestClient, test_user):
        """Test changing password."""
        response = authenticated_client.post(
            "/api/v1/change-password",
            json={
                "email": "test@example.com",  # Include email to identify the user
                "old_password": "password",
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_old_password(self, authenticated_client: TestClient, test_user):
        """Test changing password with wrong old password."""
        response = authenticated_client.post(
            "/api/v1/change-password",
            json={
                "email": "test@example.com",  # Include email to identify the user
                "old_password": "wrongpassword",
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect old password" in response.json()["detail"]

    def test_list_users_as_admin(self, admin_client: TestClient):
        """Test listing all users as admin."""
        response = admin_client.get("/api/v1/admin/users")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # Check if our test users are in the list
        emails = [user["email"] for user in data]
        assert "admin@example.com" in emails

    def test_list_users_as_non_admin(self, authenticated_client: TestClient):
        """Test listing all users as non-admin user."""
        response = authenticated_client.get("/api/v1/admin/users")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "admin role required" in response.json()["detail"].lower() 