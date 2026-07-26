import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.db.base import Base

class ValidationReport(Base):
    __tablename__ = "validation_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id = Column(UUID(as_uuid=True), ForeignKey("pain_point_clusters.id", ondelete="CASCADE"))
    
    # B2B Validation Metrics
    report_title = Column(String)
    friction_summary = Column(Text)
    cost_of_inaction = Column(Text)
    audience_profile = Column(String)
    existing_alternatives = Column(Text)
    competitor_gaps = Column(Text)
    trend_velocity = Column(String)
    risk_profile = Column(Text)
    willingness_to_pay = Column(String)
    validation_verdict = Column(String)
    
    # Evidence & Quotes
    top_pain_points = Column(JSONB, default=list)
    representative_quotes = Column(JSONB, default=list)
    
    # Scoring
    demand_score = Column(Float, default=0.0)
    pain_severity_score = Column(Float, default=0.0)
    competition_score = Column(Float, default=0.0)
    overall_confidence_score = Column(Float, default=0.0)
    opportunity_score = Column(Float, default=0.0)
    
    # Strategy
    strategic_recommendations = Column(JSONB, default=list)
    opportunity_why = Column(JSONB, default=list)
    recommended_positioning = Column(Text)
    mvp_features = Column(JSONB, default=list)
    
    # Quantitative Validation
    market_size_tam = Column(String, default="Analyzing...")
    market_growth_cagr = Column(String, default="Analyzing...")
    
    # Raw stats
    post_count = Column(Integer, default=1)
    total_upvotes = Column(Integer, default=0)
    total_comments = Column(Integer, default=0)
    source_links = Column(JSONB, default=list)
    tam_cagr_sources = Column(JSONB, default=list)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    cluster = relationship("PainPointCluster", back_populates="reports", lazy="selectin")

    @property
    def niche(self):
        if self.cluster and self.cluster.scan_job:
            return self.cluster.scan_job.niche_query
        return "General"
