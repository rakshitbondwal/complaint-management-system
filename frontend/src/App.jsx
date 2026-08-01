import React from "react";
import FileUpload from "./components/FileUpload.jsx";
import ComplaintForm from "./components/ComplaintForm.jsx";
import AICopilotPanel from "./components/AICopilotPanel.jsx";
import ComplaintList from "./components/ComplaintList.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">◆</span>
          <span className="brand-name">Complaint Command</span>
        </div>
        <span className="brand-tag">AIVOA QMS — API / FDF Manufacturing</span>
      </header>

      <main className="workspace">
        <div className="workspace-col">
          <FileUpload />
          <ComplaintForm />
        </div>
        <div className="workspace-col">
          <AICopilotPanel />
        </div>
      </main>

      <section className="workspace-full">
        <ComplaintList />
      </section>
    </div>
  );
}
