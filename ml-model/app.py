from flask import Flask, request, jsonify
import joblib
import numpy as np
import google.generativeai as genai
from flask_cors import CORS
import json
import time
import re
from datetime import datetime
import os
from dotenv import load_dotenv
# load .env variables
load_dotenv()


app = Flask(__name__)
CORS(app)

# --- Load model + scaler ---
clf = joblib.load("carbon_water_predictor.pkl")
scaler = joblib.load("scaler.pkl")

# Load Gemini API keys
GEMINI_KEYS = [
    os.getenv("GEMINI_KEY_1", "").strip('"').strip(),
    os.getenv("GEMINI_KEY_2", "").strip('"').strip(),
    os.getenv("GEMINI_KEY_3", "").strip('"').strip()
]
API_KEYS = [k for k in GEMINI_KEYS if k and k != ""]

# Debug: Print how many keys loaded (remove this line after testing)
print(f"✅ Loaded {len(API_KEYS)} Gemini API keys")

# --- Product type encoding ---
PRODUCT_MAP = {
    "Polyester": 0,
    "Cotton": 1,
    "Nylon": 2,
    "Recycled_Poly": 3,
    "Organic_Cotton": 4,
    "Synthetic_Blend": 5,
    "Microfiber": 6,
    "Silk": 7,
    "Denim": 8,
    "Lawn": 9,
    "Viscose": 10,
    "Linen": 11,
    "Rayon": 12
}

class GeminiModelManager:
    def __init__(self):
        self.available_models_cache = {}
        self.model_priority_cache = {}
        self.cache_timestamp = 0
        self.cache_duration = 3600  # 1 hour cache
        
    def get_available_models(self, api_key):
        """Get available models for API key with caching"""
        current_time = time.time()
        
        # Return cached results if still valid
        if (api_key in self.available_models_cache and 
            current_time - self.cache_timestamp < self.cache_duration):
            return self.available_models_cache[api_key]
            
        try:
            genai.configure(api_key=api_key)
            available_models = genai.list_models()
            working_models = []
            
            for model in available_models:
                model_name = model.name.split('/')[-1]
                if 'generateContent' in model.supported_generation_methods:
                    working_models.append(model_name)
            
            self.available_models_cache[api_key] = working_models
            self.cache_timestamp = current_time
            
            print(f"✅ Available models for key: {working_models}")
            return working_models
            
        except Exception as e:
            print(f"❌ Failed to get models for key: {e}")
            return []
    
    def score_model(self, model_name):
        """Score models based on stability, performance, and recency"""
        score = 0
        
        # Prefer stable models over preview
        if '-preview' in model_name:
            score -= 20
        if 'stable' in model_name:
            score += 30
            
        # Prefer production-ready models
        if any(x in model_name for x in ['flash-latest', 'pro-latest', 'latest']):
            score += 50
            
        # Prefer numbered versions (they're more stable)
        version_match = re.search(r'(\d+\.\d+)', model_name)
        if version_match:
            try:
                version = float(version_match.group(1))
                score += version * 10  # Higher versions get higher scores
            except:
                pass
            
        # Prefer flash for speed, pro for quality
        if 'flash' in model_name:
            score += 25  # Fast and efficient
        if 'pro' in model_name:
            score += 30  # Higher quality
            
        # Penalize experimental and specialty models
        if any(x in model_name for x in ['exp', 'thinking', 'tts', 'image', 'robotics', 'computer-use']):
            score -= 40
            
        # Penalize dated preview models
        date_match = re.search(r'(\d{2}-\d{4})', model_name)
        if date_match:
            # Older preview models get lower scores
            preview_date = date_match.group(1)
            try:
                preview_dt = datetime.strptime(preview_date, '%m-%Y')
                days_old = (datetime.now() - preview_dt).days
                score -= min(days_old / 30, 50)  # Penalize by months old
            except:
                pass
                
        return score
    
    def get_best_models(self, api_key, count=3):
        """Get the top N best models based on scoring"""
        available_models = self.get_available_models(api_key)
        if not available_models:
            return []
            
        # Score and sort models
        scored_models = []
        for model in available_models:
            score = self.score_model(model)
            scored_models.append((model, score))
            
        # Sort by score descending
        scored_models.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N models
        best_models = [model for model, score in scored_models[:count]]
        print(f"🏆 Best models for API key: {best_models}")
        return best_models

