from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import complaints
from app.config import settings

# Creates tables on startup if they don't exist. For real migrations, use Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AIVOA Customer Complaint Management System",
    description="AI-powered complaint intake, triage, and CAPA assistant for pharma API/FDF manufacturing.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_origin,
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
