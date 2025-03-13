from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime

class TravelPlanDay(Base):
    __tablename__ = "travel_plan_days"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    travel_plan_id = Column(String, ForeignKey("travel_plans.id"))
    travel_plan = relationship("TravelPlan", back_populates="travel_plan_days")
    day_number = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    reminder = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
