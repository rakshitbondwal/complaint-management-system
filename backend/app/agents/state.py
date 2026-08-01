from typing import TypedDict, List, Optional, Tuple


class ComplaintState(TypedDict, total=False):
    # input
    raw_text: str
    existing_complaints: List[Tuple[str, str]]  # (id, text) pairs already in DB, for duplicate check

    # extract_complaint_data
    customer_name: Optional[str]
    product_name: Optional[str]
    batch_number: Optional[str]
    complaint_date: Optional[str]
    complaint_summary_line: Optional[str]

    # completeness_checker
    completeness_score: float
    missing_fields: List[str]

    # risk_classification
    risk_level: str
    risk_justification: str

    # duplicate_detection
    duplicates: List[dict]

    # root_cause_recommendation
    root_cause: List[dict]

    # capa_recommendation
    capa_recommendation: str

    # complaint_summary
    ai_summary: str
