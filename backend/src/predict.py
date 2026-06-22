import os
import json
import joblib
import numpy as np

# Resolve paths dynamically relative to this script's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

# Paths for all 4 production ML model assets
MODEL_PATHS = {
    'storage': os.path.join(MODELS_DIR, 'storage_predictor.pkl'),
    'thermal': os.path.join(MODELS_DIR, 'thermal_predictor.pkl'),
    'compute': os.path.join(MODELS_DIR, 'compute_predictor.pkl'),
    'power': os.path.join(MODELS_DIR, 'power_predictor.pkl')
}

# Paths for all 4 optimized F1 threshold config tracks
THRESHOLD_PATHS = {
    'storage': os.path.join(MODELS_DIR, 'storage_predictor_threshold.json'),
    'thermal': os.path.join(MODELS_DIR, 'thermal_predictor_threshold.json'),
    'compute': os.path.join(MODELS_DIR, 'compute_predictor_threshold.json'),
    'power': os.path.join(MODELS_DIR, 'power_predictor_threshold.json')
}


def _load_threshold(path, default_value=0.5):
    if not os.path.exists(path):
        return default_value
    try:
        with open(path, 'r', encoding='utf-8') as threshold_file:
            payload = json.load(threshold_file)
        return float(payload.get('failure_threshold', default_value))
    except Exception:
        return default_value


# 🟢 Verify and load all 4 production ML brains safely into memory at runtime
MODELS = {}
THRESHOLDS = {}

for pillar, path in MODEL_PATHS.items():
    if os.path.exists(path):
        MODELS[pillar] = joblib.load(path)
        THRESHOLDS[pillar] = _load_threshold(THRESHOLD_PATHS[pillar], 0.5)
    else:
        raise FileNotFoundError(
            f"Trained model file for '{pillar}' (.pkl) not found in /models directory. "
            "Please run 'src/train.py' first!"
        )


