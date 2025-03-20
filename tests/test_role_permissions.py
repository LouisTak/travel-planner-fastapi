import pytest
from models.user_role import UserRole
from models.role_permissions import RolePermissions

class TestRolePermissions:
    
    def test_get_travel_plan_limits(self):
        """Test that travel plan limits are correctly defined for each role."""
        limits = RolePermissions.get_travel_plan_limits()
        
        # Check that all roles have limits defined
        for role in UserRole:
            assert role.value in limits
        
        # Check specific limits for some roles
        free_limits = limits[UserRole.FREE.value]
        assert free_limits["max_plans"] == 2
        assert free_limits["max_days_per_plan"] == 3
        assert free_limits["max_activities_per_day"] == 3
        
        premium_limits = limits[UserRole.PREMIUM.value]
        assert premium_limits["max_plans"] > free_limits["max_plans"]
        assert premium_limits["max_days_per_plan"] > free_limits["max_days_per_plan"]
        assert premium_limits["max_activities_per_day"] > free_limits["max_activities_per_day"]
        
        admin_limits = limits[UserRole.ADMIN.value]
        # Admin should have unlimited (-1) plans, which is special case
        assert admin_limits["max_plans"] == -1

    def test_get_feature_descriptions(self):
        """Test that feature descriptions are correctly defined."""
        descriptions = RolePermissions.get_feature_descriptions()
        
        # Check for the presence of some key features
        assert "view_plans" in descriptions
        assert "basic_planning" in descriptions
        
        # Check some specific descriptions
        assert "View and browse travel plans" in descriptions["view_plans"]
        assert "Create and manage basic travel plans" in descriptions["basic_planning"]

    def test_has_feature_free_user(self):
        """Test feature access for free users."""
        # Free users should have access to basic features
        assert RolePermissions.has_feature(UserRole.FREE.value, "view_plans") is True
        assert RolePermissions.has_feature(UserRole.FREE.value, "basic_planning") is True
        
        # Free users should not have access to premium features
        assert RolePermissions.has_feature(UserRole.FREE.value, "export_plans") is False
        assert RolePermissions.has_feature(UserRole.FREE.value, "advanced_suggestions") is False

    def test_has_feature_subscriber_user(self):
        """Test feature access for subscriber users."""
        # Subscribers should have access to all free features
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "view_plans") is True
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "basic_planning") is True
        
        # Subscribers should have some additional features
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "export_plans") is True
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "regenerate_days") is True
        
        # Subscribers should not have access to premium features
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "advanced_suggestions") is False
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "collaborative_planning") is False

    def test_has_feature_premium_user(self):
        """Test feature access for premium users."""
        # Premium users should have access to all subscriber features
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "view_plans") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "basic_planning") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "export_plans") is True
        
        # Premium users should have additional features
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "advanced_suggestions") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "collaborative_planning") is True
        
        # Premium users should not have access to admin features
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "user_management") is False

    def test_has_feature_admin_user(self):
        """Test feature access for admin users."""
        # Admins should have access to all features
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "view_plans") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "basic_planning") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "export_plans") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "advanced_suggestions") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "user_management") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "all_features") is True

    def test_has_feature_nonexistent(self):
        """Test checking for a feature that doesn't exist."""
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "nonexistent_feature") is False 