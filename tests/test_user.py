import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json
from sqlalchemy.orm import Session

class TestUserController:
    def test_update_profile(self, authenticated_client: TestClient):
        """Test updating user profile."""
        response = authenticated_client.put(
            "/api/v1/users/me",
            json={
                "username": "updateduser",
                "nickname": "Updated User"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "updateduser"
        assert data["nickname"] == "Updated User"
        assert data["email"] == "test@example.com"  # Email shouldn't change

    def test_update_profile_unauthorized(self, client: TestClient):
        """Test updating profile without authentication."""
        response = client.put(
            "/api/v1/users/me",
            json={
                "username": "updateduser",
                "nickname": "Updated User"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password(self, authenticated_client: TestClient):
        """Test changing password."""
        response = authenticated_client.post(
            "/api/v1/users/change-password",
            json={
                "old_password": "password",
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK

    def test_change_password_wrong_old_password(self, authenticated_client: TestClient):
        """Test changing password with wrong old password."""
        response = authenticated_client.post(
            "/api/v1/users/change-password",
            json={
                "old_password": "wrongpassword",
                "new_password": "newpassword123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Incorrect password" in response.json()["detail"]

    def test_update_user_role_as_admin(self, admin_client: TestClient, test_user):
        """Test updating user role as admin."""
        response = admin_client.post(
            f"/api/v1/users/{test_user.id}/role",
            json="PREMIUM"
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "PREMIUM"

    def test_update_user_role_as_non_admin(self, authenticated_client: TestClient, admin_user):
        """Test updating user role as non-admin user."""
        response = authenticated_client.post(
            f"/api/v1/users/{admin_user.id}/role",
            json="FREE"
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "requires admin role" in response.json()["detail"]

    def test_list_users_as_admin(self, admin_client: TestClient):
        """Test listing all users as admin."""
        response = admin_client.get("/api/v1/users")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # At least test_user and admin_user
        
        # Check if our test users are in the list
        emails = [user["email"] for user in data]
        assert "test@example.com" in emails
        assert "admin@example.com" in emails

    def test_list_users_as_non_admin(self, authenticated_client: TestClient):
        """Test listing all users as non-admin user."""
        response = authenticated_client.get("/api/v1/users")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "requires admin role" in response.json()["detail"] 