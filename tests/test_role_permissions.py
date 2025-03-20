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
        assert admin_limits["max_plans"] > premium_limits["max_plans"]

    def test_get_feature_descriptions(self):
        """Test that feature descriptions are correctly defined."""
        descriptions = RolePermissions.get_feature_descriptions()
        
        # Check for the presence of some key features
        assert "view_plans" in descriptions
        assert "create_plan" in descriptions
        assert "delete_plans" in descriptions
        assert "use_ai_suggestions" in descriptions
        assert "use_ai_optimization" in descriptions
        assert "export_plans" in descriptions
        assert "collaborative_planning" in descriptions
    
    def test_has_feature_free_user(self):
        """Test feature access for free users."""
        # Free users should have access to basic features
        assert RolePermissions.has_feature(UserRole.FREE.value, "view_plans") is True
        assert RolePermissions.has_feature(UserRole.FREE.value, "create_plan") is True
        assert RolePermissions.has_feature(UserRole.FREE.value, "delete_plans") is True
        assert RolePermissions.has_feature(UserRole.FREE.value, "use_ai_suggestions") is True
        
        # Free users should not have access to premium features
        assert RolePermissions.has_feature(UserRole.FREE.value, "export_plans") is False
        assert RolePermissions.has_feature(UserRole.FREE.value, "collaborative_planning") is False
        assert RolePermissions.has_feature(UserRole.FREE.value, "use_ai_optimization") is False
    
    def test_has_feature_subscriber_user(self):
        """Test feature access for subscriber users."""
        # Subscribers should have access to all free features
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "view_plans") is True
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "create_plan") is True
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "delete_plans") is True
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "use_ai_suggestions") is True
        
        # Subscribers should have access to some premium features
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "export_plans") is True
        
        # But not to the highest tier features
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "collaborative_planning") is False
        assert RolePermissions.has_feature(UserRole.SUBSCRIBER.value, "use_ai_optimization") is False
    
    def test_has_feature_premium_user(self):
        """Test feature access for premium users."""
        # Premium users should have access to all subscriber features
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "view_plans") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "create_plan") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "delete_plans") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "use_ai_suggestions") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "export_plans") is True
        
        # Premium users should have access to premium features
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "collaborative_planning") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "use_ai_optimization") is True
        assert RolePermissions.has_feature(UserRole.PREMIUM.value, "use_ai_personalization") is True
    
    def test_has_feature_admin_user(self):
        """Test feature access for admin users."""
        # Admins should have access to all features
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "view_plans") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "create_plan") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "delete_plans") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "use_ai_suggestions") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "export_plans") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "collaborative_planning") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "use_ai_optimization") is True
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "use_ai_personalization") is True
        
        # And admin-specific features
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "admin_stats") is True
    
    def test_has_feature_nonexistent(self):
        """Test behavior when checking for a nonexistent feature."""
        # Should return False for a nonexistent feature
        assert RolePermissions.has_feature(UserRole.ADMIN.value, "nonexistent_feature") is False 