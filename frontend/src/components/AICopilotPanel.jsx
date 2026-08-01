import React from "react";
import { useSelector } from "react-redux";

const RISK_CLASS = {
  Critical: "risk-critical",
  Major: "risk-major",
  Minor: "risk-minor",
  Unclassified: "risk-unclassified",
};

export default function AICopilotPanel() {
  const { aiAssessment, status } = useSelector((s) => s.complaints);

  if (status === "analyzing") {
    return (
      <div className="panel copilot-panel copilot-loading">
        <div className="panel-eyebrow">AI Copilot</div>
        <h2>Risk Assessment</h2>
        <div className="loading-pulse">Running extraction → completeness → risk → duplicate check → root cause → CAPA → summary…</div>
      </div>
    );
  }

  if (!aiAssessment) {
    return (
      <div className="panel copilot-panel copilot-empty">
        <div className="panel-eyebrow">AI Copilot</div>
        <h2>Risk Assessment</h2>
        <p className="panel-sub">Run an analysis on the left to see the AI's risk assessment, root cause, CAPA suggestion, and duplicate check here.</p>
      </div>
    );
  }

  const riskClass = RISK_CLASS[aiAssessment.risk_level] || "risk-unclassified";
  const completenessPct = Math.round((aiAssessment.completeness_score || 0) * 100);

  return (
    <div className={`panel copilot-panel ${riskClass}`}>
      <div className="panel-eyebrow">AI Copilot</div>
      <h2>Risk Assessment</h2>

      <div className="risk-badge-row">
        <span className={`risk-badge ${riskClass}`}>{aiAssessment.risk_level}</span>
        <div className="completeness-meter" title={`${completenessPct}% complete`}>
          <div className="completeness-track">
            <div className="completeness-fill" style={{ width: `${completenessPct}%` }} />
          </div>
          <span className="completeness-label">{completenessPct}% complete</span>
        </div>
      </div>

      <p className="risk-justification">{aiAssessment.risk_justification}</p>

      {aiAssessment.missing_fields?.length > 0 && (
        <div className="alert alert-amber">
          Missing required fields: {aiAssessment.missing_fields.join(", ")}
        </div>
      )}

      {aiAssessment.duplicates?.length > 0 && (
        <div className="alert alert-red">
          Possible duplicate of {aiAssessment.duplicates.length} existing complaint(s) — top match{" "}
          {Math.round(aiAssessment.duplicates[0].similarity * 100)}% similar.
        </div>
      )}

      <section className="copilot-section">
        <h3>Root Cause (6M)</h3>
        <ul className="root-cause-list">
          {aiAssessment.root_cause?.map((rc, i) => (
            <li key={i}>
              <span className={`likelihood-dot likelihood-${rc.likelihood?.toLowerCase()}`} />
              <strong>{rc.category}</strong> ({rc.likelihood}) — {rc.reasoning}
            </li>
          ))}
        </ul>
      </section>

      <section className="copilot-section">
        <h3>CAPA Recommendation</h3>
        <p>{aiAssessment.capa_recommendation}</p>
      </section>

      <section className="copilot-section">
        <h3>Summary</h3>
        <p>{aiAssessment.ai_summary}</p>
      </section>
    </div>
  );
}
