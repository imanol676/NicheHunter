from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class ScanJobBase(BaseModel):
    niche_query: str
    subreddits: List[str]
    filters: Optional[Dict[str, Any]] = None

class ScanJobCreate(ScanJobBase):
    org_id: UUID

class ScanJob(ScanJobBase):
    id: UUID
    org_id: UUID
    status: str
    posts_found: int
    pain_points_extracted: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)
