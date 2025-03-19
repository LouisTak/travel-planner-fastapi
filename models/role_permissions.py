"""
Role-based permissions and limits for the Travel Planner application.
"""
from typing import Dict, Any
from models.user_role import UserRole

class RolePermissions:
    """Define permissions and limits for each user role."""
    
    @staticmethod
    def get_travel_plan_limits() -> Dict[str, Dict[str, Any]]:
        """
        Get travel plan creation limits for each role.
        
        Returns:
            Dictionary containing limits for each role:
            - max_plans: Maximum number of travel plans
            - max_days_per_plan: Maximum days per travel plan
            - max_activities_per_day: Maximum activities per day
            - can_use_ai: Whether the role can use AI features
            - can_regenerate_days: Whether the role can regenerate days
            - max_suggestions_per_day: Maximum AI suggestions per day
        """
        return {
            UserRole.FREE.value: {
                "max_plans": 2,
                "max_days_per_plan": 3,
                "max_activities_per_day": 3,
                "can_use_ai": True,
                "can_regenerate_days": False,
                "max_suggestions_per_day": 5,
                "features": [
                    "basic_planning",
                    "view_plans",
                    "basic_suggestions"
                ]
            },
            UserRole.SUBSCRIBER.value: {
                "max_plans": 5,
                "max_days_per_plan": 7,
                "max_activities_per_day": 5,
                "can_use_ai": True,
                "can_regenerate_days": True,
                "max_suggestions_per_day": 15,
                "features": [
                    "basic_planning",
                    "view_plans",
                    "basic_suggestions",
                    "regenerate_days",
                    "export_plans"
                ]
            },
            UserRole.PREMIUM.value: {
                "max_plans": 10,
                "max_days_per_plan": 14,
                "max_activities_per_day": 8,
                "can_use_ai": True,
                "can_regenerate_days": True,
                "max_suggestions_per_day": 50,
                "features": [
                    "basic_planning",
                    "view_plans",
                    "advanced_suggestions",
                    "regenerate_days",
                    "export_plans",
                    "collaborative_planning",
                    "priority_support"
                ]
            },
            UserRole.TESTER.value: {
                "max_plans": 20,
                "max_days_per_plan": 30,
                "max_activities_per_day": 10,
                "can_use_ai": True,
                "can_regenerate_days": True,
                "max_suggestions_per_day": 100,
                "features": [
                    "basic_planning",
                    "view_plans",
                    "advanced_suggestions",
                    "regenerate_days",
                    "export_plans",
                    "collaborative_planning",
                    "beta_features",
                    "debug_mode"
                ]
            },
            UserRole.ADMIN.value: {
                "max_plans": -1,  # Unlimited
                "max_days_per_plan": -1,  # Unlimited
                "max_activities_per_day": -1,  # Unlimited
                "can_use_ai": True,
                "can_regenerate_days": True,
                "max_suggestions_per_day": -1,  # Unlimited
                "features": [
                    "basic_planning",
                    "view_plans",
                    "advanced_suggestions",
                    "regenerate_days",
                    "export_plans",
                    "collaborative_planning",
                    "user_management",
                    "system_settings",
                    "analytics",
                    "all_features"
                ]
            }
        }
    
    @staticmethod
    def get_feature_descriptions() -> Dict[str, str]:
        """Get descriptions for each feature."""
        return {
            "basic_planning": "Create and manage basic travel plans",
            "view_plans": "View and browse travel plans",
            "basic_suggestions": "Get basic AI-powered travel suggestions",
            "advanced_suggestions": "Get detailed, personalized AI travel recommendations",
            "regenerate_days": "Regenerate specific days in a travel plan",
            "export_plans": "Export travel plans in various formats",
            "collaborative_planning": "Plan trips collaboratively with others",
            "priority_support": "Access to priority customer support",
            "beta_features": "Access to beta and experimental features",
            "debug_mode": "Access to debugging tools and detailed logs",
            "user_management": "Manage user accounts and roles",
            "system_settings": "Configure system-wide settings",
            "analytics": "Access to system analytics and metrics",
            "all_features": "Access to all system features"
        }
    
    @staticmethod
    def has_feature(role: str, feature: str) -> bool:
        """
        Check if a role has access to a specific feature.
        
        Args:
            role: User role to check
            feature: Feature to check for
            
        Returns:
            bool: Whether the role has access to the feature
        """
        limits = RolePermissions.get_travel_plan_limits()
        return feature in limits.get(role, {}).get("features", []) 