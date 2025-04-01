import uuid 
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from database.database import Base, get_db
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from models.user_role import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    nickname = Column(String(80), nullable=True)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(20), nullable=False, default=UserRole.get_default())
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    travel_plans = relationship("TravelPlan", back_populates="user")
    
    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
        
    def check_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)
    
    def has_role(self, role: str) -> bool:
        """Check if the user has a specific role."""
        return self.role == role
    
    def is_admin(self) -> bool:
        """Check if the user is an admin."""
        return self.role == UserRole.ADMIN.value
    
    def is_premium(self) -> bool:
        """Check if the user has premium access."""
        return self.role in [UserRole.PREMIUM.value, UserRole.ADMIN.value]

def get_user_by_email(email: str):
    db = next(get_db())
    return db.query(User).filter(User.email == email).first()
