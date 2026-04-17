from pydantic import BaseModel
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
