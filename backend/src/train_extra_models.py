import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

# Ensure path matching variables point to root directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

print("⏳ Generating synthetic training data matrices for Compute and Power...")

# =========================================================================
# 📊 1. GENERATE SYNTHETIC DATA & TRAIN COMPUTE MODEL
# =========================================================================
# Features: [cpu_utilization, memory_usage, thread_throttling_state]
np.random.seed(42)
n_samples = 2000

cpu_util = np.random.uniform(10.0, 98.0, n_samples)
mem_util = np.random.uniform(20.0, 95.0, n_samples)
throttling = np.where(cpu_util > 85, np.random.choice([0, 1], n_samples, p=[0.2, 0.8]), 0)

# Failure condition: high resource utilization compounding with thermal throttling loops
compute_fail = np.where((cpu_util > 80) & (mem_util > 80) & (throttling == 1), 1, 0)

df_compute = pd.DataFrame({
    'cpu_utilization': cpu_util,
    'memory_usage': mem_util,
    'throttling_state': throttling
})

X_comp = df_compute.values
y_comp = compute_fail

X_c_train, X_c_test, y_c_train, y_c_test = train_test_split(X_comp, y_comp, test_size=0.2, random_state=42)
compute_model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
compute_model.fit(X_c_train, y_c_train)

joblib.dump(compute_model, os.path.join(MODELS_DIR, 'compute_predictor.pkl'))
print("🟢 Successfully generated and dumped: models/compute_predictor.pkl")


# =========================================================================
# ⚡ 2. GENERATE SYNTHETIC DATA & TRAIN POWER MODEL
# =========================================================================
# Features: [voltage_12v, voltage_5v, current_amperage]
voltage_12v = np.random.uniform(11.2, 12.6, n_samples)
voltage_5v = np.random.uniform(4.5, 5.5, n_samples)
amperage = np.random.uniform(5.0, 25.0, n_samples)

# Failure condition: Voltage drop below standard operating threshold boundaries under heavy load
power_fail = np.where((voltage_12v < 11.5) & (amperage > 18.0), 1, np.where(voltage_5v < 4.7, 1, 0))

df_power = pd.DataFrame({
    'voltage_12v': voltage_12v,
    'voltage_5v': voltage_5v,
    'current_amperage': amperage
})

X_pow = df_power.values
y_pow = power_fail

X_p_train, X_p_test, y_p_train, y_p_test = train_test_split(X_pow, y_pow, test_size=0.2, random_state=42)
power_model = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, random_state=42)
power_model.fit(X_p_train, y_p_train)

joblib.dump(power_model, os.path.join(MODELS_DIR, 'power_predictor.pkl'))
print("🟢 Successfully generated and dumped: models/power_predictor.pkl")
print("🏁 Core ML compilation complete across all 4 pillars!")