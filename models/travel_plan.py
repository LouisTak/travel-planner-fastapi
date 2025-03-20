from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime

class TravelPlan(Base):
    __tablename__ = "travel_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    user = relationship("User", back_populates="travel_plans")
    title = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=False)
    remarks = Column(Text, nullable=True)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with TravelPlanDay
    travel_plan_days = relationship("TravelPlanDay", back_populates="travel_plan", cascade="all, delete-orphan")