# Initialize model manager
model_manager = GeminiModelManager()
# Add this function AFTER the GeminiModelManager class ends
def test_api_key(api_key):
    """Simple test to check if API key works"""
    try:
        genai.configure(api_key=api_key)
        models = genai.list_models()
        return True
    except Exception as e:
        return False

# -----------------------------
# === New math layer helpers ===
# -----------------------------
def RegressionModel(features_scaled: np.ndarray) -> float:
    """
    R: RegressionModel (mathematical linear estimator).
    We do not retrain here (time constraints). Instead we compute a principled
    linear estimate on the scaled environmental features (excluding product index).
    Returns a normalized continuous score in 0..1.
    """
    # features_scaled: shape (1, 6) -> [product_type_encoded, ghg, water, energy, pollutants, waste]
    # use only continuous numeric inputs (indices 1..5)
    numeric = features_scaled.flatten()[1:6]  # length 5
    # weights chosen by domain: heavier weight to GHG and water (tunable)
    weights = np.array([0.35, 0.30, 0.20, 0.10, 0.05])  # sums to 1.0
    # linear combination
    raw = float(np.dot(numeric, weights))
    # Normalize: raw is on scaled feature space (unknown bounds). Convert using logistic to 0..1
    reg_score = 1.0 / (1.0 + np.exp(-raw))
    return reg_score

def RNucleus(features_scaled: np.ndarray) -> float:
    """
    RNucleus: a stability / signal-strength metric derived from feature dispersion.
    Used to weight how much we trust Regression vs Classification.
    Returns a value in 0..1 where higher means more 'stable' signal.
    """
    numeric = features_scaled.flatten()[1:6]
    std = float(np.std(numeric))
    # Normalize std into 0..1 via tanh-like transform. Smaller std -> closer to 1 (stable)
    nuc = 1.0 - (np.tanh(std) / np.tanh(3.0))  # clamp-ish; if std large -> lower nucleus
    nuc = max(0.0, min(1.0, nuc))
    return nuc

def RLCV(reg_score: float, class_confidence: float, nucleus: float) -> (float, float):
    """
    RLCV: Regression Linear-Convex Variable
    - alpha is regression weight derived from RNucleus (nucleus closer to 1 -> rely more on regression)
    - We compute final convex fusion: fused = alpha*reg_score + (1-alpha)*class_confidence
    Returns (fused_score, alpha)
    """
    # Tune how nucleus maps to alpha: emphasize regression when nucleus high
    alpha = 0.55 + 0.4 * nucleus  # alpha in [0.55, 0.95]
    alpha = max(0.0, min(1.0, alpha))
    fused = alpha * reg_score + (1 - alpha) * class_confidence
    fused = max(0.0, min(1.0, fused))
    return fused, alpha

def convert_to_class_from_score(score: float) -> str:
    """Map fused score (0..1) to class labels used in frontend/paper"""
    if score < 0.34:
        return "Low"
    elif score < 0.67:
        return "Moderate"
    else:
        return "High"

