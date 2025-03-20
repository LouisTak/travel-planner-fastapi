"""
Dependencies for checking user roles and permissions.
"""
from fastapi import Depends, HTTPException, status
from typing import List, Callable, Dict
from sqlalchemy.orm import Session

from models.user import User
from models.user_role import UserRole
from models.role_permissions import RolePermissions
from dependencies.auth import get_current_user
from database.database import get_db

def check_role_permissions(required_features: List[str]):
    """
    Create a dependency that checks if a user has the required features based on their role.
    
    Args:
        required_features: List of features that the user must have access to
        
    Returns:
        A dependency function that validates user access
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        for feature in required_features:
            if not RolePermissions.has_feature(current_user.role, feature):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"You don't have access to this feature. Required feature: {feature}"
                )
        return current_user
    
    return role_checker

def check_plan_limits(operation: str):
    """
    Create a dependency that checks if a user has reached their plan limits for operations
    like creating a plan.
    
    Args:
        operation: The operation to check limits for ("create_plan", etc.)
        
    Returns:
        A dependency function that validates user limits
    """
    # This would check the database for the user's current number of plans
    # and compare against their role's limit
    async def limit_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # For now, we're assuming the limit check always passes
        # In a real implementation, this would check against the database
        return current_user
    
    return limit_checker

def check_ai_limits(operation: str):
    """
    Create a dependency that checks if a user has reached their AI usage limits,
    specifically for operations like regenerating days.
    
    Args:
        operation: The operation to check limits for ("regenerate_day", etc.)
        
    Returns:
        A dependency function that validates user AI usage
    """
    async def ai_limit_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Check if the user can regenerate days
        limits = RolePermissions.get_travel_plan_limits()
        role_limits = limits.get(current_user.role, {})
        
        if operation == "regenerate_day" and not role_limits.get("can_regenerate_days", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your current subscription doesn't allow regenerating days"
            )
        
        # In a real implementation, we would also check rate limits here
        return current_user
    
    return ai_limit_checker

# Define a helper for the role hierarchy
ROLE_HIERARCHY = {
    UserRole.FREE.value: 0,
    UserRole.SUBSCRIBER.value: 1,
    UserRole.PREMIUM.value: 2,
    UserRole.TESTER.value: 3,
    UserRole.ADMIN.value: 4
}

def minimum_role(min_role: UserRole):
    """
    Create a dependency that checks if a user has at least the specified role level.
    
    Args:
        min_role: The minimum role required
        
    Returns:
        A dependency function that validates user role
    """
    async def role_checker(current_user: User = Depends(get_current_user)):
        current_role_level = ROLE_HIERARCHY.get(current_user.role, -1)
        min_role_level = ROLE_HIERARCHY.get(min_role.value, 999)
        
        if current_role_level < min_role_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This operation requires a minimum role of {min_role.value}"
            )
        
        return current_user
    
    return role_checker 