import sys
import os
import pandas as pd
import numpy as np

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from services import SimulationEngine, ImpactAnalysisEngine

def test_impact_analysis():
    print("Initializing SimulationEngine...")
    engine = SimulationEngine()
    
    year = 2030
    print(f"Testing Impact Analysis for Year {year}...")
    
    df_before = engine.get_prediction(year, "Before")
    df_after = engine.get_prediction(year, "After")
    
    analysis = ImpactAnalysisEngine.analyze_impact(df_before, df_after)
    
    print("\n--- Analysis Results ---")
    print(f"Severity: {analysis['severity']}")
    print("Deltas:", analysis['delta_metrics'])
    print("Recommendations:")
    for r in analysis['recommendations']:
        print(f"- {r}")
        
    # Validation assertions
    if analysis['delta_metrics']['temperature_rise'] < 1.4:
        print("❌ FAILED: Temp rise too low (should be ~1.5).")
        sys.exit(1)
        
    if "High Impact" not in analysis['severity']:
        print("❌ FAILED: Severity should be High given the large temp increase.")
        sys.exit(1)

    print("\n✅ Impact Analysis Verification Passed!")

if __name__ == "__main__":
    test_impact_analysis()
