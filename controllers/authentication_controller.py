from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.database import get_db
from repositories.user_repository import get_user_by_email, create_user, verify_password
from schemas.user_schemas import UserCreate, UserResponse, UserLogin
from schemas.authentication_schemas import create_access_token, create_refresh_token, get_current_user
router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", scheme_name="Bearer", scopes={"me": "Read information about the current user."}, )

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return create_user(db, user)

@router.post("/login")
async def login(form_data: UserLogin, db: Session = Depends(get_db)):
    user = get_user_by_email(db, form_data.email)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    return {"access_token": access_token, "refresh_token": refresh_token}

@router.post("/refresh")
async def refresh(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    user = await get_current_user(token, db)
    if(not user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token}

@router.post("/logout")
async def logout(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    return {"message": "Logged out successfully"}

@router.post("/me")
async def me(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    user = await get_current_user(token, db)
    return UserResponse.model_validate(user)
