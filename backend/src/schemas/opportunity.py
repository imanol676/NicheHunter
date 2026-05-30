from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class OpportunityBase(BaseModel):
    title: str
    problem_statement: str
    market_analysis: str
    proposed_solutions: str
    monetization_ideas: str
    competitive_landscape: str
    opportunity_score: float
    difficulty: str
    strategies: Optional[List[str]] = None
    post_count: Optional[int] = 1
    total_upvotes: Optional[int] = 0
    sentiment: Optional[str] = None
    urgency: Optional[str] = None
    willingness_to_pay: Optional[str] = None
    niche: Optional[str] = None
    temporal_trends: Optional[str] = None
    emerging_niches: Optional[str] = None
    reddit_links: Optional[List[str]] = []

class OpportunityCreate(OpportunityBase):
    cluster_id: UUID

class Opportunity(OpportunityBase):
    id: UUID
    cluster_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
