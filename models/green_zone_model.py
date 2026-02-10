import pandas as pd
from sklearn.cluster import KMeans
import os
import ast

# ---------------- LOAD DATA ----------------
df = pd.read_csv("../data/campus_osm_data.csv")
print("Available columns:", df.columns.tolist())

# ---------------- EXTRACT LAT / LON FROM 'coordinates' ----------------
def parse_coordinates(val):
    """
    Expected formats:
    [lon, lat]
    (lon, lat)
    '[-72.57, 23.02]'
    """
    try:
        if isinstance(val, str):
            val = ast.literal_eval(val)
        if isinstance(val, (list, tuple)) and len(val) >= 2:
            lon, lat = val[0], val[1]
            return float(lat), float(lon)
    except Exception:
        pass
    return None, None

if "coordinates" not in df.columns:
    raise ValueError("❌ 'coordinates' column not found in campus_osm_data.csv")

df[["latitude_clean", "longitude_clean"]] = df["coordinates"].apply(
    lambda x: pd.Series(parse_coordinates(x))
)

# ---------------- CLEAN DATA ----------------
coords = df[["latitude_clean", "longitude_clean"]].dropna().reset_index(drop=True)

print("Valid coordinate points:", len(coords))

if len(coords) < 2:
    raise ValueError("Not enough valid points for K-Means clustering")

# ---------------- K-MEANS CLUSTERING ----------------
kmeans = KMeans(n_clusters=2, random_state=42)
coords["green_cluster"] = kmeans.fit_predict(coords)

# ---------------- SAVE OUTPUT ----------------
OUTPUT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "green_zone_output.csv"
)

coords.rename(
    columns={
        "latitude_clean": "latitude",
        "longitude_clean": "longitude"
    },
    inplace=True
)

coords.to_csv(OUTPUT_PATH, index=False)

print("✅ green_zone_output.csv created successfully")