# -----------------------------
# --- Helper: Get dynamic Gemini response ---
# -----------------------------
def get_gemini_response(eco_level: str, eco_score: float, tone: str, co2: float = None, water: float = None) -> dict:
    style = "professional" if tone == "professional" else "friendly"
    
    # SIMPLE, WORKING PROMPT - Just improved for diversity
    prompt = f"""
    You are an environmental sustainability consultant for clothing brands. 
    Provide fresh, diverse responses each time - never repeat the same phrasing or suggestions.
    
    Context:
    - Tone: {style}
    - Eco Level: {eco_level}
    - Eco Score: {eco_score:.2f}
    - CO₂ emissions: {co2} tons
    - Water Consumption: {water} liters

    Return ONLY a valid JSON object with the following structure:
    {{
        "reason": "Brief explanation of why this eco level was assigned (2-3 sentences)",
        "suggestions": [
            "First actionable suggestion for improvement",
            "Second actionable suggestion for improvement", 
            "Third actionable suggestion for improvement"
        ],
        "prediction": "Forecast of likely outcomes if suggestions are implemented (2-3 sentences)"
    }}

    Important:
    - Vary your language and suggestions significantly each time
    - Do not include any additional text outside the JSON object
    - Do not use markdown formatting
    - Ensure the JSON is valid and properly formatted
    """

       # Try each API key with its best available models
    for i, key in enumerate(API_KEYS):
        # First test if key is valid
        if not test_api_key(key):
            print(f"❌ API Key {i+1} is invalid or has no access")
            continue
            
        best_models = model_manager.get_best_models(key)
        if not best_models:
            print(f"⚠️ No suitable models found for API key {i+1}")
            # Try with default models
            best_models = ["gemini-1.5-pro-latest", "gemini-1.5-flash-latest"]
            
        for model_name in best_models:
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.8,  # Slightly higher for diversity
                        "top_p": 0.9,
                        "top_k": 40
                    }
                )
                text = response.text.strip()
                
                # Clean the response
                text = text.replace("```json", "").replace("```", "").strip()
                
                # Try to parse JSON
                try:
                    data = json.loads(text)
                    if all(key in data for key in ["reason", "suggestions", "prediction"]):
                        print(f"✅ Success with API key {i+1}, model: {model_name}")
                        return data
                    else:
                        print(f"⚠️ API key {i+1}, model {model_name}: Missing required fields")
                        continue
                except json.JSONDecodeError as e:
                    print(f"⚠️ API key {i+1}, model {model_name}: JSON parse error: {e}")
                    # Use the text anyway with fallback structure
                    return {
                        "reason": text,
                        "suggestions": [
                            "Implement energy-efficient manufacturing processes",
                            "Adopt water recycling systems in production",
                            "Optimize supply chain logistics for lower emissions"
                        ],
                        "prediction": "With proper sustainability measures, significant environmental impact reduction is achievable."
                    }
                    
            except Exception as e:
                print(f"❌ API key {i+1}, model {model_name}: {str(e)}")
                # Remove this model from cache if it fails
                if key in model_manager.available_models_cache:
                    if model_name in model_manager.available_models_cache[key]:
                        model_manager.available_models_cache[key].remove(model_name)
                continue

    # Fallback response if all models fail
    return {
        "reason": f"Based on your environmental metrics (CO₂: {co2} tons, Water: {water} liters), your brand is at a {eco_level} sustainability level. This indicates opportunities for improvement in production processes.",
        "suggestions": [
            "Implement energy-efficient technologies in manufacturing",
            "Adopt water recycling systems in dyeing processes",
            "Optimize supply chain logistics to reduce carbon footprint"
        ],
        "prediction": f"By implementing sustainable practices, {eco_level} brands typically achieve 25-40% environmental impact reduction within 12-18 months."
    }

