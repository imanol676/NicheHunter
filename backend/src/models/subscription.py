import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    lemonsqueezy_subscription_id = Column(String, unique=True)
    status = Column(String)
    plan = Column(String)
    current_period_end = Column(DateTime)
    
    organization = relationship("Organization", back_populates="subscriptions")
