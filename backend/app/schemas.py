import uuid
from typing import Optional, List
from datetime import datetime

from pydantic import BaseModel


class ComplaintAnalyzeRequest(BaseModel):
    raw_text: str
    source_type: str = "manual"


class DuplicateMatch(BaseModel):
    id: str
    similarity: float
    complaint_text: str


class RootCauseSuggestion(BaseModel):
    category: str  # Man / Machine / Material / Method / Environment / Measurement
    likelihood: str  # High / Medium / Low
    reasoning: str


class ComplaintAnalysisResponse(BaseModel):
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    batch_number: Optional[str] = None
    complaint_date: Optional[str] = None
    complaint_text: str

    completeness_score: float
    missing_fields: List[str] = []

    risk_level: str
    risk_justification: str

    duplicates: List[DuplicateMatch] = []

    root_cause: List[RootCauseSuggestion] = []
    capa_recommendation: str
    ai_summary: str


class ComplaintCreate(BaseModel):
    customer_name: Optional[str] = None
    product_name: Optional[str] = None
    batch_number: Optional[str] = None
    complaint_date: Optional[str] = None
    complaint_text: str
    source_type: str = "manual"

    completeness_score: float = 0.0
    missing_fields: Optional[List[str]] = None
    risk_level: str = "Unclassified"
    risk_justification: Optional[str] = None
    is_duplicate: bool = False
    duplicate_of_id: Optional[str] = None
    duplicate_score: Optional[float] = None
    root_cause: Optional[List[RootCauseSuggestion]] = None
    capa_recommendation: Optional[str] = None
    ai_summary: Optional[str] = None


class ComplaintOut(BaseModel):
    id: uuid.UUID
    customer_name: Optional[str]
    product_name: Optional[str]
    batch_number: Optional[str]
    complaint_date: Optional[str]
    complaint_text: str
    source_type: str
    completeness_score: float
    risk_level: str
    risk_justification: Optional[str]
    is_duplicate: bool
    duplicate_score: Optional[float]
    capa_recommendation: Optional[str]
    ai_summary: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
