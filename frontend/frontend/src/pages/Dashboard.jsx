import { useState, useEffect } from "react";
import Navbar from "../components/Navbar";
import DeviceList from "../components/DeviceList";
import AnalyticsPanel from "../components/AnalyticsPanel";
import AlertsPanel from "../components/AlertsPanel";

function Dashboard() {
  // 🧭 Multi-Page Internal View Router State
  const [activeTab, setActiveTab] = useState("nodes"); // Options: "nodes" | "telemetry" | "alerts"
  
  const [selectedNode, setSelectedNode] = useState("node_001");
  const [liveData, setLiveData] = useState(null);
  const [trendHistory, setTrendHistory] = useState([]);
  const [isSimulating, setIsSimulating] = useState(false);
  const [summary, setSummary] = useState({
    total_monitored_devices: 3,
    active_critical_failures: 0,
    active_system_warnings: 1,
    global_fleet_health_index: 94
  });

  const triggerLiveSimulation = async (nodeId) => {
    setIsSimulating(true);
    try {
      const response = await fetch(`http://localhost:8000/api/device-health/live?node_id=${nodeId}`);
      const json = await response.json();
      if (json.status === "success") {
        setLiveData(json.data);
      }
    } catch (error) {
      console.error("Simulation engine offline:", error);
    } finally {
      setIsSimulating(false);
    }
  };

  useEffect(() => {
    const fetchNodeData = async () => {
      try {
        const historyResponse = await fetch(`http://localhost:8000/api/device-health/history?node_id=${selectedNode}`);
        const historyJson = await historyResponse.json();
        setTrendHistory(Array.isArray(historyJson) ? historyJson : []);

        const summaryResponse = await fetch('http://localhost:8000/api/device-management/dashboard-summary');
        const summaryJson = await summaryResponse.json();
        if (summaryJson.status === "success") {
          setSummary(summaryJson.summary);
        }
      } catch (error) {
        console.error("Error fetching telemetry matrix streams:", error);
      }
    };

    fetchNodeData();
    const interval = setInterval(() => triggerLiveSimulation(selectedNode), 3000);
    return () => clearInterval(interval);
  }, [selectedNode]);

  return (
    <div style={{ backgroundColor: "#0f172a", minHeight: "100vh", color: "#f8fafc", fontFamily: "sans-serif" }}>
      <Navbar />
      
      {/* 🧭 PREMIUM MULTI-PAGE ENTERPRISE NAVIGATION BAR */}
      <div style={{ backgroundColor: "#1e293b", borderBottom: "1px solid #334155", display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0 24px" }}>
        <div style={{ display: "flex", gap: "8px" }}>
          <button 
            onClick={() => setActiveTab("nodes")}
            style={{ padding: "16px 20px", background: "none", border: "none", borderBottom: activeTab === "nodes" ? "3px solid #3b82f6" : "3px solid transparent", color: activeTab === "nodes" ? "#3b82f6" : "#94a3b8", fontWeight: "700", cursor: "pointer", fontSize: "14px", textTransform: "uppercase" }}
          >
            🖥️ Managed Cluster Nodes
          </button>
          <button 
            onClick={() => setActiveTab("telemetry")}
            style={{ padding: "16px 20px", background: "none", border: "none", borderBottom: activeTab === "telemetry" ? "3px solid #3b82f6" : "3px solid transparent", color: activeTab === "telemetry" ? "#3b82f6" : "#94a3b8", fontWeight: "700", cursor: "pointer", fontSize: "14px", textTransform: "uppercase" }}
          >
            📊 Multi-Pillar Telemetry Engine
          </button>
          <button 
            onClick={() => setActiveTab("alerts")}
            style={{ padding: "16px 20px", background: "none", border: "none", borderBottom: activeTab === "alerts" ? "3px solid #3b82f6" : "3px solid transparent", color: activeTab === "alerts" ? "#3b82f6" : "#94a3b8", fontWeight: "700", cursor: "pointer", fontSize: "14px", textTransform: "uppercase" }}
          >
            🚨 Categorized Alert Center
          </button>
        </div>

        {/* Dynamic Selector Context Control */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "8px 0" }}>
          <select 
            value={selectedNode} 
            onChange={(e) => setSelectedNode(e.target.value)}
            style={{ backgroundColor: "#0f172a", border: "1px solid #475569", color: "#f1f5f9", padding: "6px 12px", borderRadius: "6px", fontWeight: "500", cursor: "pointer", outline: "none" }}
          >
            <option value="node_001">Dell PowerEdge R760 (Device A)</option>
            <option value="node_002">Dell PowerEdge R660 (Device B)</option>
            <option value="node_003">Dell PowerEdge XE9680 (Device C)</option>
          </select>
          <button 
            onClick={() => triggerLiveSimulation(selectedNode)}
            disabled={isSimulating}
            style={{ backgroundColor: "#2563eb", color: "white", fontWeight: "600", padding: "6px 14px", borderRadius: "6px", border: "none", cursor: "pointer", opacity: isSimulating ? 0.5 : 1, fontSize: "13px" }}
          >
            {isSimulating ? "Simulating..." : "⚡ Sync Refetch"}
          </button>
        </div>
      </div>

      {/* 📊 REAL-TIME CORE FLEET STATS ROW */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "16px", padding: "20px 24px 0 24px" }}>
        <div style={{ backgroundColor: "#1e293b", padding: "14px 18px", borderRadius: "10px", border: "1px solid #334155" }}>
          <p style={{ margin: 0, fontSize: "11px", color: "#94a3b8", fontWeight: "600", textTransform: "uppercase" }}>Cluster Size</p>
          <p style={{ margin: "2px 0 0 0", fontSize: "22px", fontWeight: "700" }}>{summary.total_monitored_devices} Active Nodes</p>
        </div>
        <div style={{ backgroundColor: "#1e293b", padding: "14px 18px", borderRadius: "10px", border: "1px solid #334155" }}>
          <p style={{ margin: 0, fontSize: "11px", color: "#94a3b8", fontWeight: "600", textTransform: "uppercase" }}>Fleet Health Index</p>
          <p style={{ margin: "2px 0 0 0", fontSize: "22px", fontWeight: "700", color: "#4ade80" }}>{summary.global_fleet_health_index}% Stable</p>
        </div>
        <div style={{ backgroundColor: "#1e293b", padding: "14px 18px", borderRadius: "10px", border: "1px solid #334155" }}>
          <p style={{ margin: 0, fontSize: "11px", color: "#94a3b8", fontWeight: "600", textTransform: "uppercase" }}>Medium Risk Indicators</p>
          <p style={{ margin: "2px 0 0 0", fontSize: "22px", fontWeight: "700", color: "#f59e0b" }}>{summary.active_system_warnings} Flagged</p>
        </div>
        <div style={{ backgroundColor: "#1e293b", padding: "14px 18px", borderRadius: "10px", border: "1px solid #334155" }}>
          <p style={{ margin: 0, fontSize: "11px", color: "#94a3b8", fontWeight: "600", textTransform: "uppercase" }}>Critical Outages</p>
          <p style={{ margin: "2px 0 0 0", fontSize: "22px", fontWeight: "700", color: "#ef4444" }}>{summary.active_critical_failures} Overloads</p>
        </div>
      </div>

      {/* 🏛️ MULTI-PAGE VIEW RENDERING LOGIC */}
      <div style={{ padding: "24px", minHeight: "65vh" }}>
        
        {/* PAGE 1: CLUSTER NODES OVERVIEW VIEW */}
        {activeTab === "nodes" && (
          <div style={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "12px", padding: "24px" }}>
            <h2 style={{ margin: "0 0 4px 0", fontSize: "18px", fontWeight: "700", color: "#3b82f6" }}>🖥️ Virtual Computer Systems Registry</h2>
            <p style={{ margin: "0 0 20px 0", fontSize: "13px", color: "#94a3b8" }}>Overview status profiles for simulated hardware node configurations.</p>
            <DeviceList liveData={liveData} selectedNode={selectedNode} setSelectedNode={setSelectedNode} />
          </div>
        )}

        {/* PAGE 2: DEEP-DIVE TELEMETRY PILLARS VIEW */}
        {activeTab === "telemetry" && (
          <div style={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "12px", padding: "24px" }}>
            <h2 style={{ margin: "0 0 4px 0", fontSize: "18px", fontWeight: "700", color: "#a855f7" }}>📊 Component Performance Engine</h2>
            <p style={{ margin: "0 0 20px 0", fontSize: "13px", color: "#94a3b8" }}>Real-time telemetry streams evaluating Thermal Management, Fan Speeds, Storage Risk, and Power Supplies.</p>
            <AnalyticsPanel liveData={liveData} trendHistory={trendHistory} />
          </div>
        )}

        {/* PAGE 3: CATEGORIZED CRITICAL/NORMAL ALERT SYSTEM */}
        {activeTab === "alerts" && (
          <div style={{ backgroundColor: "#1e293b", border: "1px solid #334155", borderRadius: "12px", padding: "24px" }}>
            <div style={{ borderBottom: "1px solid #334155", paddingBottom: "12px", marginBottom: "20px" }}>
              <h2 style={{ margin: "0 0 4px 0", fontSize: "18px", fontWeight: "700", color: "#ef4444" }}>🚨 Threat Assessment Log Center</h2>
              <p style={{ margin: "0", fontSize: "13px", color: "#94a3b8" }}>XGBoost predictive diagnostics sorted by severity categories.</p>
            </div>
            
            {/* Split Threat Matrix Layout Cards */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "20px" }}>
              
              {/* 🔴 CRITICAL SECTOR */}
              <div style={{ backgroundColor: "#0f172a", borderRadius: "8px", padding: "16px", borderTop: "4px solid #ef4444" }}>
                <h4 style={{ margin: "0 0 12px 0", color: "#ef4444", fontSize: "13px", textTransform: "uppercase", fontWeight: "700" }}>🔴 Critical Faults</h4>
                {trendHistory.filter(log => log.status === "critical").length > 0 ? (
                  trendHistory.filter(log => log.status === "critical").slice(0, 3).map((item, idx) => (
                    <div key={idx} style={{ backgroundColor: "#1e293b", padding: "10px", borderRadius: "6px", marginBottom: "8px", border: "1px solid #334155" }}>
                      <p style={{ margin: "0 0 4px 0", fontSize: "13px", color: "#fca5a5" }}><strong>Incident:</strong> {item.reason}</p>
                      <p style={{ margin: 0, fontSize: "11px", color: "#94a3b8" }}><strong>Action:</strong> {item.recommended_action}</p>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: "12px", color: "#64748b", fontStyle: "italic" }}>No active severe anomalies detected.</p>
                )}
              </div>

              {/* 🟡 MEDIUM RISK SECTOR */}
              <div style={{ backgroundColor: "#0f172a", borderRadius: "8px", padding: "16px", borderTop: "4px solid #f59e0b" }}>
                <h4 style={{ margin: "0 0 12px 0", color: "#f59e0b", fontSize: "13px", textTransform: "uppercase", fontWeight: "700" }}>🟡 Medium Risks</h4>
                {trendHistory.filter(log => log.status === "warning").length > 0 ? (
                  trendHistory.filter(log => log.status === "warning").slice(0, 3).map((item, idx) => (
                    <div key={idx} style={{ backgroundColor: "#1e293b", padding: "10px", borderRadius: "6px", marginBottom: "8px", border: "1px solid #334155" }}>
                      <p style={{ margin: "0 0 4px 0", fontSize: "13px", color: "#fde047" }}><strong>Warning:</strong> {item.reason}</p>
                      <p style={{ margin: 0, fontSize: "11px", color: "#94a3b8" }}><strong>Action:</strong> {item.recommended_action}</p>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: "12px", color: "#64748b", fontStyle: "italic" }}>No moderate risks flagged.</p>
                )}
              </div>

              {/* 🟢 NORMAL STABLE SECTOR */}
              <div style={{ backgroundColor: "#0f172a", borderRadius: "8px", padding: "16px", borderTop: "4px solid #10b981" }}>
                <h4 style={{ margin: "0 0 12px 0", color: "#10b981", fontSize: "13px", textTransform: "uppercase", fontWeight: "700" }}>🟢 Normal Operations</h4>
                {trendHistory.filter(log => log.status === "healthy" || !log.status).length > 0 ? (
                  trendHistory.filter(log => log.status === "healthy" || !log.status).slice(0, 3).map((item, idx) => (
                    <div key={idx} style={{ backgroundColor: "#1e293b", padding: "10px", borderRadius: "6px", marginBottom: "8px", border: "1px solid #334155" }}>
                      <p style={{ margin: "0 0 4px 0", fontSize: "12px", color: "#a7f3d0" }}>✓ System operating within normal parameters.</p>
                      <p style={{ margin: 0, fontSize: "11px", color: "#64748b" }}>Score: {item.overall_score}% efficiency profile.</p>
                    </div>
                  ))
                ) : (
                  <p style={{ fontSize: "12px", color: "#64748b", fontStyle: "italic" }}>No healthy status telemetry logged.</p>
                )}
              </div>

            </div>
          </div>
        )}

      </div>

      {/* Footer Element */}
      <div style={{ padding: "20px", textAlign: "center", fontSize: "12px", color: "#64748b", borderTop: "1px solid #1e293b" }}>
        DELL Intelligent Fleet Diagnostics Console © 2026
      </div>
    </div>
  );
}

export default Dashboard;