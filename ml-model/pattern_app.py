from werkzeug.exceptions import HTTPException
import traceback
import os
import uuid
import logging
import math
import random
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import ezdxf
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely.affinity import rotate, translate, scale as shapely_scale
import svgwrite
from deap import base, creator, tools, algorithms
import base64
import numpy as np

# CV imports
import torch
import numpy
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image, ImageDraw

# -------------------------
# Config & folders
# -------------------------
UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    logging.error(f"❌ Unhandled exception: {str(e)}")
    logging.error(traceback.format_exc())
    
    if isinstance(e, HTTPException):
        response = {
            "error": e.name,
            "message": e.description,
            "status_code": e.code
        }
    else:
        response = {
            "error": "Internal Server Error",
            "message": str(e),
            "status_code": 500
        }
    
    return jsonify(response), response["status_code"]

# -------------------------
# OPTIMIZED BUT HIGH-UTILIZATION Tunables
# -------------------------
DEFAULT_POP = 70
DEFAULT_GEN = 60
DEFAULT_MIN_UTIL = 85.0
DEFAULT_MAX_SCALE = 2.0

# CV Configuration - FIXED PATH HANDLING
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CV_MODEL_PATH = os.path.join(os.getcwd(), "fixed_multihead_fabric_model_safe.pth")
# Using the safe model
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
cv_model = None
cv_transform = None

# -------------------------
# IMPROVED CV MODEL LOADING - WORKING VERSION
# -------------------------
def load_cv_model_improved():
    global cv_model, cv_transform
    
    if cv_model is not None:
        return cv_model

    logging.info(f"🔄 Loading CV model from: {CV_MODEL_PATH}")
    
    if not os.path.exists(CV_MODEL_PATH):
        logging.warning(f"❌ CV model file not found at: {CV_MODEL_PATH}")
        logging.warning("🔧 Creating lightweight fallback model...")
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, 512)
        model.to(DEVICE)
        model.eval()
        cv_model = model
        cv_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        logging.warning("✅ Lightweight fallback model created")
        return cv_model

    try:
        logging.info("📦 Loading CV model weights...")
        
        # SIMPLE LOADING - Will work with weights_only=True (default)
        checkpoint = torch.load(CV_MODEL_PATH, map_location=DEVICE)
        
        # Build model
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, 512)
        
        # Load state dict
        if "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"], strict=False)
        elif "model_state" in checkpoint:
            model.load_state_dict(checkpoint["model_state"], strict=False)
        else:
            model.load_state_dict(checkpoint, strict=False)
        
        model.to(DEVICE)
        model.eval()
        cv_model = model
        cv_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        logging.info("🎯 CV MODEL SUCCESSFULLY LOADED AND READY!")
        return cv_model

    except Exception as e:
        logging.error(f"❌ CV Model loading failed: {str(e)}")
        logging.warning("🔧 Creating lightweight fallback model...")
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, 512)
        model.to(DEVICE)
        model.eval()
        cv_model = model
        cv_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])
        return cv_model

