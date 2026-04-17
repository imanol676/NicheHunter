import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.db.base import Base

class ScanJob(Base):
    __tablename__ = "scan_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    niche_query = Column(String)
    subreddits = Column(ARRAY(String))
    status = Column(String, default="pending")
    posts_found = Column(Integer, default=0)
    pain_points_extracted = Column(Integer, default=0)
    filters = Column(JSONB)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)

    organization = relationship("Organization", back_populates="scan_jobs")
    raw_posts = relationship("RawPost", back_populates="scan_job")
    clusters = relationship("PainPointCluster", back_populates="scan_job")
