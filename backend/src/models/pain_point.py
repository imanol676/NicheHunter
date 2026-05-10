import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import relationship
from src.db.base import Base

class PainPoint(Base):
    __tablename__ = "pain_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    raw_post_id = Column(UUID(as_uuid=True), ForeignKey("raw_posts.id"))
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("pain_point_clusters.id"), nullable=True)
    description = Column(Text)
    embedding = Column(Vector(1536))
    category = Column(String)
    severity = Column(String)
    confidence_score = Column(Float)
    frequency_count = Column(Integer, default=1)
    metadata_ = Column("metadata", JSONB)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    raw_post = relationship("RawPost", back_populates="pain_points")
    cluster = relationship("PainPointCluster", back_populates="pain_points")
