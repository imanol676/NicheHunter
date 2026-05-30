import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.db.base import Base

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("pain_point_clusters.id"))
    title = Column(String)
    problem_statement = Column(Text)
    market_analysis = Column(Text)
    proposed_solutions = Column(Text)
    monetization_ideas = Column(Text)
    competitive_landscape = Column(Text)
    opportunity_score = Column(Float)
    difficulty = Column(String)
    strategies = Column(JSONB)
    
    # Nuevas métricas avanzadas (DaaS)
    post_count = Column(Integer, default=1)
    total_upvotes = Column(Integer, default=0)
    sentiment = Column(String)
    urgency = Column(String)
    willingness_to_pay = Column(String)
    temporal_trends = Column(String)
    emerging_niches = Column(String)
    reddit_links = Column(JSONB, default=list)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    cluster = relationship("PainPointCluster", back_populates="opportunities")
    saved_by_orgs = relationship("SavedOpportunity", back_populates="opportunity")

    @property
    def niche(self):
        if self.cluster and self.cluster.scan_job:
            return self.cluster.scan_job.niche_query
        return "General"
