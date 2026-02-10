import os
import sys
import pickle
import pandas as pd
import numpy as np
import ast
from flask import Flask, jsonify
from flask_cors import CORS

# ---------------- PROJECT ROOT ----------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(BASE_DIR)

from models.carbon_model import carbon_reduction_kgs

app = Flask(__name__)
CORS(app)

# ---------------- LOAD MODEL ----------------
MODEL_PATH = os.path.join(BASE_DIR, "models", "solar_model.pkl")
solar_model = pickle.load(open(MODEL_PATH, "rb"))

# ---------------- LOAD DATA ----------------
campus = pd.read_csv(os.path.join(BASE_DIR, "data", "campus_osm_data.csv"))
green_zones = pd.read_csv(os.path.join(BASE_DIR, "data", "green_zone_output.csv"))

# ---------------- COORDINATE PARSING ----------------
def parse_coordinates(val):
    try:
        if isinstance(val, str):
            val = ast.literal_eval(val)
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            lon, lat = val[0], val[1]
            return float(lat), float(lon)
    except Exception:
        pass
    return None, None

campus[["lat", "lon"]] = campus["coordinates"].apply(
    lambda x: pd.Series(parse_coordinates(x))
)

# Fill missing coordinates with campus center (prevents empty output)
campus["lat"].fillna(campus["lat"].mean(), inplace=True)
campus["lon"].fillna(campus["lon"].mean(), inplace=True)

# ---------------- ROOT ----------------
@app.route("/")
def home():
    return jsonify({
        "status": "Backend running",
        "endpoints": ["/solar", "/green-zones", "/carbon", "/recommendations"]
    })

# ---------------- SOLAR API ----------------
@app.route("/solar")
def solar():
    results = []

    for _, row in campus.iterrows():
        # Average environmental conditions (assumption-based)
        features = np.array([[32, 45, 6.5]])
        predicted_power = solar_model.predict(features)[0]

        # Scale power for campus-level demo
        energy_kwh = round(abs(predicted_power) / 100, 2)

        results.append({
            "building": row.get("name", "Campus Block"),
            "lat": row["lat"],
            "lon": row["lon"],
            "predicted_energy_kwh": energy_kwh
        })

    return jsonify(results)

# ---------------- CARBON API ----------------
@app.route("/carbon")
def carbon():
    carbon_data = []

    for _, row in campus.iterrows():
        # Use same assumed energy for consistency
        energy_kwh = 10
        carbon_data.append({
            "building": row.get("name", "Campus Block"),
            "carbon_saved_kg": carbon_reduction_kgs(energy_kwh)
        })

    return jsonify(carbon_data)

# ---------------- GREEN ZONES ----------------
@app.route("/green-zones")
def green():
    return jsonify(green_zones.to_dict(orient="records"))

# ---------------- AI RECOMMENDATIONS ----------------
@app.route("/recommendations")
def recommendations():
    recs = [
        "Install rooftop solar panels on high-exposure buildings",
        "Increase tree plantation in clustered green zones",
        "Adopt smart energy monitoring systems",
        "Promote renewable energy awareness across campus"
    ]
    return jsonify(recs)

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
