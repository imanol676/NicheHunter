from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class SubscriptionBase(BaseModel):
    lemonsqueezy_subscription_id: str
    status: str
    plan: str
    current_period_end: datetime

class SubscriptionCreate(SubscriptionBase):
    org_id: UUID

class Subscription(SubscriptionBase):
    id: UUID
    org_id: UUID
    model_config = ConfigDict(from_attributes=True)
