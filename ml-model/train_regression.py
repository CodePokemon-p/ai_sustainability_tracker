import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
df = pd.read_csv("cleaned_textile_data.csv")

# Debug: show columns
print("✅ Dataset loaded. Columns:", df.columns.tolist())
print(df.head())

# Encode Product_Type
le = LabelEncoder()
df["product_type_encoded"] = le.fit_transform(df["Product_Type"])
joblib.dump(le, "product_type_encoder.pkl")
print("🔢 Encoded Product_Type into product_type_encoded")

# Rename Eco friendly → eco_level
df = df.rename(columns={"Eco friendly": "eco_level"})

# Define features + target
required_features = [
    "product_type_encoded",
    "Greenhouse_Gas_Emissions",
    "Water_Consumption",
    "Energy_Consumption",
    "Pollutants_Emitted",
    "Waste_Generation"
]

for col in required_features:
    if col not in df.columns:
        raise ValueError(f"❌ Missing column in dataset: {col}")

X = df[required_features]
y = df["eco_level"]  # now matches app.py expectations

# Normalize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train classifier
clf = RandomForestClassifier(
    n_estimators=200, random_state=42, class_weight="balanced"
)
clf.fit(X_scaled, y)

# Save model + scaler
joblib.dump(clf, "carbon_water_predictor.pkl")
joblib.dump(scaler, "scaler.pkl")

print("🎉 Training complete! Saved carbon_water_predictor.pkl and scaler.pkl")
