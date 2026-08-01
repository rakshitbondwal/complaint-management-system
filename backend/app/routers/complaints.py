import json
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.agents.graph import run_complaint_pipeline
from app.services.document_parser import extract_text_from_upload

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


def _existing_texts(db: Session) -> List[tuple]:
    rows = db.query(models.Complaint.id, models.Complaint.complaint_text).all()
    return [(str(r[0]), r[1]) for r in rows]


def _run_pipeline_and_build_response(raw_text: str, db: Session) -> schemas.ComplaintAnalysisResponse:
    result = run_complaint_pipeline(raw_text, _existing_texts(db))
    return schemas.ComplaintAnalysisResponse(
        customer_name=result.get("customer_name"),
        product_name=result.get("product_name"),
        batch_number=result.get("batch_number"),
        complaint_date=result.get("complaint_date"),
        complaint_text=raw_text,
        completeness_score=result.get("completeness_score", 0.0),
        missing_fields=result.get("missing_fields", []),
        risk_level=result.get("risk_level", "Unclassified"),
        risk_justification=result.get("risk_justification", ""),
        duplicates=[schemas.DuplicateMatch(**d) for d in result.get("duplicates", [])],
        root_cause=[schemas.RootCauseSuggestion(**rc) for rc in result.get("root_cause", [])],
        capa_recommendation=result.get("capa_recommendation", ""),
        ai_summary=result.get("ai_summary", ""),
    )


@router.post("/analyze/text", response_model=schemas.ComplaintAnalysisResponse)
def analyze_text_complaint(payload: schemas.ComplaintAnalyzeRequest, db: Session = Depends(get_db)):
    """Runs the LangGraph AI pipeline over manually typed complaint text."""
    if not payload.raw_text.strip():
        raise HTTPException(status_code=400, detail="Complaint text cannot be empty.")
    return _run_pipeline_and_build_response(payload.raw_text, db)


@router.post("/analyze/upload", response_model=schemas.ComplaintAnalysisResponse)
async def analyze_uploaded_complaint(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Runs the LangGraph AI pipeline over an uploaded PDF/email/text file."""
    file_bytes = await file.read()
    raw_text = extract_text_from_upload(file.filename, file_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="Could not extract any text from the uploaded file.")
    return _run_pipeline_and_build_response(raw_text, db)


@router.post("/", response_model=schemas.ComplaintOut)
def save_complaint(payload: schemas.ComplaintCreate, db: Session = Depends(get_db)):
    """Persists a reviewed complaint (post AI-assist, after human confirms the form)."""
    complaint = models.Complaint(
        customer_name=payload.customer_name,
        product_name=payload.product_name,
        batch_number=payload.batch_number,
        complaint_date=payload.complaint_date,
        complaint_text=payload.complaint_text,
        source_type=payload.source_type,
        completeness_score=payload.completeness_score,
        missing_fields=json.dumps(payload.missing_fields or []),
        risk_level=payload.risk_level,
        risk_justification=payload.risk_justification,
        is_duplicate=payload.is_duplicate,
        duplicate_of_id=uuid.UUID(payload.duplicate_of_id) if payload.duplicate_of_id else None,
        duplicate_score=payload.duplicate_score,
        root_cause=json.dumps([rc.model_dump() for rc in payload.root_cause] if payload.root_cause else []),
        capa_recommendation=payload.capa_recommendation,
        ai_summary=payload.ai_summary,
        status=models.ComplaintStatus.LOGGED,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("/", response_model=List[schemas.ComplaintOut])
def list_complaints(db: Session = Depends(get_db)):
    return db.query(models.Complaint).order_by(models.Complaint.created_at.desc()).all()


@router.get("/{complaint_id}", response_model=schemas.ComplaintOut)
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(models.Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found.")
    return complaint
