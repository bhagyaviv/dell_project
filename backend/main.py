import os
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import mysql.connector
from src.predict import predict_hardware_failure

load_dotenv()

app = FastAPI(title="Intelligent Device Management Platform API - MySQL 4-Pillar Mode")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration matching your local MySQL setup
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD"),  # Fetches securely from RAM environment
    "database": os.getenv("DB_DATABASE", "dell_device_management")
}

def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 1. Ensure Master Fleet Table Exists
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_fleet_registry (
            node_id VARCHAR(128) PRIMARY KEY,
            node_name VARCHAR(255) NOT NULL,
            datacenter_rack VARCHAR(64) NOT NULL,
            date_provisioned TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 2. Create the Relational 4-Pillar Telemetry Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS health_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            node_id VARCHAR(128) NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            overall_score INT,
            status VARCHAR(50),
            storage_score INT,
            thermal_score INT,
            compute_score INT,
            power_score INT,
            reason TEXT,
            recommended_action TEXT,
            FOREIGN KEY (node_id) REFERENCES device_fleet_registry(node_id) ON DELETE CASCADE
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("🚀 MySQL database structure verified. Multi-node fleet logging operational!")
    except Exception as e:
        print(f"❌ Failed to initialize MySQL Database: {e}")

@app.on_event("startup")
def on_startup():
    init_db()

# =========================================================================
# 🎰 Live Prediction Endpoint (Updated for Multi-Node Tracking)
# =========================================================================
@app.get("/api/device-health/live")
def get_device_health(node_id: str = "node_001"):  # 🌟 Dynamic Node Parameter Added
    try:
        mock_prometheus_dict = {
            "storage_smart_5": float(random.choice([0, 0, 0, 0, 1, 0, 0])),
            "storage_smart_197": 0.0,
            "storage_smart_198": 0.0,
            "thermal_core_temp": random.uniform(40.0, 95.0), 
            "thermal_ambient_temp": 24.0,
            "cooling_fan_pwm": random.uniform(50.0, 100.0),
            "cooling_fan_rpm": random.uniform(1800.0, 4500.0),
            "cpu_utilization": random.uniform(10.0, 95.0),       
            "memory_utilization": random.uniform(20.0, 90.0),    
            "power_voltage_12v": random.uniform(11.4, 12.4),
            "power_voltage_5v": random.uniform(4.8, 5.2),        
            "power_amperage": random.uniform(5.0, 20.0)          
        }
        
        result = predict_hardware_failure(mock_prometheus_dict) 
        
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 🌟 Ensure the node profile exists in the registry to satisfy Foreign Key rules
        cursor.execute("""
            INSERT IGNORE INTO device_fleet_registry (node_id, node_name, datacenter_rack)
            VALUES (%s, %s, %s)
        """, (node_id, f"Dell PowerEdge {node_id.upper()}", f"Rack-{random.randint(1,15)}"))
        
        sql_query = """
            INSERT INTO health_logs (
                node_id, overall_score, status, storage_score, thermal_score, 
                compute_score, power_score, reason, recommended_action
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        record_values = (
            node_id,
            result['overall_health_score'],
            result['status'],
            result['component_breakdown']['storage']['risk_score'],
            result['component_breakdown']['thermal_cooling']['risk_score'],
            result['component_breakdown']['compute_performance']['risk_score'],
            result['component_breakdown']['power_delivery']['risk_score'],
            result['reason'],
            result['recommended_action']
        )
        
        cursor.execute(sql_query, record_values)
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"status": "success", "node_id": node_id, "data": result}
        
    except Exception as e:
        return {"status": "error", "message": f"Inference/Write Failure: {str(e)}"}

# =========================================================================
# 🌐 Historical Trends Endpoint (Filtered by Node ID)
# =========================================================================
@app.get("/api/device-health/history")
def get_historical_trends(node_id: str = "node_001"):  # 🌟 Filter Trends Dynamically
    """Returns the last 20 evaluation logs formatted for specific React chart tracking"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        # 🌟 Select logs only belonging to the target device
        cursor.execute("""
            SELECT timestamp, overall_score, storage_score, thermal_score, compute_score, power_score 
            FROM health_logs 
            WHERE node_id = %s
            ORDER BY id DESC LIMIT 20
        """, (node_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows[::-1]
    except Exception as e:
        return {"status": "error", "message": f"Database lookup failure: {str(e)}"}

# =========================================================================
# 📊 AGGREGATE OPERATIONS & ANALYTICS API ENDPOINTS
# =========================================================================
@app.get("/api/device-management/dashboard-summary")
def get_dashboard_summary():
    """Calculates fleet-wide overview analytics metrics for landing page counters"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT COUNT(*) as total_nodes FROM device_fleet_registry")
        total_nodes = cursor.fetchone()["total_nodes"]
        
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'critical' THEN 1 END) as critical_count,
                COUNT(CASE WHEN status = 'warning' THEN 1 END) as warning_count,
                AVG(overall_score) as fleet_avg_health
            FROM health_logs
            WHERE id IN (SELECT MAX(id) FROM health_logs GROUP BY node_id)
        """)
        stats = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "summary": {
                "total_monitored_devices": total_nodes if total_nodes > 0 else 3,
                "active_critical_failures": stats["critical_count"] or 0,
                "active_system_warnings": stats["warning_count"] or 0,
                "global_fleet_health_index": round(stats["fleet_avg_health"] or 100.0, 1)
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/device-management/pillar-averages")
def get_pillar_performance_metrics():
    """Calculates structural performance metrics for UI radar chart evaluations"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                AVG(storage_score) as avg_storage,
                AVG(thermal_score) as avg_thermal,
                AVG(compute_score) as avg_compute,
                AVG(power_score) as avg_power
            FROM health_logs
        """)
        averages = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return {
            "status": "success",
            "telemetry_metrics": {
                "storage_infrastructure": round(averages["avg_storage"] or 100.0, 1),
                "thermal_regulation": round(averages["avg_thermal"] or 100.0, 1),
                "compute_utilization": round(averages["avg_compute"] or 100.0, 1),
                "power_grid_efficiency": round(averages["avg_power"] or 100.0, 1)
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)