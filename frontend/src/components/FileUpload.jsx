import React, { useRef, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { analyzeComplaintFile, analyzeComplaintText } from "../store/complaintsSlice.js";

export default function FileUpload() {
  const dispatch = useDispatch();
  const status = useSelector((s) => s.complaints.status);
  const fileInputRef = useRef(null);
  const [pastedText, setPastedText] = useState("");
  const [fileName, setFileName] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);
    dispatch(analyzeComplaintFile(file));
  };

  const handleAnalyzePasted = () => {
    if (!pastedText.trim()) return;
    dispatch(analyzeComplaintText(pastedText));
  };

  const isAnalyzing = status === "analyzing";

  return (
    <div className="panel intake-panel">
      <div className="panel-eyebrow">Intake</div>
      <h2>Bring in a complaint</h2>
      <p className="panel-sub">Upload a PDF or email export, or paste raw complaint text below.</p>

      <div className="upload-dropzone" onClick={() => fileInputRef.current?.click()}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.eml"
          hidden
          onChange={handleFileChange}
        />
        <span className="upload-icon">⇧</span>
        <span>{fileName ? fileName : "Click to choose a PDF, .eml, or .txt file"}</span>
      </div>

      <div className="divider-label">or paste text</div>

      <textarea
        className="text-input"
        rows={6}
        placeholder="Paste an email body or complaint description here..."
        value={pastedText}
        onChange={(e) => setPastedText(e.target.value)}
      />
      <button className="btn btn-primary" onClick={handleAnalyzePasted} disabled={isAnalyzing}>
        {isAnalyzing ? "Analyzing with AI..." : "Run AI Analysis"}
      </button>
    </div>
  );
}
