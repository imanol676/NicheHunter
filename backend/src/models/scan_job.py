import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.db.base import Base

class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    niche_query = Column(String) # Mantenemos esto por retrocompatibilidad o combinaciones
    target_industry = Column(String, nullable=True)
    business_process = Column(String, nullable=True)
    subreddits = Column(ARRAY(String))
    competitors = Column(ARRAY(String), default=list)
    status = Column(String, default="pending")
    posts_found = Column(Integer, default=0)
    pain_points_extracted = Column(Integer, default=0)
    phase = Column(String, default="exploration")
    cost_coins = Column(Integer, default=0)
    filters = Column(JSONB)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))
    completed_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="scan_jobs", lazy="selectin")
    user = relationship("User", backref="scan_jobs", lazy="selectin")
    raw_posts = relationship("RawPost", back_populates="scan_job", cascade="all, delete-orphan", lazy="selectin")
    clusters = relationship("PainPointCluster", back_populates="scan_job", cascade="all, delete-orphan", lazy="selectin")