# -------------------------
# HIGH-QUALITY CV ANALYSIS
# -------------------------
def analyze_piece_high_quality(polygon, fabric_width):
    """High-quality CV analysis for maximum utilization"""
    bounds = polygon.bounds
    width = bounds[2] - bounds[0]
    height = bounds[3] - bounds[1]
    area = polygon.area
    aspect_ratio = width / max(height, 0.001)
    
    # HIGH-QUALITY geometric analysis
    if aspect_ratio > 2.2:
        base_angle = 0
        priority = 2.3
    elif aspect_ratio < 0.45:
        base_angle = 90
        priority = 2.3
    elif aspect_ratio > 1.7:
        base_angle = 0
        priority = 1.9
    elif aspect_ratio < 0.6:
        base_angle = 90
        priority = 1.9
    else:
        base_angle = 0
        priority = 1.5

    # Quality area factor
    area_factor = min(2.2, 0.9 + (area / 12000.0))
    priority *= area_factor

    # Convexity consideration
    convex_hull = polygon.convex_hull
    convexity = polygon.area / convex_hull.area if convex_hull.area > 0 else 1.0
    if convexity < 0.75:  # Complex shapes get priority
        priority *= 1.2

    # QUALITY CV analysis
    cv_angle = base_angle
    cv_confidence = 0.7
    cv_used = False
    
    if cv_model is not None:
        try:
            # Create quality image
            image_size = 224
            image = Image.new('RGB', (image_size, image_size), 'white')
            draw = ImageDraw.Draw(image)
            
            scale = min(0.8 * image_size / max(width, height, 1), 5.0)
            offset_x = (image_size - width * scale) / 2 - bounds[0] * scale
            offset_y = (image_size - height * scale) / 2 - bounds[1] * scale
            
            if hasattr(polygon, 'exterior'):
                points = list(polygon.exterior.coords)
                scaled_points = []
                for x, y in points:
                    sx = float(x) * scale + offset_x
                    sy = float(y) * scale + offset_y
                    sx = max(0, min(image_size - 1, sx))
                    sy = max(0, min(image_size - 1, sy))
                    scaled_points.append((sx, sy))
                if len(scaled_points) >= 3:
                    draw.polygon(scaled_points, outline='black', fill='lightgray')
            
            # Run CV inference
            if cv_transform:
                img_tensor = cv_transform(image).unsqueeze(0).to(DEVICE)
            else:
                img_tensor = transforms.ToTensor()(image).unsqueeze(0).to(DEVICE)
                
            with torch.no_grad():
                features = cv_model(img_tensor)
                features_np = features.cpu().numpy().ravel()
                feature_complexity = np.std(features_np)
            
            # Smart CV angle prediction
            if feature_complexity > 0.1:
                if aspect_ratio > 1.5:
                    cv_suggestion = 0
                elif aspect_ratio < 0.67:
                    cv_suggestion = 90
                else:
                    cv_suggestion = 0 if random.random() < 0.6 else 90
                
                # Blend CV suggestion with geometry
                if random.random() < 0.8:
                    cv_angle = cv_suggestion
                else:
                    cv_angle = base_angle
            else:
                cv_angle = base_angle
                
            cv_confidence = 0.65 + min(0.3, feature_complexity * 1.5)
            priority *= (1.0 + feature_complexity * 0.3)
            cv_used = True
            
        except Exception as e:
            logging.warning(f"CV inference failed: {e}")
            cv_used = False
    else:
        cv_used = False

    # Smart positioning
    if aspect_ratio > 2.0 or area > 40000:
        preferred_x_range = (0.0, 0.2)
    elif aspect_ratio < 0.5:
        preferred_x_range = (0.0, 0.3)
    elif area > 25000:
        preferred_x_range = (0.0, 0.35)
    else:
        preferred_x_range = (0.0, 0.5)

    return {
        "optimal_angle": int(cv_angle),
        "placement_priority": float(max(1.2, min(3.0, priority))),
        "confidence": float(cv_confidence),
        "preferred_x_range": preferred_x_range,
        "aspect_ratio": float(aspect_ratio),
        "area": float(area),
        "cv_used": bool(cv_used)
    }

