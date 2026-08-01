import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchComplaints } from "../store/complaintsSlice.js";

const RISK_CLASS = {
  Critical: "risk-critical",
  Major: "risk-major",
  Minor: "risk-minor",
  Unclassified: "risk-unclassified",
};

export default function ComplaintList() {
  const dispatch = useDispatch();
  const list = useSelector((s) => s.complaints.complaintsList);

  useEffect(() => {
    dispatch(fetchComplaints());
  }, [dispatch]);

  return (
    <div className="panel log-panel">
      <div className="panel-eyebrow">Log</div>
      <h2>Logged Complaints ({list.length})</h2>
      {list.length === 0 && <p className="panel-sub">No complaints logged yet.</p>}
      <div className="complaint-log-grid">
        {list.map((c) => (
          <div className={`log-card ${RISK_CLASS[c.risk_level] || "risk-unclassified"}`} key={c.id}>
            <div className="log-card-header">
              <strong>{c.product_name || "Unnamed product"}</strong>
              <span className={`risk-badge ${RISK_CLASS[c.risk_level] || "risk-unclassified"}`}>
                {c.risk_level}
              </span>
            </div>
            <div className="log-card-meta">
              {c.customer_name || "Unknown customer"} · Batch {c.batch_number || "N/A"}
            </div>
            <p className="log-card-summary">{c.ai_summary || c.complaint_text.slice(0, 140)}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
