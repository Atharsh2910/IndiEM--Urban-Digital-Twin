import sys
import os
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services import SimulationEngine

def test_geojson():
    engine = SimulationEngine()
    geojson_str = engine.get_it_park_geojson()
    
    if not geojson_str:
        print("GeoJSON is None!")
        return

    data = json.loads(geojson_str)
    print(f"Features count: {len(data.get('features', []))}")
    
    for f in data.get('features', []):
        props = f.get('properties', {})
        geom = f.get('geometry', {})
        print(f"Type: {props.get('type')}, Geometry: {geom.get('type')}")

if __name__ == "__main__":
    test_geojson()
