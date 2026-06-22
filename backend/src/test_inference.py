from predict import predict_hardware_failure

# 1. Simulate a completely healthy machine state
healthy_sample = {
    "storage_smart_5": 0,
    "storage_smart_197": 0,
    "storage_smart_198": 0,
    "thermal_core_temp": 45.0,
    "thermal_ambient_temp": 24.0,
    "cooling_fan_rpm": 2100
}

# 2. Simulate a critical hardware failure state
critical_sample = {
    "storage_smart_5": 85,          # High reallocated sectors count
    "storage_smart_197": 12,        # High pending sectors count
    "storage_smart_198": 4,
    "thermal_core_temp": 88.0,      # Severe overheating
    "thermal_ambient_temp": 25.0,   # High core-to-ambient delta
    "cooling_fan_rpm": 950          # Slipping/stalling fan
}

print("--- Testing Healthy Inference Stream ---")
healthy_result = predict_hardware_failure(healthy_sample)
print(f"Overall Health Score: {healthy_result['overall_health_score']}")
print(f"Status: {healthy_result['status']}")
print(f"Action: {healthy_result['recommended_action']}\n")

print("--- Testing Critical Inference Stream ---")
critical_result = predict_hardware_failure(critical_sample)
print(f"Overall Health Score: {critical_result['overall_health_score']}")
print(f"Status: {critical_result['status']}")
print(f"Action: {critical_result['recommended_action']}")