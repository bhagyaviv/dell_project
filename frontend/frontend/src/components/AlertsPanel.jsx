function AlertsPanel({ liveData }) {
  // If there's no data or the component is idle
  if (!liveData) {
    return (
      <div style={{ padding: "16px", color: "#64748b", fontStyle: "italic", textAlign: "left" }}>
        Awaiting telemetry signature stream...
      </div>
    );
  }

  // Determine threat severity profile color codes
  const getSeverityStyle = (status) => {
    switch (status?.toLowerCase()) {
      case "critical":
        return { borderLeft: "4px solid #ef4444", bg: "#2d1a1a", text: "#fca5a5" };
      case "warning":
        return { borderLeft: "4px solid #f59e0b", bg: "#2d251a", text: "#fde047" };
      default:
        return { borderLeft: "4px solid #10b981", bg: "#1a2d20", text: "#a7f3d0" };
    }
  };

  const style = getSeverityStyle(liveData.status);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "12px", textAlign: "left" }}>
      
      {/* Dynamic Machine Learning Insight Card */}
      <div style={{ backgroundColor: style.bg, padding: "16px", borderRadius: "8px", borderLeft: style.borderLeft }}>
        <h4 style={{ margin: "0 0 4px 0", color: style.text, textTransform: "uppercase", fontSize: "12px", fontWeight: "700" }}>
          System Status: {liveData.status || "UNKNOWN"}
        </h4>
        <p style={{ margin: "8px 0 0 0", fontSize: "14px", color: "#e2e8f0", lineHeight: "1.4" }}>
          <strong>Diagnostic Logic:</strong> {liveData.reason || "Metrics running within normal parameters."}
        </p>
      </div>

      {/* Action Recommendation Box */}
      {liveData.recommended_action && (
        <div style={{ backgroundColor: "#0f172a", padding: "14px", borderRadius: "8px", border: "1px dashed #334155" }}>
          <h5 style={{ margin: "0 0 4px 0", color: "#3b82f6", fontSize: "12px", textTransform: "uppercase" }}>
            🔧 Prescriptive Action Plan
          </h5>
          <p style={{ margin: 0, fontSize: "13px", color: "#94a3b8" }}>
            {liveData.recommended_action}
          </p>
        </div>
      )}

      {/* Probability Index Summary Footer */}
      <div style={{ backgroundColor: "#1e293b", padding: "12px", borderRadius: "8px", border: "1px solid #334155", fontSize: "13px" }}>
        <strong>Model Output Summary:</strong> Node overall risk factor evaluated at {100 - (liveData.overall_health_score || 100)}%.
      </div>

    </div>
  );
}

export default AlertsPanel;