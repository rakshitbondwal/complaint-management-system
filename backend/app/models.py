import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, Enum, Float, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class RiskLevel(str, enum.Enum):
    CRITICAL = "Critical"
    MAJOR = "Major"
    MINOR = "Minor"
    UNCLASSIFIED = "Unclassified"


class ComplaintStatus(str, enum.Enum):
    DRAFT = "Draft"
    UNDER_REVIEW = "Under Review"
    LOGGED = "Logged"
    CLOSED = "Closed"


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Core complaint fields (populate the "Log Customer Complaint" form)
    customer_name = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    batch_number = Column(String(100), nullable=True)
    complaint_date = Column(String(50), nullable=True)
    complaint_text = Column(Text, nullable=False)
    source_type = Column(String(50), default="manual")  # manual | pdf | email

    # AI Copilot outputs
    completeness_score = Column(Float, default=0.0)
    missing_fields = Column(Text, nullable=True)  # JSON-encoded list
    risk_level = Column(Enum(RiskLevel), default=RiskLevel.UNCLASSIFIED)
    risk_justification = Column(Text, nullable=True)
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(UUID(as_uuid=True), ForeignKey("complaints.id"), nullable=True)
    duplicate_score = Column(Float, nullable=True)
    root_cause = Column(Text, nullable=True)  # JSON-encoded fishbone categories
    capa_recommendation = Column(Text, nullable=True)
    ai_summary = Column(Text, nullable=True)

    status = Column(Enum(ComplaintStatus), default=ComplaintStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
