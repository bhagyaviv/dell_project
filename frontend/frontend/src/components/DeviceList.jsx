function DeviceList({ liveData }) {
  // 1. Get your backend's overall health score and status if available
  const liveScore = liveData?.overall_health_score ?? 92; 
  const liveStatus = liveData?.status ? (liveData.status.charAt(0).toUpperCase() + liveData.status.slice(1)) : "Healthy";

  // 2. Map it directly onto Device A
  const devices = [
    {
      id: 1,
      name: "Device A",
      health: liveScore,            // <-- Dynamically changing with ML output!
      status: liveStatus,          // <-- Dynamically changing!
      temp: "42°C",
      voltage: "220V"
    },
    {
      id: 2,
      name: "Device B",
      health: 76,
      status: "Warning",
      temp: "48°C",
      voltage: "218V"
    },
    {
      id: 3,
      name: "Device C",
      health: 45,
      status: "Critical",
      temp: "55°C",
      voltage: "210V"
    }
  ];

  return (
    <div className="card">
      <h2>Devices</h2>
      {devices.map((device) => (
        <div key={device.id} className="device-item">
          <h3>{device.name}</h3>
          <p>Status: <span className={`status-${device.status.toLowerCase()}`}>{device.status}</span></p>
          <p>Temp: {device.temp} | Voltage: {device.voltage}</p>
          <p><strong>Health: {device.health}%</strong></p>
        </div>
      ))}
    </div>
  );
}

export default DeviceList;