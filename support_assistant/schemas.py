from pydantic import BaseModel, Field
from typing import List

class AskRequest(BaseModel):
    query: str

class AskResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float = Field(ge=0.0, le=1.0)