# --- API Route: Prediction ---
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        required_fields = [
            "greenhouse_gas_emissions",
            "water_consumption",
            "energy_consumption",
            "pollutants_emitted",
            "waste_generation",
            "tone"
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Product type encoding
        if "product_type_encoded" not in data:
            if "product_type" in data:
                product_type = data["product_type"].strip().replace(" ", "_")
                if product_type in PRODUCT_MAP:
                    data["product_type_encoded"] = PRODUCT_MAP[product_type]
                else:
                    return jsonify({"error": f"Unknown product_type: {product_type}"}), 400
            else:
                return jsonify({"error": "Missing product_type"}), 400

        # Prepare features
        features = np.array([[  
            data["product_type_encoded"],
            data["greenhouse_gas_emissions"],
            data["water_consumption"],
            data["energy_consumption"],
            data["pollutants_emitted"],
            data["waste_generation"]
        ]], dtype=float)

        features_scaled = scaler.transform(features)

        # ----- CLASSIFIER outputs (keep existing behavior) -----
        try:
            class_label = clf.predict(features_scaled)[0]
            class_confidence = float(clf.predict_proba(features_scaled).max())
        except Exception as e:
            # If classifier lacks predict_proba, fall back to 0.5 confidence
            class_label = str(clf.predict(features_scaled)[0])
            class_confidence = 0.5

        tone = data["tone"]

        # ----- NEW: Regression + RLCV fusion -----
        reg_score = RegressionModel(features_scaled)          # continuous 0..1 (R)
        nucleus = RNucleus(features_scaled)                   # RNucleus (0..1)
        fused_score, alpha = RLCV(reg_score, class_confidence, nucleus)  # RLCV fusion

        # Map fused score to final eco level for front-end (keeps existing UI behavior)
        eco_level = convert_to_class_from_score(fused_score)
        eco_score = float(fused_score)  # normalized 0..1 numeric score

        # Get Gemini response (same call signature)
        analysis_dict = get_gemini_response(
            eco_level=eco_level,
            eco_score=eco_score,
            tone=tone,
            co2=data.get("greenhouse_gas_emissions"),
            water=data.get("water_consumption")
        )

        # Return extended information (includes R, RLCV, RNucleus for viva/debug)
        return jsonify({
            "eco_level": eco_level,
            "eco_score": eco_score,
            "analysis": analysis_dict,
            # Extra fields for reproducibility / viva display
            "internal": {
                "classification_label": str(class_label),
                "classification_confidence": round(class_confidence, 4),
                "regression_R": round(reg_score, 4),
                "rnucleus": round(nucleus, 4),
                "rlcv_alpha": round(alpha, 4),
                "rlcv_fused_score": round(fused_score, 4)
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- API Route: Generate response only ---
@app.route("/generate_response", methods=["POST"])
def generate_response():
    try:
        data = request.get_json()
        eco_level = data.get("eco_level")
        tone = data.get("tone", "professional")
        prompt = data.get("prompt")

        if prompt:
            for i, key in enumerate(API_KEYS):
                best_models = model_manager.get_best_models(key)
                for model_name in best_models:
                    try:
                        genai.configure(api_key=key)
                        model = genai.GenerativeModel(model_name)
                        
                        # Simple enhanced prompt for diversity
                        enhanced_prompt = f"""
                        You are a sustainability expert. Provide fresh, diverse perspectives.
                        
                        Request: {prompt}
                        
                        Instructions:
                        - Provide unique, varied responses each time
                        - Include specific examples and actionable advice
                        - Use {tone} tone
                        - Be engaging and professional
                        """
                        
                        response = model.generate_content(
                            enhanced_prompt,
                            generation_config={
                                "temperature": 0.8,
                                "top_p": 0.9,
                                "top_k": 40
                            }
                        )
                        text = response.text.strip()
                        
                        return jsonify({
                            "success": True,
                            "response": text
                        })
                        
                    except Exception as e:
                        print(f"Error with API key {i+1}, model {model_name}: {str(e)}")
                        continue

            return jsonify({"error": "All models failed to generate response"}), 500

        if not eco_level:
            return jsonify({"error": "Missing required field: eco_level"}), 400

        analysis_dict = get_gemini_response(eco_level, 0.5, tone)
        return jsonify({"generated_text": str(analysis_dict), "parsed": analysis_dict})

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# --- Health check to test models ---
@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint to see available models"""
    health_info = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "available_models": {}
    }
    
    for i, key in enumerate(API_KEYS):
        models = model_manager.get_available_models(key)
        best_models = model_manager.get_best_models(key)
        health_info["available_models"][f"api_key_{i+1}"] = {
            "all_models": models,
            "best_models": best_models
        }
    
    return jsonify(health_info)
    #---so this for tone checker in msg alert tool---
@app.route("/analyze_message", methods=["POST"])
def analyze_message():
    msg = request.json.get("message", "")
    tone = "urgent" if any(word in msg.lower() for word in ["alert", "high", "critical", "urgent"]) else "neutral"
    return jsonify({"tone": tone})

# --- Start Flask ---
if __name__ == "__main__":
    print("🚀 Flask API running on http://127.0.0.1:5000")
    print("🔍 Testing Gemini API keys...")
    
    # Quick test of each API key
    for i, key in enumerate(API_KEYS):
        if test_api_key(key):
            print(f"✅ API Key {i+1}: VALID")
            best_models = model_manager.get_best_models(key)
            if best_models:
                print(f"   Available models: {best_models[:2]}")  # Show first 2
        else:
            print(f"❌ API Key {i+1}: INVALID - Check your .env file")
    
    print("💡 Visit http://127.0.0.1:5000/health to see available models")
    app.run(debug=False)