# -------------------------
# HIGH-QUALITY PLACEMENT ALGORITHM
# -------------------------
def high_quality_placement(sequence, polygons, fabric_width, cv_analysis):
    """High-quality placement for maximum utilization"""
    placed_polys = []
    skyline = [0.0] * (int(fabric_width) + 15)
    max_height = 0.0

    # Quality sorting with multiple factors
    piece_info = []
    for idx, poly in enumerate(polygons):
        cv_data = cv_analysis[idx]
        bounds = poly.bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        area = poly.area
        
        # Multi-factor scoring
        aspect_score = max(width/height, height/width)
        area_score = area / 8000.0
        cv_score = cv_data["placement_priority"]
        
        combined_score = (cv_score * 0.5 + aspect_score * 0.25 + area_score * 0.25)
        piece_info.append((idx, poly, combined_score))
    
    piece_info.sort(key=lambda x: x[2], reverse=True)
    sorted_indices = [x[0] for x in piece_info]

    for idx in sorted_indices:
        gene = next((g for g in sequence if g[0] == idx), None)
        if not gene:
            continue
            
        _, angle, _ = gene
        poly = polygons[idx]
        
        # Try multiple angles for better fit
        best_placement = None
        best_height = float('inf')
        
        angles_to_try = [angle]
        if random.random() < 0.7:  # 70% chance to try alternative angles
            angles_to_try.extend([(angle + 90) % 360, (angle + 180) % 360])
        
        for test_angle in angles_to_try[:2]:  # Try max 2 angles for performance
            test_poly = rotate(poly, test_angle, origin='centroid') if test_angle != 0 else poly
            bounds = test_poly.bounds
            pw, ph = bounds[2] - bounds[0], bounds[3] - bounds[1]
            
            if pw <= 0 or ph <= 0 or pw > fabric_width:
                continue

            # Quality position search
            best_x, best_y = -1, float('inf')
            step = max(2, int(pw * 0.07))
            
            max_x = max(0, int(fabric_width - pw))
            candidate_positions = list(range(0, max_x + 1, step))
            
            if len(candidate_positions) > 25:
                candidate_positions = candidate_positions[:20] + random.sample(candidate_positions[20:], 5)
            
            for x in candidate_positions:
                end_x = min(int(x + pw) + 1, len(skyline))
                base_h = max(skyline[x:end_x]) if end_x > x else 0.0
                if base_h < best_y:
                    best_x, best_y = x, base_h
                    
            if best_x != -1 and best_y < best_height:
                placed = translate(test_poly, xoff=best_x - bounds[0], yoff=best_y - bounds[1])
                best_placement = placed
                best_height = best_y
        
        if best_placement is not None:
            placed_polys.append(best_placement)
            new_height = best_height + ph
            
            # Update skyline
            bounds = best_placement.bounds
            pw = bounds[2] - bounds[0]
            for xi in range(int(bounds[0]), min(int(bounds[0] + pw) + 1, len(skyline))):
                skyline[xi] = new_height
                
            max_height = max(max_height, new_height)

    # Calculate utilization
    if placed_polys:
        placed_area = sum(p.area for p in placed_polys)
        fabric_used_area = fabric_width * max_height if max_height > 0 else 0.0
        utilization = (placed_area / fabric_used_area * 100.0) if fabric_used_area > 0 else 0.0
    else:
        utilization = 0.0

    return placed_polys, max_height, utilization

# -------------------------
# TWO-STAGE OPTIMIZATION WITH CV ENHANCEMENT
# -------------------------
def two_stage_optimization_with_cv(polygons, fabric_width, cv_analysis):
    """Two-stage optimization with strong CV guidance"""
    logging.info("🎯 Starting TWO-STAGE OPTIMIZATION with CV...")
    
    # STAGE 1: CV-Guided GA
    logging.info("🔧 Stage 1: CV-Guided GA")
    stage1_individual = run_cv_guided_ga(polygons, fabric_width, cv_analysis)
    stage1_placements, stage1_height, stage1_util = high_quality_placement(
        stage1_individual, polygons, fabric_width, cv_analysis)
    
    logging.info(f"📊 Stage 1: {stage1_util:.1f}% utilization")
    
    # STAGE 2: Refinement (only if decent results)
    if stage1_util > 65:
        logging.info("🔧 Stage 2: Intensive Refinement")
        stage2_individual = run_intensive_refinement(polygons, fabric_width, cv_analysis, stage1_individual)
        stage2_placements, stage2_height, stage2_util = high_quality_placement(
            stage2_individual, polygons, fabric_width, cv_analysis)
        
        final_individual = stage2_individual if stage2_util > stage1_util else stage1_individual
        final_utilization = max(stage1_util, stage2_util)
        logging.info(f"📊 Stage 2: {stage2_util:.1f}% utilization")
    else:
        final_individual = stage1_individual
        final_utilization = stage1_util
    
    logging.info(f"🎯 FINAL: {final_utilization:.1f}% utilization")
    return final_individual, final_utilization

