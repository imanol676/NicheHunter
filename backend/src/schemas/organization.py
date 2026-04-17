from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class OrganizationBase(BaseModel):
    name: str
    lemonsqueezy_customer_id: Optional[str] = None
    plan_tier: str = "Explorer"
    credits_remaining: int = 0

class OrganizationCreate(OrganizationBase):
    pass

class Organization(OrganizationBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
