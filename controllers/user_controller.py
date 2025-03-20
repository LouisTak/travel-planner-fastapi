from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.user_schemas import UserUpdate, UserChangePassword, UserResponse, UserRoleUpdate
from repositories.user_repository import update_user, change_password, update_user_role, get_all_users
from models.user import User, UserRole
from dependencies.auth import get_current_user
from typing import List

router = APIRouter(tags=["User"])

# Define a dependency for admin-only access
async def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this action. Admin role required."
        )
    return current_user

@router.post("/update-profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_user(db, user_update, current_user.id)

@router.post('/change-password', status_code=status.HTTP_200_OK)
async def update_password(
    user_pwd: UserChangePassword, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return change_password(db, user_pwd, current_user.id)

@router.get('/admin/users', response_model=List[UserResponse])
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return get_all_users(db)