import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from src.db.base import Base

class PainPointCluster(Base):
    __tablename__ = "pain_point_clusters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_job_id = Column(UUID(as_uuid=True), ForeignKey("scan_jobs.id", ondelete="CASCADE"))
    label = Column(String)
    summary = Column(Text)
    size = Column(Integer)
    avg_severity_score = Column(Float)
    centroid = Column(Vector(3072))
    representative_samples = Column(JSONB)
    cluster_cohesion = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    scan_job = relationship("ScanJob", back_populates="clusters", lazy="selectin")
    pain_points = relationship("PainPoint", back_populates="cluster", cascade="all, delete-orphan", lazy="selectin")
    reports = relationship("ValidationReport", back_populates="cluster", cascade="all, delete-orphan", lazy="selectin")
