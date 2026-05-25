from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

class PainPointBase(BaseModel):
    description: str
    category: str
    severity: str
    confidence_score: float
    frequency_count: Optional[int] = 1
    metadata: Optional[Dict[str, Any]] = None

class PainPoint(PainPointBase):
    id: UUID
    raw_post_id: Optional[UUID] = None
    cluster_id: Optional[UUID] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
