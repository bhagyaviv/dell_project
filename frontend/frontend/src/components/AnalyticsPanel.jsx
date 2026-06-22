import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

function AnalyticsPanel({ liveData, trendHistory }) {
  
  // 🌟 Map the exact database column keys to our chart data lines
  const formatChartData = () => {
    if (!trendHistory || trendHistory.length === 0) {
      return [{ name: "Idle", Storage: 0, Thermal: 0, Compute: 0, Power: 0, Overall: 0 }];
    }
    
    return trendHistory.map(log => ({
      // Human-readable timestamp string for X-axis labels
      name: log.timestamp ? new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : "Live",
      Storage: log.storage_score ?? 0,
      Thermal: log.thermal_score ?? 0,
      Compute: log.compute_score ?? 0,
      Power: log.power_score ?? 0,
      Overall: log.overall_score ?? 100
    }));
  };

  const chartData = formatChartData();

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "24px", textAlign: "left" }}>
      
      {/* Overall Health Score Arc */}
      <div>
        <h4 style={{ margin: "0 0 12px 0", fontSize: "14px", color: "#3b82f6", textTransform: "uppercase", tracking: "wider" }}>
           Anomaly Timeline Stability Arc
        </h4>
        <div style={{ width: "100%", height: 180, backgroundColor: "#0f172a", borderRadius: "8px", padding: "10px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: "10px" }} />
              <YAxis stroke="#64748b" style={{ fontSize: "10px" }} domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }} />
              <Line type="monotone" dataKey="Overall" stroke="#3b82f6" strokeWidth={3} dot={{ r: 2 }} name="Overall Health" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* 4-Pillars Core Analytics Vector */}
      <div>
        <h4 style={{ margin: "0 0 12px 0", fontSize: "14px", color: "#a855f7", textTransform: "uppercase", tracking: "wider" }}>
           Sub-Component Risk Assessment Matrix
        </h4>
        <div style={{ width: "100%", height: 220, backgroundColor: "#0f172a", borderRadius: "8px", padding: "10px" }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="name" stroke="#64748b" style={{ fontSize: "10px" }} />
              <YAxis stroke="#64748b" style={{ fontSize: "10px" }} domain={[0, 100]} />
              <Tooltip contentStyle={{ backgroundColor: "#1e293b", borderColor: "#334155", color: "#f8fafc" }} />
              
              {/* Individual vectors tracks */}
              <Line type="monotone" dataKey="Storage" stroke="#c084fc" strokeWidth={2} dot={false} name="Storage Risk" />
              <Line type="monotone" dataKey="Thermal" stroke="#f97316" strokeWidth={2} dot={false} name="Thermal Risk" />
              <Line type="monotone" dataKey="Compute" stroke="#38bdf8" strokeWidth={2} dot={false} name="Compute Risk" />
              <Line type="monotone" dataKey="Power" stroke="#facc15" strokeWidth={2} dot={false} name="Power Risk" />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        {/* Color Legend codes row */}
        <div style={{ display: "flex", gap: "16px", marginTop: "12px", fontSize: "11px", justifyContent: "center", fontWeight: "600" }}>
          <span style={{ color: "#c084fc" }}>● Storage</span>
          <span style={{ color: "#f97316" }}>● Thermal</span>
          <span style={{ color: "#38bdf8" }}>● Compute</span>
          <span style={{ color: "#facc15" }}>● Power</span>
        </div>
      </div>

    </div>
  );
}

export default AnalyticsPanel;