from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any

class ClusterBase(BaseModel):
    scan_job_id: Optional[UUID] = None
    label: str
    summary: Optional[str] = None
    size: int
    avg_severity_score: Optional[float] = None
    representative_samples: Optional[Dict[str, Any]] = None

class Cluster(ClusterBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
