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
    source_id = Column(String, unique=True, index=True) # Ex reddit_id
    source_platform = Column(String, default="reddit") # 'reddit', 'hackernews', 'youtube'
    source_community = Column(String) # Ex subreddit (or tag/search query)
    title = Column(String)
    body = Column(Text)
    top_comments = Column(Text)
    engagement_score = Column(Integer) # Ex score (upvotes, likes)
    reply_count = Column(Integer) # Ex num_comments
    source_created_at = Column(DateTime) # Ex reddit_created_at
    url = Column(String)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    scan_job = relationship("ScanJob", back_populates="raw_posts", lazy="selectin")
    pain_points = relationship("PainPoint", back_populates="raw_post", cascade="all, delete-orphan", lazy="selectin")
