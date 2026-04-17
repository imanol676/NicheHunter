import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.db.base import Base

class RawPost(Base):
    __tablename__ = "raw_posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scan_job_id = Column(UUID(as_uuid=True), ForeignKey("scan_jobs.id"))
    reddit_id = Column(String, unique=True, index=True)
    subreddit = Column(String)
    title = Column(String)
    body = Column(Text)
    top_comments = Column(Text)
    score = Column(Integer)
    num_comments = Column(Integer)
    reddit_created_at = Column(DateTime)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    scan_job = relationship("ScanJob", back_populates="raw_posts")
    pain_points = relationship("PainPoint", back_populates="raw_post")
