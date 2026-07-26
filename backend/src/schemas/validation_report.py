from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class ValidationReportBase(BaseModel):
    report_title: Optional[str] = None
    friction_summary: Optional[str] = None
    cost_of_inaction: Optional[str] = None
    audience_profile: Optional[str] = None
    existing_alternatives: Optional[str] = None
    competitor_gaps: Optional[str] = None
    trend_velocity: Optional[str] = None
    risk_profile: Optional[str] = None
    willingness_to_pay: Optional[str] = None
    validation_verdict: Optional[str] = None
    
    # Evidence & Quotes
    top_pain_points: Optional[List[Dict[str, Any]]] = []
    representative_quotes: Optional[List[str]] = []
    
    # Scoring
    demand_score: Optional[float] = 0.0
    pain_severity_score: Optional[float] = 0.0
    competition_score: Optional[float] = 0.0
    overall_confidence_score: Optional[float] = 0.0
    opportunity_score: Optional[float] = 0.0
    
    # Strategy
    strategic_recommendations: Optional[List[str]] = []
    opportunity_why: Optional[List[str]] = []
    recommended_positioning: Optional[str] = None
    mvp_features: Optional[List[str]] = []
    
    market_size_tam: Optional[str] = None
    market_growth_cagr: Optional[str] = None
    tam_cagr_sources: Optional[List[str]] = []
    
    post_count: Optional[int] = 1
    total_upvotes: Optional[int] = 0
    total_comments: Optional[int] = 0
    source_links: Optional[List[str]] = []
    niche: Optional[str] = None

class ValidationReportCreate(ValidationReportBase):
    cluster_id: UUID

class ValidationReport(ValidationReportBase):
    id: UUID
    cluster_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
