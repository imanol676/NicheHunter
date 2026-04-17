import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    lemonsqueezy_customer_id = Column(String, unique=True)
    plan_tier = Column(String, default="Explorer")
    credits_remaining = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    subscriptions = relationship("Subscription", back_populates="organization")
    scan_jobs = relationship("ScanJob", back_populates="organization")
    saved_opportunities = relationship("SavedOpportunity", back_populates="organization")
