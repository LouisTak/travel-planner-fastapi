import uuid 
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from database.database import Base, get_db
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    nickname = Column(String(80), nullable=True)
    hashed_password = Column(String(256), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    travel_plans = relationship("TravelPlan", back_populates="user")
    
    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
        
    def check_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == email).first()
