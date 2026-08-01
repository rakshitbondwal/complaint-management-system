from app.agents.state import ComplaintState
from app.services.groq_client import chat_json
from app.services.duplicate_detector import find_duplicates

REQUIRED_FIELDS = ["customer_name", "product_name", "batch_number", "complaint_date"]


def extract_complaint_data(state: ComplaintState) -> ComplaintState:
    """Node 1: pull structured fields out of raw complaint text (from form, PDF, or email)."""
    system = (
        "You are a pharmaceutical quality assurance assistant. Extract structured fields "
        "from a raw customer complaint (which may come from an email, PDF, or manual entry) "
        "about an API (active pharmaceutical ingredient) or FDF (finished dosage form) product."
    )
    user = f"""
Complaint text:
---
{state['raw_text']}
---

Extract these fields as JSON:
{{
  "customer_name": string or null,
  "product_name": string or null,
  "batch_number": string or null,
  "complaint_date": string or null (ISO format if determinable, else as written),
  "complaint_summary_line": string (one line describing the core issue)
}}
If a field is not present in the text, use null. Do not invent values.
"""
    result = chat_json(system, user)
    state["customer_name"] = result.get("customer_name")
    state["product_name"] = result.get("product_name")
    state["batch_number"] = result.get("batch_number")
    state["complaint_date"] = result.get("complaint_date")
    state["complaint_summary_line"] = result.get("complaint_summary_line")
    return state


def completeness_checker(state: ComplaintState) -> ComplaintState:
    """Node 2: flag which mandatory QMS complaint fields are missing."""
    missing = [f for f in REQUIRED_FIELDS if not state.get(f)]
    score = round((len(REQUIRED_FIELDS) - len(missing)) / len(REQUIRED_FIELDS), 2)
    state["missing_fields"] = missing
    state["completeness_score"] = score
    return state


def risk_classification(state: ComplaintState) -> ComplaintState:
    """Node 3: classify complaint severity per typical pharma QMS risk tiers."""
    system = (
        "You are a QA risk assessor for a pharmaceutical manufacturer (API/FDF). Classify complaint "
        "severity using standard QMS conventions:\n"
        "- Critical: patient safety risk, adverse event, contamination, mislabeling that could cause harm\n"
        "- Major: product quality defect impacting efficacy/GMP compliance but no immediate safety risk\n"
        "- Minor: cosmetic, packaging, documentation, or service issues with no quality/safety impact"
    )
    user = f"""
Complaint text:
---
{state['raw_text']}
---

Respond as JSON:
{{
  "risk_level": "Critical" | "Major" | "Minor",
  "risk_justification": string (2-3 sentences citing what in the complaint drove the classification)
}}
"""
    result = chat_json(system, user)
    state["risk_level"] = result.get("risk_level", "Unclassified")
    state["risk_justification"] = result.get("risk_justification", "")
    return state


def duplicate_detection(state: ComplaintState) -> ComplaintState:
    """Node 4: compare against previously logged complaints using TF-IDF cosine similarity."""
    existing = state.get("existing_complaints", [])
    state["duplicates"] = find_duplicates(state["raw_text"], existing)
    return state


def root_cause_recommendation(state: ComplaintState) -> ComplaintState:
    """Node 5 (bonus): suggest likely root cause categories using a fishbone (6M) framework."""
    system = (
        "You are a QA investigator using the fishbone (6M) root cause framework "
        "(Man, Machine, Material, Method, Measurement, Environment) for a pharmaceutical complaint."
    )
    user = f"""
Complaint text:
---
{state['raw_text']}
---

Suggest the top 2-3 most likely root cause categories as JSON:
{{
  "root_cause": [
    {{"category": "Material" | "Man" | "Machine" | "Method" | "Measurement" | "Environment",
      "likelihood": "High" | "Medium" | "Low",
      "reasoning": string}}
  ]
}}
"""
    result = chat_json(system, user)
    state["root_cause"] = result.get("root_cause", [])
    return state


def capa_recommendation(state: ComplaintState) -> ComplaintState:
    """Node 6 (bonus): draft Corrective and Preventive Action recommendations."""
    system = (
        "You are a QA specialist drafting a CAPA (Corrective and Preventive Action) recommendation "
        "for a pharmaceutical manufacturing complaint, following standard QMS practice."
    )
    root_cause_text = ", ".join(rc.get("category", "") for rc in state.get("root_cause", [])) or "unknown"
    user = f"""
Complaint text:
---
{state['raw_text']}
---
Risk level: {state.get('risk_level')}
Likely root cause categories: {root_cause_text}

Respond as JSON:
{{
  "capa_recommendation": string (a short, actionable CAPA plan: immediate correction + preventive action)
}}
"""
    result = chat_json(system, user)
    state["capa_recommendation"] = result.get("capa_recommendation", "")
    return state


def complaint_summary(state: ComplaintState) -> ComplaintState:
    """Node 7 (bonus): produce a concise summary for the AI Copilot panel."""
    system = "You write concise QA-ready summaries of pharmaceutical customer complaints."
    user = f"""
Complaint text:
---
{state['raw_text']}
---
Extracted product: {state.get('product_name')}, batch: {state.get('batch_number')}
Risk level: {state.get('risk_level')}

Respond as JSON:
{{
  "ai_summary": string (3-4 sentence executive summary suitable for a QA review dashboard)
}}
"""
    result = chat_json(system, user)
    state["ai_summary"] = result.get("ai_summary", "")
    return state
