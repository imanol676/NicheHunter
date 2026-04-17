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
    strategies: Optional[Dict[str, Any]] = None

class OpportunityCreate(OpportunityBase):
    cluster_id: UUID

class Opportunity(OpportunityBase):
    id: UUID
    cluster_id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
