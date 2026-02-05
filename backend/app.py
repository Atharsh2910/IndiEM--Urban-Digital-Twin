from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from services import SimulationEngine
from dotenv import load_dotenv
import os
import json

# Load env vars
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)  # Enable CORS

# Initialize simulation engine
engine = SimulationEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "IndiEM Digital Twin Backend is running"})

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    try:
        year = int(request.args.get('year', 2025))
        scenario = request.args.get('scenario', 'Before')
        
        if year not in [2025, 2030, 2035, 2040]:
            return jsonify({"error": "Invalid year. Supported: 2025, 2030, 2035, 2040"}), 400
            
        print(f"Generating prediction for Year: {year}, Scenario: {scenario}")
        
        df = engine.get_prediction(year, scenario)
        geojson_str = engine.to_geojson(df)
        
        return geojson_str, 200, {'Content-Type': 'application/json'}
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/impact-analysis', methods=['GET'])
def get_impact_analysis():
    try:
        year = int(request.args.get('year', 2025))
        
        # Run "Before" simulation for that year
        df_before = engine.get_prediction(year, "Before")
        
        # Run "After" simulation for that year
        df_after = engine.get_prediction(year, "After")
        
        # Analyze
        from services import ImpactAnalysisEngine
        analysis = ImpactAnalysisEngine.analyze_impact(df_before, df_after)
        
        return jsonify(analysis), 200
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
