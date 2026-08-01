from langgraph.graph import StateGraph, END

from app.agents.state import ComplaintState
from app.agents import nodes


def build_complaint_graph():
    graph = StateGraph(ComplaintState)

    graph.add_node("extract_complaint_data", nodes.extract_complaint_data)
    graph.add_node("completeness_checker", nodes.completeness_checker)
    graph.add_node("risk_classification", nodes.risk_classification)
    graph.add_node("duplicate_detection", nodes.duplicate_detection)
    graph.add_node("root_cause_recommendation", nodes.root_cause_recommendation)
    graph.add_node("generate_capa_recommendation", nodes.capa_recommendation)
    graph.add_node("complaint_summary", nodes.complaint_summary)

    graph.set_entry_point("extract_complaint_data")
    graph.add_edge("extract_complaint_data", "completeness_checker")
    graph.add_edge("completeness_checker", "risk_classification")
    graph.add_edge("risk_classification", "duplicate_detection")
    graph.add_edge("duplicate_detection", "root_cause_recommendation")
    graph.add_edge("root_cause_recommendation", "generate_capa_recommendation")
    graph.add_edge("generate_capa_recommendation", "complaint_summary")
    graph.add_edge("complaint_summary", END)
    
    return graph.compile()


# compiled once at import time, reused across requests
complaint_pipeline = build_complaint_graph()


def run_complaint_pipeline(raw_text: str, existing_complaints: list[tuple[str, str]]) -> ComplaintState:
    initial_state: ComplaintState = {
        "raw_text": raw_text,
        "existing_complaints": existing_complaints,
    }
    final_state = complaint_pipeline.invoke(initial_state)
    return final_state
