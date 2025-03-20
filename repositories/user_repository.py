from sqlalchemy.orm import Session
from models.user import User
from schemas.user_schemas import UserCreate, UserChangePassword, UserUpdate
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        nickname=user.nickname,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def change_password(db: Session, user_data: UserChangePassword):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user_data.old_password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect old password")
    user.hashed_password = pwd_context.hash(user_data.new_password)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_data: UserUpdate):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_data.nickname is not None:
        user.nickname = user_data.nickname
    db.commit()
    db.refresh(user)
    return user