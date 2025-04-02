from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.database import get_db
from schemas.user_schemas import UserCreate, UserResponse, UserLogin, UserChangePassword
from repositories.user_repository import (
    get_user_by_email,
    create_user,
    verify_password,
    change_password,
)
from dependencies.auth import (
    get_current_user,
    create_access_token,
    create_refresh_token,
)
from models.user import User
from datetime import timedelta
from typing import Dict, Any
from middleware.jwt_auth import (
    JWTBearer,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from fastapi import Response

router = APIRouter(tags=["Authentication"])

auth_bearer = JWTBearer()


@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    db_user = get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(user=user)


@router.post("/login")
async def login(user_data: UserLogin, response: Response):
    user = get_user_by_email(email=user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token = create_access_token(data={"sub": user.email})

    # Create refresh token
    refresh_token = create_refresh_token(data={"sub": user.email})

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "nickname": user.nickname,
            "role": user.role,
        },
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(credentials=Depends(auth_bearer)):
    current_user = await get_current_user(credentials)
    return current_user


@router.put("/change-password", status_code=status.HTTP_200_OK)
async def update_password(
    user_pwd: UserChangePassword, credentials=Depends(auth_bearer)
):
    current_user = await get_current_user(credentials)
    return change_password(user_pwd, current_user.id)


@router.post("/logout")
async def logout(response: Response, credentials=Depends(auth_bearer)):
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return {"message": "Logged out successfully"}


@router.post("/refresh-token")
async def refresh_token(credentials=Depends(auth_bearer)):
    current_user = await get_current_user(credentials)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": current_user.email})

    return {
        "access_token": access_token,
        "refresh_token": credentials,
        "token_type": "bearer",
    }
