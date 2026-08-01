# Complaint Command — AI-Powered Customer Complaint Management System

Built for the AIVOA Round 1 AI Product Engineer assignment. Pharma (API/FDF) customer
complaint intake → AI extraction → completeness check → risk classification → duplicate
detection → root cause (6M fishbone) → CAPA recommendation → summary, surfaced through
a "Log Customer Complaint" form and an "AI Copilot Risk Assessment" panel.

## Stack

| Layer | Tech |
|---|---|
| Frontend | React 18 + Redux Toolkit + Vite |
| Backend | Python + FastAPI |
| AI Agent Orchestration | LangGraph |
| LLM | Groq — `gemma2-9b-it` (fallback `llama-3.3-70b-versatile`) |
| Database | PostgreSQL (SQLAlchemy ORM — MySQL is a one-line swap, see below) |
| Font | Google Inter / Inter Tight |

## Repo layout

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
│   │   │   ├── nodes.py          each AI step as a graph node
│   │   │   └── graph.py          StateGraph wiring + entrypoint fn
│   │   └── services/
│   │       ├── groq_client.py        Groq chat + JSON-mode helper
│   │       ├── document_parser.py    PDF/email/text extraction
│   │       └── duplicate_detector.py TF-IDF cosine similarity
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.jsx / App.jsx
│   │   ├── store/                Redux slice + store
│   │   ├── api/client.js         axios instance
│   │   ├── components/           FileUpload, ComplaintForm, AICopilotPanel, ComplaintList
│   │   └── styles/index.css
│   ├── index.html
│   ├── vite.config.js
│   └── package.json
└── sample-complaints/            demo input files (email/text, incl. a duplicate pair)
```

## How the AI pipeline works (LangGraph)

`backend/app/agents/graph.py` wires seven nodes into a linear `StateGraph`:

```
extract_complaint_data → completeness_checker → risk_classification
→ duplicate_detection → root_cause_recommendation → capa_recommendation
→ complaint_summary → END
```

Each node reads/writes a shared `ComplaintState` TypedDict. The extraction, risk,
root-cause, CAPA, and summary nodes call Groq's `gemma2-9b-it` via
`services/groq_client.chat_json`, which forces JSON-only output and retries once on
`llama-3.3-70b-versatile` if the smaller model returns malformed JSON. Duplicate
detection deliberately uses TF-IDF + cosine similarity against complaints already in
Postgres (no external vector DB needed) — fast, explainable, and enough for the demo
scope.

## 1. Environment setup

### Install VS Code + extensions
1. Install [VS Code](https://code.visualstudio.com/).
2. Install extensions: **Python** (ms-python.python), **Pylance**, **ES7+ React/Redux
   snippets**, **Prettier**, and optionally **Thunder Client** (for testing the API).
3. Open the `complaint-management-system` folder as your VS Code workspace
   (`code complaint-management-system`).

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 14+ running locally (or use Docker — see below)
- A free Groq API key: https://console.groq.com/keys

### Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: paste your GROQ_API_KEY, set DATABASE_URL

# create the database (psql example)
createdb complaints_db

uvicorn app.main:app --reload --port 8000
```
Backend now runs at `http://localhost:8000`. Interactive API docs at
`http://localhost:8000/docs`.

**Using MySQL instead of Postgres:** install `pip install pymysql` instead of
`psycopg2-binary`, and set `DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/complaints_db`
in `.env`. Nothing else changes — SQLAlchemy abstracts the rest.

**No local Postgres? Quick Docker option:**
```bash
docker run --name complaints-pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=complaints_db -p 5432:5432 -d postgres:16
```

### Frontend setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://localhost:5173` and calls the backend at
`http://localhost:8000` (override with a `VITE_API_BASE_URL` env var if needed).

## 2. Demo workflow (for your walkthrough video)

1. Start backend (`uvicorn ...`) and frontend (`npm run dev`).
2. Open `http://localhost:5173`.
3. In the **Intake** panel, paste text from `sample-complaints/complaint_critical_email.txt`
   (or upload it as a `.txt`/`.pdf`) and click **Run AI Analysis**.
4. Watch the **Log Customer Complaint** form auto-populate (customer, product, batch,
   date) and the **AI Copilot Risk Assessment** panel show: risk tier + justification,
   completeness %, missing fields, root cause (6M), CAPA recommendation, and summary.
5. Click **Log Complaint** to persist it.
6. Paste `complaint_duplicate_test.txt` next — it references the same batch as the
   first complaint, so the AI Copilot should flag it as a likely duplicate.
7. Try `complaint_minor_manual.txt` to show a Minor-risk classification (packaging
   issue, no safety impact) for contrast against the Critical one.

For your code walkthrough video, trace one request end-to-end:
`FileUpload.jsx` → `analyzeComplaintText` thunk (`complaintsSlice.js`) → axios POST
`/api/complaints/analyze/text` → `routers/complaints.py` →
`agents/graph.run_complaint_pipeline` → each node in `agents/nodes.py` → response
shape in `schemas.py` → Redux `applyAnalysis` reducer → `ComplaintForm.jsx` /
`AICopilotPanel.jsx` re-render.

## 3. Bonus AI features implemented

- **Complaint Completeness Checker** — flags missing mandatory fields, shown as a %
  meter in the AI Copilot panel.
- **AI Risk Classification** — Critical / Major / Minor per standard QMS severity
  conventions, with a written justification.
- **Duplicate Complaint Detection** — TF-IDF cosine similarity against previously
  logged complaints.
- **Root Cause Recommendation** — 6M fishbone (Man/Machine/Material/Method/
  Measurement/Environment) categories with likelihood + reasoning.
- **CAPA Recommendation** — drafted corrective + preventive action plan.
- **Complaint Summary** — QA-dashboard-ready executive summary.

## Notes on scope

- OCR/document parsing uses `pypdf` text extraction — good enough for text-based PDFs,
  not scanned-image OCR (explicitly out of scope per the assignment brief).
- No Alembic migrations — `Base.metadata.create_all()` creates tables on first run,
  which is appropriate for an assignment-scope project.
- Every field extracted by the LLM is shown in an editable form field before saving,
  so a human QA reviewer always confirms before it's logged — matching how the demo
  video's "Log Customer Complaint" step behaves as a human-in-the-loop checkpoint.