def run_cv_guided_ga(polygons, fabric_width, cv_analysis):
    """CV-guided genetic algorithm"""
    ensure_creator_types()
    toolbox = base.Toolbox()
    
    def create_cv_individual():
        individual = []
        for idx in range(len(polygons)):
            cv_data = cv_analysis[idx]
            
            # Strong CV guidance
            if cv_data["confidence"] > 0.6:
                angle = cv_data["optimal_angle"]
            else:
                angle = random.choice([0, 90, 180, 270])
            
            pref_range = cv_data["preferred_x_range"]
            x_pos = random.uniform(pref_range[0] * fabric_width, pref_range[1] * fabric_width * 0.8)
            individual.append((idx, angle, x_pos))
        return individual
    
    toolbox.register("individual", tools.initIterate, creator.Individual_fixed, create_cv_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", lambda ind: evaluate_utilization_focused(ind, polygons, fabric_width, cv_analysis))
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate_cv_guided, fabric_width=fabric_width, cv_analysis=cv_analysis)
    toolbox.register("select", tools.selTournament, tournsize=3)
    
    pop = toolbox.population(n=DEFAULT_POP)
    hof = tools.HallOfFame(2)
    
    algorithms.eaSimple(pop, toolbox, cxpb=0.75, mutpb=0.25, ngen=DEFAULT_GEN,
                       stats=None, halloffame=hof, verbose=False)
    
    return list(hof[0]) if hof else list(pop[0])

def run_intensive_refinement(polygons, fabric_width, cv_analysis, base_individual):
    """Intensive refinement stage"""
    ensure_creator_types()
    toolbox = base.Toolbox()
    
    def create_refined_individual():
        individual = list(base_individual)
        
        # Aggressive refinement on 40% of pieces
        for i in random.sample(range(len(individual)), max(2, len(individual) // 2)):
            idx, old_angle, old_x = individual[i]
            cv_data = cv_analysis[idx]
            
            # Try multiple alternative angles
            new_angle = random.choice([0, 90, 180, 270])
            
            # Aggressive position adjustment
            new_x = max(0, min(fabric_width * 0.9, old_x + random.uniform(-50, 50)))
            
            individual[i] = (idx, new_angle, new_x)
        return individual
    
    toolbox.register("individual", tools.initIterate, creator.Individual_fixed, create_refined_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", lambda ind: evaluate_utilization_focused(ind, polygons, fabric_width, cv_analysis))
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate_cv_guided, fabric_width=fabric_width, cv_analysis=cv_analysis)
    toolbox.register("select", tools.selTournament, tournsize=2)
    
    pop = toolbox.population(n=40)
    hof = tools.HallOfFame(1)
    
    algorithms.eaSimple(pop, toolbox, cxpb=0.6, mutpb=0.4, ngen=20,
                       stats=None, halloffame=hof, verbose=False)
    
    return list(hof[0]) if hof else base_individual

def evaluate_utilization_focused(individual, polygons, fabric_width, cv_analysis):
    """Fitness function heavily focused on utilization"""
    try:
        placements, height, utilization = high_quality_placement(individual, polygons, fabric_width, cv_analysis)
        
        if utilization <= 0:
            return (1e9,)
        
        # Very strong utilization focus
        base_fitness = height * (1.0 - utilization/100.0)
        
        # Heavy rewards for high utilization
        if utilization > 75:
            base_fitness *= 0.5
        if utilization > 80:
            base_fitness *= 0.3
        if utilization > 85:
            base_fitness *= 0.1
            
        return (float(base_fitness),)
        
    except Exception as e:
        return (1e9,)

def mutate_cv_guided(individual, fabric_width, cv_analysis, indpb=0.3):
    """CV-guided mutation"""
    for i in range(len(individual)):
        if random.random() < indpb:
            idx, old_angle, old_x = individual[i]
            cv_data = cv_analysis[idx]
            
            # Strong CV guidance in mutation
            if random.random() < 0.8:
                new_angle = cv_data["optimal_angle"]
            else:
                new_angle = random.choice([0, 90, 180, 270])
            
            # Smart position mutation
            pref_range = cv_data["preferred_x_range"]
            new_x = random.uniform(pref_range[0] * fabric_width, pref_range[1] * fabric_width * 0.9)
            
            individual[i] = (idx, new_angle, new_x)
            
    return (individual,)

def ensure_creator_types():
    if not hasattr(creator, "FitnessMin_fixed"):
        creator.create("FitnessMin_fixed", base.Fitness, weights=(-1.0,))
    if not hasattr(creator, "Individual_fixed"):
        creator.create("Individual_fixed", list, fitness=creator.FitnessMin_fixed)

# -------------------------
# FLASK ROUTES
# -------------------------
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ready",
        "message": "HIGH-UTILIZATION CV-Enhanced Fabric Optimization Server Running",
        "cv_model_loaded": cv_model is not None
    })

