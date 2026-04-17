import os

schemas_code = {
    "user.py": """from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    clerk_id: str
    email: str
    name: Optional[str] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
""",
    "organization.py": """from pydantic import BaseModel, ConfigDict
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
""",
    "subscription.py": """from pydantic import BaseModel, ConfigDict
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
""",
    "scan.py": """from pydantic import BaseModel, ConfigDict
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
""",
    "brainstorm.py": """from pydantic import BaseModel
from uuid import UUID
from typing import List, Dict, Any

class Message(BaseModel):
    role: str
    content: str

class BrainstormRequest(BaseModel):
    opportunity_id: UUID
    messages: List[Message]

class BrainstormResponse(BaseModel):
    reply: str
""",
    "opportunity.py": """from pydantic import BaseModel, ConfigDict
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
"""
}

SCHEMAS_DIR = "c:\\Users\\imano\\OneDrive\\Escritorio\\proyectos\\painpoint_scraper\\backend\\src\\schemas"
os.makedirs(SCHEMAS_DIR, exist_ok=True)

for filename, content in schemas_code.items():
    with open(os.path.join(SCHEMAS_DIR, filename), "w", encoding="utf-8") as f:
        f.write(content)

init_content = ""
for filename in schemas_code.keys():
    module_name = filename.replace(".py", "")
    with open(os.path.join(SCHEMAS_DIR, filename), "r", encoding="utf-8") as rf:
        content = rf.read()
        for line in content.split('\\n'):
            if line.startswith("class "):
                class_name = line.replace("class ", "").split("(")[0].strip()
                init_content += f"from .{module_name} import {class_name}\\n"

with open(os.path.join(SCHEMAS_DIR, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(init_content)

print("Schemas generated successfully!")
