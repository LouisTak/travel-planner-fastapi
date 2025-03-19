"""
Dependencies for checking role-based permissions.
"""
from typing import List, Optional, Callable
from functools import wraps
from fastapi import HTTPException, Depends, status
from models.user import User
from models.role_permissions import RolePermissions
from models.user_role import UserRole
from schemas.authentication_schemas import get_current_user


def check_role_permissions(required_features: List[str]):
    """
    Dependency for checking if a user has the required features based on their role.
    
    Args:
        required_features: List of features required to access the endpoint
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        for feature in required_features:
            if not RolePermissions.has_feature(current_user.role, feature):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Your current role ({current_user.role}) does not have access to this feature"
                )
        return current_user
    return role_checker


def check_plan_limits(operation: str):
    """
    Dependency for checking if a user has reached their plan limits.
    
    Args:
        operation: The operation being performed (create_plan, add_activity, etc.)
    """
    async def limit_checker(current_user: User = Depends(get_current_user)):
        limits = RolePermissions.get_travel_plan_limits()[current_user.role]
        
        if operation == "create_plan":
            # Count user's existing plans
            plan_count = len(current_user.travel_plans)
            if limits["max_plans"] != -1 and plan_count >= limits["max_plans"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You have reached the maximum number of travel plans ({limits['max_plans']}) for your role"
                )
        
        return current_user
    return limit_checker


def check_ai_limits(operation: str):
    """
    Dependency for checking if a user has reached their AI usage limits.
    
    Args:
        operation: The operation being performed (get_suggestions, regenerate_day)
    """
    async def limit_checker(current_user: User = Depends(get_current_user)):
        limits = RolePermissions.get_travel_plan_limits()[current_user.role]
        
        if operation == "regenerate_day" and not limits["can_regenerate_days"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your current role does not have access to day regeneration"
            )
        
        # Note: For production, you would want to track daily AI usage in Redis or similar
        return current_user
    return limit_checker


def minimum_role(min_role: UserRole):
    """
    Dependency for checking if a user has at least the specified role level.
    
    Args:
        min_role: Minimum role required to access the endpoint
    """
    role_hierarchy = {
        UserRole.FREE.value: 0,
        UserRole.SUBSCRIBER.value: 1,
        UserRole.PREMIUM.value: 2,
        UserRole.TESTER.value: 3,
        UserRole.ADMIN.value: 4
    }
    
    async def role_checker(current_user: User = Depends(get_current_user)):
        user_level = role_hierarchy.get(current_user.role, -1)
        required_level = role_hierarchy.get(min_role.value, 999)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires at least {min_role.value} role access"
            )
        return current_user
    return role_checker 