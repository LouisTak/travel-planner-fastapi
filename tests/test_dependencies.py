import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
import asyncio
from models.user import User, UserRole
from dependencies.role_checker import check_role_permissions, minimum_role
from models.role_permissions import RolePermissions

class TestRoleChecker:
    @pytest.mark.asyncio
    async def test_require_admin_with_admin_user(self):
        """Test the require_admin dependency with an admin user."""
        # Create a mock admin user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.ADMIN.value
    
        # Call the function and verify no exception is raised
        from controllers.user_controller import require_admin
        result = await require_admin(mock_user)
        assert result == mock_user
    
    @pytest.mark.asyncio
    async def test_require_admin_with_non_admin_user(self):
        """Test the require_admin dependency with a non-admin user."""
        # Create a mock non-admin user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.SUBSCRIBER.value
    
        # Call the function and verify an exception is raised
        from controllers.user_controller import require_admin
        with pytest.raises(HTTPException) as excinfo:
            await require_admin(mock_user)
        assert excinfo.value.status_code == 403
        assert "Admin role required" in excinfo.value.detail
    
    @pytest.mark.asyncio
    @patch('dependencies.role_checker.RolePermissions.has_feature')
    async def test_check_role_permissions_with_access(self, mock_has_feature):
        """Test the check_role_permissions dependency with a user that has access."""
        mock_has_feature.return_value = True
    
        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.PREMIUM.value
    
        # Create the dependency
        role_checker = check_role_permissions(["premium_feature"])
    
        # Call the dependency and verify no exception is raised
        result = await role_checker(mock_user)
        assert result == mock_user
    
    @pytest.mark.asyncio
    @patch('dependencies.role_checker.RolePermissions.has_feature')
    async def test_check_role_permissions_without_access(self, mock_has_feature):
        """Test the check_role_permissions dependency with a user that doesn't have access."""
        mock_has_feature.return_value = False
    
        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.FREE.value
    
        # Create the dependency
        role_checker = check_role_permissions(["premium_feature"])
    
        # Call the dependency and verify an exception is raised
        with pytest.raises(HTTPException) as excinfo:
            await role_checker(mock_user)
        assert excinfo.value.status_code == 403
        assert "access to this feature" in excinfo.value.detail.lower()
    
    @pytest.mark.skip(reason="Plan limits not implemented yet")
    def test_check_plan_limits_within_limits(self):
        """Test the check_plan_limits dependency with a user within limits."""
        pass
    
    @pytest.mark.skip(reason="Plan limits not implemented yet")
    def test_check_plan_limits_at_limit(self):
        """Test the check_plan_limits dependency with a user at their limit."""
        pass
    
    @pytest.mark.asyncio
    async def test_minimum_role_with_sufficient_role(self):
        """Test the minimum_role dependency with a user of sufficient role."""
        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.PREMIUM.value
    
        # Create the dependency
        role_checker = minimum_role(UserRole.SUBSCRIBER)  # Require at least SUBSCRIBER
    
        # Call the dependency and verify no exception is raised
        result = await role_checker(mock_user)
        assert result == mock_user
    
    @pytest.mark.asyncio
    async def test_minimum_role_with_insufficient_role(self):
        """Test the minimum_role dependency with a user of insufficient role."""
        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.FREE.value
    
        # Create the dependency
        role_checker = minimum_role(UserRole.SUBSCRIBER)  # Require at least SUBSCRIBER
    
        # Call the dependency and verify an exception is raised
        with pytest.raises(HTTPException) as excinfo:
            await role_checker(mock_user)
        assert excinfo.value.status_code == 403
        assert "minimum role" in excinfo.value.detail.lower() 