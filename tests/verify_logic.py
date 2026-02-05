import sys
import os
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from services import SimulationEngine

def test_simulation():
    print("Initializing SimulationEngine...")
    engine = SimulationEngine()
    
    print("Testing 2030 Prediction (Before Scenario)...")
    res_2030 = engine.get_prediction(2030, "Before")
    
    base_temp = engine.base_df["temperature"].mean()
    pred_temp = res_2030["temperature"].mean()
    
    print(f"Base Mean Temp: {base_temp:.4f}")
    print(f"2030 Mean Temp: {pred_temp:.4f}")
    
    if pred_temp <= base_temp:
        print("❌ FAILED: Projected temperature did not increase.")
        sys.exit(1)
        
    print("Testing IT Park Impact (After Scenario)...")
    res_after = engine.get_prediction(2025, "After")
    
    # Filter IT park area
    # x: 18-21, y: 10-13
    mask = (res_after["x"].between(18, 21)) & (res_after["y"].between(10, 13))
    it_park_temps = res_after.loc[mask, "temperature"]
    base_it_temps = engine.base_df.loc[mask, "temperature"]
    
    diff = it_park_temps.mean() - base_it_temps.mean()
    print(f"IT Park Temp Difference: {diff:.4f}")
    
    if diff < 1.4: # Should be +1.5 exactly basically
        print("❌ FAILED: IT Park impact not applied correctly.")
        sys.exit(1)
        
    print("✅ Verification Passed!")

if __name__ == "__main__":
    test_simulation()
