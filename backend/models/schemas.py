from pydantic import BaseModel, Field
from typing import List, Dict, Any

class AnalyzeRequest(BaseModel):
    message: str = Field(..., min_length=1)
    language: str = "en"

class AnalyzeResponse(BaseModel):
    category: str
    intent: str
    language: str
    missing_information: List[str]


class DraftRequest(BaseModel):
    category: str
    information: dict[str,Any]
    language: str = "en"


class DraftResponse(BaseModel):
    title: str
    content: str
    language: str