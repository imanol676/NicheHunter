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
