import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
import os

# ---------------- LOAD DATA ----------------
gen = pd.read_csv("../data/Plant_1_Generation_Data.csv")
weather = pd.read_csv("../data/Plant_1_Weather_Sensor_Data.csv")

# Keep only required columns
gen = gen[["DC_POWER"]]
weather = weather[[
    "AMBIENT_TEMPERATURE",
    "MODULE_TEMPERATURE",
    "IRRADIATION"
]]

# Align by index length (safe for this Kaggle dataset)
min_len = min(len(gen), len(weather))
gen = gen.iloc[:min_len]
weather = weather.iloc[:min_len]

# Combine datasets
df = pd.concat([weather, gen], axis=1)

# Drop missing values
df = df.dropna()

# ---------------- FEATURES & TARGET ----------------
X = df[["AMBIENT_TEMPERATURE", "MODULE_TEMPERATURE", "IRRADIATION"]]
y = df["DC_POWER"]

print("Training samples:", X.shape[0])

# ---------------- TRAIN MODEL ----------------
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# ---------------- SAVE MODEL (FIXED PATH) ----------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "solar_model.pkl")
pickle.dump(model, open(MODEL_PATH, "wb"))

print("✅ solar_model.pkl created successfully in models folder")
