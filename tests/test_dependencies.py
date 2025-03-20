import pytest
from fastapi import HTTPException
from unittest.mock import MagicMock, patch
from dependencies.role_checker import (
    check_role_permissions, 
    check_plan_limits, 
    check_ai_limits, 
    minimum_role
)
from models.user import User
from models.user_role import UserRole

class TestRoleChecker:
    
    def test_require_admin_with_admin_user(self):
        """Test the require_admin dependency with an admin user."""
        # Create a mock admin user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.ADMIN.value
        
        # Call the function and verify no exception is raised
        from controllers.user_controller import require_admin
        result = require_admin(mock_user)
        assert result == mock_user
    
    def test_require_admin_with_non_admin_user(self):
        """Test the require_admin dependency with a non-admin user."""
        # Create a mock non-admin user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.SUBSCRIBER.value
        
        # Call the function and verify an exception is raised
        from controllers.user_controller import require_admin
        with pytest.raises(HTTPException) as excinfo:
            require_admin(mock_user)
        
        assert excinfo.value.status_code == 403
        assert "requires admin role" in excinfo.value.detail
    
    @patch('dependencies.role_checker.RolePermissions.has_feature')
    def test_check_role_permissions_with_access(self, mock_has_feature):
        """Test the check_role_permissions dependency with a user that has access."""
        mock_has_feature.return_value = True
        
        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.PREMIUM.value
        
        # Create the dependency
        dependency = check_role_permissions(["premium_feature"])
        
        # Call the dependency and verify no exception is raised
        result = dependency(mock_user)
        assert result == mock_user
        
        # Verify has_feature was called with the right arguments
        mock_has_feature.assert_called_with(UserRole.PREMIUM.value, "premium_feature")
    
    @patch('dependencies.role_checker.RolePermissions.has_feature')
    def test_check_role_permissions_without_access(self, mock_has_feature):
        """Test the check_role_permissions dependency with a user that doesn't have access."""
        mock_has_feature.return_value = False
        
        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.FREE.value
        
        # Create the dependency
        dependency = check_role_permissions(["premium_feature"])
        
        # Call the dependency and verify an exception is raised
        with pytest.raises(HTTPException) as excinfo:
            dependency(mock_user)
        
        assert excinfo.value.status_code == 403
        assert "don't have access" in excinfo.value.detail
        
        # Verify has_feature was called with the right arguments
        mock_has_feature.assert_called_with(UserRole.FREE.value, "premium_feature")
    
    @patch('dependencies.role_checker.RolePermissions.get_travel_plan_limits')
    @patch('repositories.travel_plan_repository.count_user_travel_plans')
    async def test_check_plan_limits_within_limits(self, mock_count_plans, mock_get_limits):
        """Test the check_plan_limits dependency with a user within their limits."""
        # Set up mocks
        mock_get_limits.return_value = {
            UserRole.SUBSCRIBER.value: {
                "max_plans": 5
            }
        }
        mock_count_plans.return_value = 2  # User has 2 plans, limit is 5
        
        # Create a mock user and db
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.SUBSCRIBER.value
        mock_user.id = "test-user-id"
        mock_db = MagicMock()
        
        # Create the dependency
        dependency = check_plan_limits("create_plan")
        
        # Call the dependency and verify no exception is raised
        result = await dependency(mock_user, mock_db)
        assert result == mock_user
        
        # Verify our mocks were called correctly
        mock_get_limits.assert_called_once()
        mock_count_plans.assert_called_with(mock_db, mock_user.id)
    
    @patch('dependencies.role_checker.RolePermissions.get_travel_plan_limits')
    @patch('repositories.travel_plan_repository.count_user_travel_plans')
    async def test_check_plan_limits_at_limit(self, mock_count_plans, mock_get_limits):
        """Test the check_plan_limits dependency with a user at their limit."""
        # Set up mocks
        mock_get_limits.return_value = {
            UserRole.FREE.value: {
                "max_plans": 2
            }
        }
        mock_count_plans.return_value = 2  # User has 2 plans, limit is 2
        
        # Create a mock user and db
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.FREE.value
        mock_user.id = "test-user-id"
        mock_db = MagicMock()
        
        # Create the dependency
        dependency = check_plan_limits("create_plan")
        
        # Call the dependency and verify an exception is raised
        with pytest.raises(HTTPException) as excinfo:
            await dependency(mock_user, mock_db)
        
        assert excinfo.value.status_code == 403
        assert "maximum number of travel plans" in excinfo.value.detail
        
        # Verify our mocks were called correctly
        mock_get_limits.assert_called_once()
        mock_count_plans.assert_called_with(mock_db, mock_user.id)
    
    def test_minimum_role_with_sufficient_role(self):
        """Test the minimum_role dependency with a user of sufficient role."""
        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.PREMIUM.value
        
        # Create the dependency
        dependency = minimum_role(UserRole.SUBSCRIBER)  # Require at least SUBSCRIBER
        
        # Call the dependency and verify no exception is raised
        result = dependency(mock_user)
        assert result == mock_user
    
    def test_minimum_role_with_insufficient_role(self):
        """Test the minimum_role dependency with a user of insufficient role."""
        # Create a mock user
        mock_user = MagicMock(spec=User)
        mock_user.role = UserRole.FREE.value
        
        # Create the dependency
        dependency = minimum_role(UserRole.SUBSCRIBER)  # Require at least SUBSCRIBER
        
        # Call the dependency and verify an exception is raised
        with pytest.raises(HTTPException) as excinfo:
            dependency(mock_user)
        
        assert excinfo.value.status_code == 403
        assert "minimum role required" in excinfo.value.detail 