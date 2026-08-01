import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { updateFormField, saveComplaint, resetForm } from "../store/complaintsSlice.js";

const FIELDS = [
  { key: "customer_name", label: "Customer / Site Name" },
  { key: "product_name", label: "Product Name" },
  { key: "batch_number", label: "Batch / Lot Number" },
  { key: "complaint_date", label: "Complaint Date" },
];

export default function ComplaintForm() {
  const dispatch = useDispatch();
  const { formDraft, aiAssessment, status } = useSelector((s) => s.complaints);

  const handleChange = (field, value) => {
    dispatch(updateFormField({ field, value }));
  };

  const handleLogComplaint = () => {
    const payload = {
      ...formDraft,
      source_type: "manual",
      completeness_score: aiAssessment?.completeness_score ?? 0,
      missing_fields: aiAssessment?.missing_fields ?? [],
      risk_level: aiAssessment?.risk_level ?? "Unclassified",
      risk_justification: aiAssessment?.risk_justification ?? "",
      is_duplicate: (aiAssessment?.duplicates?.length ?? 0) > 0,
      duplicate_of_id: aiAssessment?.duplicates?.[0]?.id ?? null,
      duplicate_score: aiAssessment?.duplicates?.[0]?.similarity ?? null,
      root_cause: aiAssessment?.root_cause ?? [],
      capa_recommendation: aiAssessment?.capa_recommendation ?? "",
      ai_summary: aiAssessment?.ai_summary ?? "",
    };
    dispatch(saveComplaint(payload));
  };

  return (
    <div className="panel form-panel">
      <div className="panel-eyebrow">Step 2</div>
      <h2>Log Customer Complaint</h2>

      <div className="field-grid">
        {FIELDS.map(({ key, label }) => (
          <label className="field" key={key}>
            <span>{label}</span>
            <input
              type="text"
              value={formDraft[key] || ""}
              onChange={(e) => handleChange(key, e.target.value)}
              placeholder={aiAssessment ? "AI-populated - verify" : "Not yet analyzed"}
            />
          </label>
        ))}
      </div>

      <label className="field field-wide">
        <span>Complaint Description</span>
        <textarea
          rows={5}
          value={formDraft.complaint_text || ""}
          onChange={(e) => handleChange("complaint_text", e.target.value)}
        />
      </label>

      <div className="form-actions">
        <button className="btn btn-ghost" onClick={() => dispatch(resetForm())}>
          Clear
        </button>
        <button
          className="btn btn-primary"
          onClick={handleLogComplaint}
          disabled={status === "saving" || !formDraft.complaint_text}
        >
          {status === "saving" ? "Logging..." : "Log Complaint"}
        </button>
      </div>
    </div>
  );
}
