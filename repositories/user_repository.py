from sqlalchemy.orm import Session
from models.user import User, UserRole
from schemas.user_schemas import UserCreate, UserChangePassword, UserUpdate
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from typing import List
from database.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(username: str):
    db = next(get_db())
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(email: str):
    db = next(get_db())
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(user_id: int):
    db = next(get_db())
    return db.query(User).filter(User.id == user_id).first()

def create_user(user: UserCreate):
    db = next(get_db())
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        nickname=user.nickname,
        hashed_password=hashed_password,
        role=UserRole.FREE.value
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def change_password(user_data: UserChangePassword, user_id: int):
    db = next(get_db())
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user_data.old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect old password")
    user.hashed_password = pwd_context.hash(user_data.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password updated successfully"}

def update_user(user_data: UserUpdate, user_id: int):
    db = next(get_db())
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_data.nickname is not None:
        user.nickname = user_data.nickname
    db.commit()
    db.refresh(user)
    return user

def update_user_role(user_id: int, role: str):
    db = next(get_db())
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate that the role is a valid UserRole value
    try:
        user_role = UserRole(role)
        user.role = user_role.value
        db.commit()
        db.refresh(user)
        return user
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")

def get_all_users() -> List[User]:
    db = next(get_db())
    return db.query(User).all()