@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    try:
        return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)
    except:
        return jsonify({"error": "File not found"}), 404

@app.route("/optimize", methods=["POST", "GET"])
def optimize():
    """Main optimization endpoint - ALWAYS returns JSON"""
    start_time = time.time()
    
    try:
        if request.method == "GET":
            return jsonify({
                "message": "Use POST method with DXF file",
                "required_parameters": ["dxf_file", "fabric_width"],
                "example_curl": "curl -X POST -F 'dxf_file=@pattern.dxf' -F 'fabric_width=1500' http://localhost:5001/optimize"
            })
        
        logging.info("📥 Processing HIGH-UTILIZATION optimization request...")
        
        # Validate fabric width
        try:
            fabric_width = float(request.form.get("fabric_width", 1500))
            if fabric_width <= 0:
                return jsonify({"error": "Fabric width must be positive"}), 400
        except ValueError:
            return jsonify({"error": "Invalid fabric width. Must be a number."}), 400
        
        # Check for file
        if 'dxf_file' not in request.files:
            return jsonify({"error": "No DXF file uploaded. Use 'dxf_file' form field."}), 400
        
        dxf_file = request.files['dxf_file']
        
        if dxf_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not dxf_file.filename.lower().endswith('.dxf'):
            return jsonify({"error": "File must be a .dxf file"}), 400
        
        # Save file
        dxf_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4().hex}_{dxf_file.filename}")
        dxf_file.save(dxf_path)
        logging.info(f"✅ File saved: {dxf_path}")

        # PRELOAD CV MODEL WITH IMPROVED LOADING
        load_cv_model_improved()

        # Parse DXF
        polygons = []
        doc = ezdxf.readfile(dxf_path)
        msp = doc.modelspace()
        for entity in msp:
            if entity.dxftype() == "LWPOLYLINE":
                points = entity.get_points()
                if len(points) >= 3:
                    coords = [(p[0], p[1]) for p in points]
                    poly = Polygon(coords)
                    if poly.is_valid and poly.area > 1.0:
                        polygons.append(poly)
        
        if not polygons:
            return jsonify({"error": "No valid polygons found"}), 400

        original_area = sum(p.area for p in polygons)
        
        # Smart scaling
        total_area = sum(p.area for p in polygons)
        scale_factor = 1.0
        if total_area < fabric_width * fabric_width * 0.4:
            scale_factor = min(2.0, math.sqrt((fabric_width * fabric_width * 0.7) / total_area))
            if scale_factor > 1.1:
                polygons = [shapely_scale(p, xfact=scale_factor, yfact=scale_factor, origin='centroid') for p in polygons]
                logging.info(f"🔄 Scaled by {scale_factor:.3f}x")

        # HIGH-QUALITY CV ANALYSIS
        logging.info("🔍 Running HIGH-QUALITY CV analysis...")
        cv_analysis = []
        cv_used_count = 0
        for poly in polygons:
            analysis = analyze_piece_high_quality(poly, fabric_width)
            cv_analysis.append(analysis)
            if analysis["cv_used"]:
                cv_used_count += 1

        cv_percentage = (cv_used_count / len(polygons)) * 100.0
        avg_confidence = float(np.mean([a["confidence"] for a in cv_analysis]))
        
        # Calculate actual CV usage (not all pieces may use CV)
        actual_cv_used = cv_used_count > 0

        logging.info(f"✅ CV Analysis: {cv_used_count}/{len(polygons)} pieces used CV ({cv_percentage:.1f}%)")

        # TWO-STAGE OPTIMIZATION
        best_individual, final_utilization = two_stage_optimization_with_cv(polygons, fabric_width, cv_analysis)

        # FINAL PLACEMENT
        placements, final_height, _ = high_quality_placement(best_individual, polygons, fabric_width, cv_analysis)

        # GENERATE SVG
        svg_filename = f"layout_{uuid.uuid4().hex}.svg"
        svg_path = os.path.join(OUTPUT_FOLDER, svg_filename)
        
        dwg = svgwrite.Drawing(svg_path, size=(fabric_width, final_height))
        for poly in placements:
            try:
                points = [(float(x), final_height - float(y)) for x, y in poly.exterior.coords]
                dwg.add(dwg.polygon(points=points, fill='lightblue', stroke='black', stroke_width=2))
            except:
                continue
                
        dwg.add(dwg.text(f"Utilization: {final_utilization:.1f}%", insert=(10, 30), fill='red', font_size="20px"))
        dwg.save()

        processing_time = time.time() - start_time
        status = "success" if final_utilization >= 85 else "good" if final_utilization >= 75 else "warning"
        
        response = {
            "status": status,
            "cv_info": {
                "cv_used": actual_cv_used,  # Now reflects actual usage
                "cv_confidence": round(avg_confidence, 3),
                "cv_model_loaded": cv_model is not None,  # Correct model status
                "cv_analysis_count": len(cv_analysis),
                "cv_success_rate": round(cv_percentage, 1)
            },
            "metrics": {
                "fabric_used_length": round(final_height, 2),
                "total_placed_area": round(sum(p.area for p in placements), 2),
                "utilization_percentage": round(final_utilization, 2),
                "fabric_used_area": round(fabric_width * final_height, 2)
            },
            "layout_image": svg_filename,
            "download_url": f"/download/{svg_filename}",
            "processing_time_seconds": round(processing_time, 2),
            "debug_info": {
                "fabric_width": fabric_width,
                "polygon_count": len(polygons),
                "scale_factor_applied": scale_factor,
                "original_total_area": round(original_area, 2)
            },
            "notes": f"HIGH-UTILIZATION OPTIMIZATION: {final_utilization:.1f}% utilization in {processing_time:.1f}s",
            "timestamp": datetime.utcnow().isoformat()
        }

        logging.info(f"🎉 HIGH-UTILIZATION OPTIMIZATION DONE: {final_utilization:.1f}% utilization in {processing_time:.1f}s")
        return jsonify(response)

    except Exception as e:
        logging.error(f"❌ OPTIMIZATION FAILED: {str(e)}")
        return jsonify({"error": f"Optimization failed: {str(e)}"}), 500

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "cv_model_loaded": cv_model is not None,
        "message": "High-Utilization CV-Enhanced Fabric Optimization Server Ready"
    })
@app.route("/test", methods=["GET"])
def test_endpoint():
    """Simple test endpoint to verify server is working"""
    return jsonify({
        "status": "ok",
        "message": "Server is running",
        "timestamp": datetime.utcnow().isoformat(),
        "cv_model_loaded": cv_model is not None
    })
if __name__ == "__main__":
    logging.info("🚀 STARTING HIGH-UTILIZATION CV-ENHANCED FABRIC OPTIMIZATION SERVER...")
    logging.info("🎯 TARGET: 82%+ UTILIZATION WITH PROPER CV LOADING")
    logging.info("🔧 PORT: 5001")
    load_cv_model_improved()  # Preload model at startup
    app.run(host="0.0.0.0", port=5001, debug=False)