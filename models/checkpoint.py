from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Time
from sqlalchemy.orm import relationship
from database.database import Base
import uuid
from datetime import datetime

class Checkpoint(Base):
    __tablename__ = "checkpoints"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    travel_plan_day_id = Column(String, ForeignKey("travel_plan_days.id"))
    travel_plan_day = relationship("TravelPlanDay", back_populates="checkpoints")
    location = Column(String(200), nullable=True)
    activity = Column(Text, nullable=True)
    tips = Column(Text, nullable=True)
    start_at = Column(Time, nullable=True)
    end_at = Column(Time, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
