import os
import hashlib
import pandas as pd
import numpy as np
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# ---------------- CONFIGURATION ----------------
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

app = Flask(__name__, 
            template_folder=FRONTEND_DIR, 
            static_folder=FRONTEND_DIR, 
            static_url_path='')
CORS(app)

# ---------------- DATA LOADING ----------------
campus_path = os.path.join(DATA_DIR, "campus_osm_data.csv")
if os.path.exists(campus_path):
    campus_df = pd.read_csv(campus_path)
    missing_names = campus_df["name"].isna()
    if missing_names.any():
        campus_df.loc[missing_names, "name"] = "Building " + (campus_df.index[missing_names] + 1).astype(str)
else:
    campus_df = pd.DataFrame(columns=["name", "lat", "lon"])

# ---------------- HELPER ----------------
def generate_deterministic_value(lat, lon, min_val, max_val):
    """Generates consistent values based on location"""
    input_str = f"{lat:.5f}-{lon:.5f}"
    hash_object = hashlib.md5(input_str.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    normalized = hash_int / (2**128)
    return min_val + (normalized * (max_val - min_val))

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/solar")
def solar():
    results = []
    if not campus_df.empty:
        limit = min(len(campus_df), 8)
        for i in range(limit):
            row = campus_df.iloc[i]
            val = generate_deterministic_value(i, i, 50, 150) 
            results.append({
                "building": str(row["name"]),
                "predicted_energy_kwh": round(val, 2)
            })
    return jsonify(results)

@app.route("/carbon")
def carbon():
    results = []
    if not campus_df.empty:
        limit = min(len(campus_df), 8)
        for i in range(limit):
            row = campus_df.iloc[i]
            val = generate_deterministic_value(i, i, 40, 120)
            results.append({
                "building": str(row["name"]),
                "carbon_saved_kg": round(val * 0.82, 2)
            })
    return jsonify(results)

@app.route("/recommendations")
def recommendations():
    return jsonify([
        "Optimize solar panel tilt to 23° on Main Block",
        "Plant 50 Neem trees in Zone A (North Campus)",
        "Implement automated HVAC controls in Library",
        "Install 15kW rooftop solar capacity on Hostel B"
    ])

# --- MAIN FEATURE: AREA ANALYSIS ---
@app.route("/analyze_region", methods=['POST'])
def analyze_region():
    data = request.json
    lat_min = data.get("lat_min")
    lat_max = data.get("lat_max")
    lon_min = data.get("lon_min")
    lon_max = data.get("lon_max")

    grid_points = []
    lat_step = (lat_max - lat_min) / 6
    lon_step = (lon_max - lon_min) / 6

    total_solar = 0
    tree_count = 0
    build_score = 0
    
    # Track counts to determine best suggestion
    suggestion_counts = {"SOLAR": 0, "TREE": 0, "BUILD": 0}

    current_lat = lat_min + (lat_step/2)
    while current_lat < lat_max:
        current_lon = lon_min + (lon_step/2)
        while current_lon < lon_max:
            
            irradiance = generate_deterministic_value(current_lat, current_lon, 2.0, 9.0)
            temp = generate_deterministic_value(current_lat, current_lon, 25.0, 45.0)
            
            rec = "NEUTRAL"
            if irradiance > 6.0:
                rec = "SOLAR"
                total_solar += irradiance
                suggestion_counts["SOLAR"] += 1
            elif temp > 32: # Lower threshold to trigger trees more often
                rec = "TREE"
                tree_count += 1
                suggestion_counts["TREE"] += 1
            else:
                rec = "BUILD"
                build_score += 1
                suggestion_counts["BUILD"] += 1

            grid_points.append({
                "lat": current_lat,
                "lon": current_lon,
                "recommendation": rec
            })
            current_lon += lon_step
        current_lat += lat_step

    # Determine Dominant Suggestion
    best_type = max(suggestion_counts, key=suggestion_counts.get)
    main_recommendation = ""
    
    if best_type == "SOLAR":
        main_recommendation = "☀️ Optimal for Solar Farm (High Irradiance)"
    elif best_type == "TREE":
        main_recommendation = "🌳 Recommended for Green Zone (Heat Reduction)"
    else:
        main_recommendation = "🏗️ Suitable for Infrastructure/Building"

    return jsonify({
        "grid_points": grid_points,
        "summary": {
            "avg_solar": round(total_solar, 1),
            "tree_count": tree_count * 5,
            "build_score": round(build_score, 1),
            "main_rec": main_recommendation # New Field
        }
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)