def predict_hardware_failure(live_prometheus_dict):
    """
    Accepts a real-time dictionary payload of metrics from the backend data flow.
    Processes features, runs true ML inference across all 4 pillars, and returns structured insights.
    """
    
    # =========================================================================
    # 1. STORAGE INFERENCE (Pillar 1)
    # =========================================================================
    storage_features = np.array([[
        float(live_prometheus_dict.get('storage_smart_5', 0.0)),
        float(live_prometheus_dict.get('storage_smart_197', 0.0)),
        float(live_prometheus_dict.get('storage_smart_198', 0.0))
    ]])
    
    storage_prob = float(MODELS['storage'].predict_proba(storage_features)[0][1])
    storage_score = int(storage_prob * 100)
    storage_failure_likely = storage_prob >= THRESHOLDS['storage']

    # =========================================================================
    # 2. THERMAL & COOLING INFERENCE (Pillar 2)
    # =========================================================================
    core_temp = float(live_prometheus_dict.get('thermal_core_temp', 35.0))
    ambient_temp = float(live_prometheus_dict.get('thermal_ambient_temp', 23.0))
    fan_pwm = float(live_prometheus_dict.get('cooling_fan_pwm', 60.0))
    fan_rpm = float(live_prometheus_dict.get('cooling_fan_rpm', 2000.0))
    voltage_12v = float(live_prometheus_dict.get('power_voltage_12v', 12.0))

    delta_t = core_temp - ambient_temp
    thermal_efficiency = core_temp / (fan_rpm + 1.0)
    voltage_deviation = abs(voltage_12v - 12.0)
    fan_slippage = fan_pwm - (fan_rpm / 50.0)

    thermal_features = np.array([[delta_t, thermal_efficiency, voltage_deviation, fan_slippage]])
    
    thermal_prob = float(MODELS['thermal'].predict_proba(thermal_features)[0][1])
    thermal_score = int(thermal_prob * 100)
    thermal_failure_likely = thermal_prob >= THRESHOLDS['thermal']

    # =========================================================================
    # 3. COMPUTE PERFORMANCE INFERENCE (Pillar 3 - Fully Upgraded to ML)
    # =========================================================================
    cpu_util = float(live_prometheus_dict.get('cpu_utilization', 40.0))
    mem_util = float(live_prometheus_dict.get('memory_utilization', 50.0))
    throttling = 1.0 if cpu_util > 80.0 else 0.0

    compute_features = np.array([[cpu_util, mem_util, throttling]])
    
    compute_prob = float(MODELS['compute'].predict_proba(compute_features)[0][1])
    compute_score = int(compute_prob * 100)
    compute_failure_likely = compute_prob >= THRESHOLDS['compute']

    # =========================================================================
    # 4. POWER DELIVERY INFERENCE (Pillar 4 - Fully Upgraded to ML)
    # =========================================================================
    voltage_5v = float(live_prometheus_dict.get('power_voltage_5v', 5.0))
    amperage = float(live_prometheus_dict.get('power_amperage', 10.0))

    power_features = np.array([[voltage_12v, voltage_5v, amperage]])
    
    power_prob = float(MODELS['power'].predict_proba(power_features)[0][1])
    power_score = int(power_prob * 100)
    power_failure_likely = power_prob >= THRESHOLDS['power']

    # =========================================================================
    # 5. METRIC AGGREGATION & PRESCRIPTIVE LOGIC
    # =========================================================================
    overall_health_score = max(storage_score, thermal_score, compute_score, power_score)
    
    status = "healthy"
    reason = "All monitored hardware sub-systems operating within normal bounds."
    action = "No proactive maintenance scheduled."
    
    # Check ML failure flags directly to assign prescriptive feedback loops
    if storage_failure_likely or thermal_failure_likely or compute_failure_likely or power_failure_likely:
        status = "critical"
        if storage_score == max(storage_score, thermal_score, compute_score, power_score):
            reason = "Critical SMART sectors showing hardware surface degradation."
            action = "Backup all target system volumes immediately and replace the underlying physical disk drive."
        elif thermal_score == max(storage_score, thermal_score, compute_score, power_score):
            if delta_t > 42.0:
                reason = f"Severe thermal anomaly detected. Core-to-ambient temperature gradient split is high ({delta_t:.1f}°C)."
                action = "Inspect physical chassis airflow blockages and apply fresh thermal compound interface layers."
            else:
                reason = f"Cooling subsystem failure vector. Fan slipping under high duty cycle load ({int(fan_rpm)} RPM)."
                action = "Replace failed mechanical fan ball-bearing assembly units immediately."
        elif compute_score == max(storage_score, thermal_score, compute_score, power_score):
            reason = f"Compute cluster resource exhaustion. Predictive engine marks resource footprint as volatile."
            action = "Optimize container cluster threading allocations or scale hardware nodes horizontally."
        else:
            reason = f"Power distribution rail instability. Electrical anomalies verified outside safety limits."
            action = "Replace machine Power Supply Unit (PSU) immediately to protect logic boards."
                
    elif overall_health_score > 40:
        status = "warning"
        reason = "Early warning signatures detected. Components exhibiting gradual operating efficiency decline."
        action = "Flag hardware asset node for evaluation during the next routine system maintenance window."

    return {
        "overall_health_score": overall_health_score,
        "status": status,
        "component_breakdown": {
            "storage": {
                "risk_score": storage_score,
                "status": "critical" if storage_failure_likely else ("warning" if storage_score > 40 else "healthy"),
                "failure_likely": storage_failure_likely,
                "failure_threshold": int(THRESHOLDS['storage'] * 100)
            },
            "thermal_cooling": {
                "risk_score": thermal_score,
                "status": "critical" if thermal_failure_likely else ("warning" if thermal_score > 40 else "healthy"),
                "failure_likely": thermal_failure_likely,
                "failure_threshold": int(THRESHOLDS['thermal'] * 100)
            },
            "compute_performance": {
                "risk_score": compute_score,
                "status": "critical" if compute_failure_likely else ("warning" if compute_score > 40 else "healthy"),
                "failure_likely": compute_failure_likely,
                "failure_threshold": int(THRESHOLDS['compute'] * 100)
            },
            "power_delivery": {
                "risk_score": power_score,
                "status": "critical" if power_failure_likely else ("warning" if power_score > 40 else "healthy"),
                "failure_likely": power_failure_likely,
                "failure_threshold": int(THRESHOLDS['power'] * 100)
            }
        },
        "reason": reason,
        "recommended_action": action
    }