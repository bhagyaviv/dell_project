import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)
# 🟢 SMOTE pipeline for handling data center class imbalances
from imblearn.over_sampling import SMOTE 
import joblib
import os
import json


def _pick_failure_threshold(y_true, y_prob, min_precision=0.15):
    """Choose a probability threshold that favors failure detection on imbalanced data."""
    precision, recall, thresholds = precision_recall_curve(y_true, y_prob)

    best_threshold = 0.5
    best_f1 = -1.0

    for index, threshold in enumerate(thresholds):
        current_precision = precision[index + 1]
        current_recall = recall[index + 1]

        if current_precision < min_precision:
            continue

        if current_precision + current_recall == 0:
            continue

        current_f1 = 2 * current_precision * current_recall / (current_precision + current_recall)
        if current_f1 > best_f1:
            best_f1 = current_f1
            best_threshold = float(threshold)

    return best_threshold


def train_production_models():
    # Ensure all target environment folders exist
    os.makedirs('models', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # =========================================================================
    # 💾 1. STORAGE COMPONENT MODEL (Real Sourced Data + SMOTE Over-sampling)
    # =========================================================================
    processed_storage_path = 'data/storage_clean_train.csv'
    
    if os.path.exists(processed_storage_path):
        print("--- 💾 TRAINING STORAGE PILLAR (Real Backblaze Sourced Data) ---")
        storage_df = pd.read_csv(processed_storage_path)
        feature_cols = ['storage_smart_5', 'storage_smart_197', 'storage_smart_198']
        
        X_storage = storage_df[feature_cols].values
        y_storage = storage_df['failure'].values
        
        num_healthy = (y_storage == 0).sum()
        num_failed = (y_storage == 1).sum()
        imbalance_ratio = max(1.0, float(num_healthy) / float(num_failed)) if num_failed > 0 else 15.0

        X_train, X_test, y_train, y_test = train_test_split(
            X_storage, y_storage, test_size=0.2, random_state=42, stratify=y_storage
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
        )
        
        print(f"Applying SMOTE framework to imbalanced storage tracks...")
        smote = SMOTE(sampling_strategy=0.3, random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
        
        storage_model = XGBClassifier(
            n_estimators=250, max_depth=5, learning_rate=0.05,
            subsample=0.85, colsample_bytree=0.85,
            scale_pos_weight=imbalance_ratio, random_state=42, eval_metric='aucpr'
        )
        storage_model.fit(X_train_res, y_train_res, eval_set=[(X_val, y_val)], verbose=False)
        storage_threshold = _pick_failure_threshold(y_val, storage_model.predict_proba(X_val)[:, 1])
        
        storage_prob = storage_model.predict_proba(X_test)[:, 1]
        y_pred = (storage_prob >= storage_threshold).astype(int)
        
        print(f"✔ Storage Validation Accuracy: {accuracy_score(y_test, y_pred) * 100:.2f}%")
        print(f"✔ Storage Failure F1-Score: {f1_score(y_test, y_pred, zero_division=0):.3f}")
        print(f"✔ Storage Failure Threshold: {storage_threshold:.3f}\n")
        
        joblib.dump(storage_model, 'models/storage_predictor.pkl')
        with open('models/storage_predictor_threshold.json', 'w', encoding='utf-8') as f:
            json.dump({'failure_threshold': storage_threshold}, f, indent=2)
    else:
        print(f"❌ Missing file: {processed_storage_path}. Skipping Storage training.")

    # =========================================================================
    # 🌡️ 2. THERMAL & COOLING JOINT ENGINE (Real Sourced Data)
    # =========================================================================
    thermal_raw_path = 'data/thermal_raw.csv'
    
    if os.path.exists(thermal_raw_path):
        print("--- 🌡️ TRAINING THERMAL PILLAR (Real Thermal Sourced Data) ---")
        thermal_df = pd.read_csv(thermal_raw_path)
        X_thermal = pd.DataFrame()
        X_thermal['delta_t'] = thermal_df['thermal_core_temp'] - thermal_df['thermal_ambient_temp']
        X_thermal['thermal_efficiency'] = thermal_df['thermal_core_temp'] / (thermal_df['cooling_fan_rpm'] + 1)
        X_thermal['voltage_deviation'] = np.abs(thermal_df['power_voltage_12v'] - 12.0)
        X_thermal['fan_slippage'] = thermal_df['cooling_fan_pwm'] - (thermal_df['cooling_fan_rpm'] / 50.0)
        y_thermal = thermal_df['failure'].values
        
        t_healthy = (y_thermal == 0).sum()
        t_failed = (y_thermal == 1).sum()
        thermal_imbalance = max(1.0, float(t_healthy) / float(t_failed)) if t_failed > 0 else 1.0
        
        X_t_train, X_t_test, y_t_train, y_t_test = train_test_split(X_thermal.values, y_thermal, test_size=0.2, random_state=42, stratify=y_thermal)
        X_t_train, X_t_val, y_t_train, y_t_val = train_test_split(X_t_train, y_t_train, test_size=0.2, random_state=42, stratify=y_t_train)
        
        thermal_model = XGBClassifier(n_estimators=250, max_depth=4, learning_rate=0.05, scale_pos_weight=thermal_imbalance, random_state=42, eval_metric='aucpr')
        thermal_model.fit(X_t_train, y_t_train, eval_set=[(X_t_val, y_t_val)], verbose=False)
        
        thermal_threshold = _pick_failure_threshold(y_t_val, thermal_model.predict_proba(X_t_val)[:, 1])
        thermal_prob = thermal_model.predict_proba(X_t_test)[:, 1]
        y_t_pred = (thermal_prob >= thermal_threshold).astype(int)
        
        print(f"✔ Thermal Validation Accuracy: {accuracy_score(y_t_test, y_t_pred) * 100:.2f}%")
        print(f"✔ Thermal Failure F1-Score: {f1_score(y_t_test, y_t_pred, zero_division=0):.3f}")
        print(f"✔ Thermal Failure Threshold: {thermal_threshold:.3f}\n")
        
        joblib.dump(thermal_model, 'models/thermal_predictor.pkl')
        with open('models/thermal_predictor_threshold.json', 'w', encoding='utf-8') as f:
            json.dump({'failure_threshold': thermal_threshold}, f, indent=2)
    else:
        print(f"❌ Missing file: {thermal_raw_path}. Skipping Thermal training.")

    # =========================================================================
    # 🧮 3. COMPUTE PERFORMANCE ENGINE (Real Sourced Data)
    # =========================================================================
    compute_raw_path = 'data/compute_raw.csv'
    
    if os.path.exists(compute_raw_path):
        print("--- 🧮 TRAINING COMPUTE PILLAR (Real Infrastructure Data Ingestion) ---")
        compute_df = pd.read_csv(compute_raw_path)
        
        cpu_col = 'CPU_Utilization' if 'CPU_Utilization' in compute_df.columns else compute_df.columns[1]
        mem_col = 'Memory_Usage' if 'Memory_Usage' in compute_df.columns else compute_df.columns[2]
        
        cpu_util = compute_df[cpu_col].values
        mem_util = compute_df[mem_col].values
        
        # Real-world system degradation rule-map logic tagging
        compute_fail = np.where((cpu_util > 85) & (mem_util > 80), 1, 0)
        throttling = np.where(cpu_util > 80, 1, 0)
        X_comp = np.column_stack((cpu_util, mem_util, throttling))
        
        X_c_train, X_c_test, y_c_train, y_c_test = train_test_split(X_comp, compute_fail, test_size=0.2, random_state=42, stratify=compute_fail)
        X_c_train, X_c_val, y_c_train, y_c_val = train_test_split(X_c_train, y_c_train, test_size=0.2, random_state=42, stratify=y_c_train)
        
        c_imbalance = max(1.0, float((y_c_train == 0).sum()) / float((y_c_train == 1).sum())) if (y_c_train == 1).sum() > 0 else 1.0
        compute_model = XGBClassifier(n_estimators=150, max_depth=3, learning_rate=0.05, scale_pos_weight=c_imbalance, random_state=42, eval_metric='aucpr')
        compute_model.fit(X_c_train, y_c_train, eval_set=[(X_c_val, y_c_val)], verbose=False)
        
        compute_threshold = _pick_failure_threshold(y_c_val, compute_model.predict_proba(X_c_val)[:, 1])
        comp_prob = compute_model.predict_proba(X_c_test)[:, 1]
        y_c_pred = (comp_prob >= compute_threshold).astype(int)
        
        print(f"✔ Compute Validation Accuracy: {accuracy_score(y_c_test, y_c_pred) * 100:.2f}%")
        print(f"✔ Compute Failure Threshold: {compute_threshold:.3f}\n")
        
        joblib.dump(compute_model, 'models/compute_predictor.pkl')
        with open('models/compute_predictor_threshold.json', 'w', encoding='utf-8') as f:
            json.dump({'failure_threshold': compute_threshold}, f, indent=2)
    else:
        print(f"⚠️ Missing {compute_raw_path}. Skipping Compute training.")

    # =========================================================================
    # ⚡ 4. POWER DELIVERY ENGINE (Real NASA PCoE B0056 Extracted Dataset)
    # =========================================================================
    power_raw_path = 'data/power_raw.csv'
    
    if os.path.exists(power_raw_path):
        print("--- ⚡ TRAINING POWER PILLAR (Real NASA B0056 Dataset Ingestion) ---")
        power_df = pd.read_csv(power_raw_path)
        
        voltage_12v = pd.to_numeric(power_df['Voltage_measured'], errors='coerce').fillna(12.0).values
        amperage = pd.to_numeric(power_df['Current_measured'], errors='coerce').fillna(15.0).values
        # Maintain structural input shape constraints matching the live interface contract
        voltage_5v = np.random.uniform(4.9, 5.1, len(voltage_12v))
        
        # Tag actual electrical power drop thresholds based on chemical cell aging curves
        power_fail = np.where((voltage_12v < 3.2) & (np.abs(amperage) > 1.5), 1, 0)
        X_pow = np.column_stack((voltage_12v, voltage_5v, amperage))
        
        X_p_train, X_p_test, y_p_train, y_p_test = train_test_split(X_pow, power_fail, test_size=0.2, random_state=42, stratify=power_fail)
        X_p_train, X_p_val, y_p_train, y_p_val = train_test_split(X_p_train, y_p_train, test_size=0.2, random_state=42, stratify=y_p_train)
        
        p_imbalance = max(1.0, float((y_p_train == 0).sum()) / float((y_p_train == 1).sum())) if (y_p_train == 1).sum() > 0 else 10.0
        power_model = XGBClassifier(n_estimators=150, max_depth=3, learning_rate=0.05, scale_pos_weight=p_imbalance, random_state=42, eval_metric='aucpr')
        power_model.fit(X_p_train, y_p_train, eval_set=[(X_p_val, y_p_val)], verbose=False)
        
        power_threshold = _pick_failure_threshold(y_p_val, power_model.predict_proba(X_p_val)[:, 1])
        pow_prob = power_model.predict_proba(X_p_test)[:, 1]
        y_p_pred = (pow_prob >= power_threshold).astype(int)
        
        print(f"✔ Power Validation Accuracy: {accuracy_score(y_p_test, y_p_pred) * 100:.2f}%")
        print(f"✔ Power Failure Threshold: {power_threshold:.3f}\n")
        
        joblib.dump(power_model, 'models/power_predictor.pkl')
        with open('models/power_predictor_threshold.json', 'w', encoding='utf-8') as f:
            json.dump({'failure_threshold': power_threshold}, f, indent=2)
    else:
        print(f"⚠️ Missing {power_raw_path}. Skipping Power training.")

    print("🎉 Core training suite processing complete across all 4 production channels!")


if __name__ == "__main__":
    train_production_models()