# Complaint Command — AI-Powered Customer Complaint Management System

An advanced AI-driven Quality Management System (QMS) intake, triage, and CAPA assistant tailored for pharmaceutical (API/FDF) manufacturing. Complaint Command automates the path from unstructured intake (emails, PDFs, text) to structured, compliant QMS logs with human-in-the-loop validation.

---

## Key Features

- **Automated AI Extraction**: Automatically parses customer name, product, batch number, date, and core issue summary.
- **Completeness Checker**: Calculates a completeness percentage based on regulatory and QMS requirements, highlighting missing fields.
- **AI Risk Classification**: Triages severity (Critical, Major, or Minor) using standard pharma QMS severity guidelines, complete with written justifications.
- **Duplicate Complaint Detection**: Matches incoming complaints against historical records using TF-IDF cosine similarity to flag potential batch-specific clusters.
- **Root Cause Recommendation (6M)**: Analyzes text using the 6M Fishbone framework (Man, Machine, Material, Method, Measurement, Environment) to output likelihoods and QA reasoning.
- **CAPA Recommendation**: Recommends immediate corrective actions and preventive actions based on risk and root cause.
- **Executive Summarization**: Drafts a concise 3-4 sentence summary suitable for QA review dashboards.

---

## Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + Redux Toolkit + Vite + Vanilla CSS |
| **Backend** | Python + FastAPI |
| **Orchestration** | LangGraph (StateGraph Workflow) |
| **LLMs** | Groq (`gemma2-9b-it` & `llama-3.3-70b-versatile` fallback) |
| **Database** | PostgreSQL (SQLAlchemy ORM) |

---

## Project Structure

```
complaint-management-system/
├── backend/
│   ├── app/
│   │   ├── main.py               FastAPI app entrypoint
│   │   ├── config.py             env-driven settings
│   │   ├── database.py           SQLAlchemy engine/session
│   │   ├── models.py             Complaint ORM model
│   │   ├── schemas.py            Pydantic request/response models
│   │   ├── routers/complaints.py API endpoints
│   │   ├── agents/
│   │   │   ├── state.py          LangGraph shared state (TypedDict)
│   │   │   ├── nodes.py          AI processing graph nodes
│   │   │   └── graph.py          StateGraph wiring & execution entrypoint
│   │   └── services/
│   │       ├── groq_client.py        Groq chat + JSON-mode helper
│   │       ├── document_parser.py    PDF/email/text extraction
│   │       └── duplicate_detector.py TF-IDF cosine similarity
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── main.jsx / App.jsx
│   │   ├── store/                Redux state management
│   │   ├── api/client.js         Axios client
│   │   ├── components/           FileUpload, ComplaintForm, AICopilotPanel, ComplaintList
│   │   └── styles/index.css      Vanilla CSS styling
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
├── sample-complaints/            Sample input files for testing (emails & texts)
└── render.yaml                   Render Blueprint file for deployment
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL running locally (or via Docker)
- A Groq API Key

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables. Copy `.env.example` to `.env` and fill in your keys:
   ```bash
   cp .env.example .env
   ```
5. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend will be running at `http://localhost:8000`. You can inspect the interactive API documentation at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173`.

---

## Production Deployment (Render)

This repository includes a `render.yaml` Blueprint to quickly deploy the frontend, backend, and database to **Render**.

1. Go to your **Render Dashboard** -> click **New +** -> **Blueprint**.
2. Connect your GitHub repository.
3. Supply the following environment variables when prompted:
   - `GROQ_API_KEY`: Your Groq API Key.
   - `VITE_API_BASE_URL`: The public URL of your backend web service (e.g. `https://your-backend.onrender.com`).
   - `FRONTEND_ORIGIN`: The public URL of your frontend static site (e.g. `https://your-frontend.onrender.com`).
4. Click **Apply** to deploy the services.
