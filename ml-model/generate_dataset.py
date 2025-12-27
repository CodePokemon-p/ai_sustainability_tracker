import os
import random
import json
import csv
import math
import ezdxf
from PIL import Image, ImageDraw
import numpy as np

# ==============================
# ENHANCED CONFIG
# ==============================
OUTPUT_DIR = "fabric_dataset_enhanced"
TOTAL_SAMPLES = 2000
TRAIN_RATIO, VAL_RATIO, TEST_RATIO = 0.7, 0.2, 0.1
FABRIC_WIDTH, FABRIC_HEIGHT = 1500, 1000
IMG_SIZE = (224, 224)

# Enhanced categories for more diversity
PARTS = ["Sleeve", "Collar", "Front", "Back", "Pocket", "Cuff", "Yoke", "Placket", "Hem", "Facing"]
DEFECT_TYPES = ["none", "overlap", "misalign", "missing", "scaling", "clipping", "rotation_error", "deformation"]

# Fabric types for more realism
FABRIC_TYPES = ["cotton", "denim", "silk", "wool", "polyester", "linen", "knit", "stretch"]

# ==============================
# ENHANCED HELPERS
# ==============================
def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_complex_polygon():
    """Generate more diverse polygon shapes"""
    shape_type = random.choice(["regular", "irregular", "rectangular", "complex"])
    
    if shape_type == "regular":
        num_points = random.randint(5, 8)
        radius = random.randint(80, 250)
        angle_step = 2 * math.pi / num_points
        points = []
        for i in range(num_points):
            x = radius * math.cos(i * angle_step) + random.randint(-15, 15)
            y = radius * math.sin(i * angle_step) + random.randint(-15, 15)
            points.append((x, y))
    
    elif shape_type == "rectangular":
        width = random.randint(100, 300)
        height = random.randint(80, 200)
        points = [
            (-width/2, -height/2),
            (width/2, -height/2),
            (width/2, height/2),
            (-width/2, height/2)
        ]
        # Add some variation
        points = [(x + random.randint(-10, 10), y + random.randint(-10, 10)) for x, y in points]
    
    elif shape_type == "complex":
        num_points = random.randint(6, 12)
        base_radius = random.randint(70, 180)
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            radius_var = base_radius * random.uniform(0.7, 1.3)
            x = radius_var * math.cos(angle) + random.randint(-20, 20)
            y = radius_var * math.sin(angle) + random.randint(-20, 20)
            points.append((x, y))
    
    else:  # irregular
        num_points = random.randint(4, 7)
        points = []
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            radius = random.randint(60, 200)
            x = radius * math.cos(angle) + random.randint(-25, 25)
            y = radius * math.sin(angle) + random.randint(-25, 25)
            points.append((x, y))
    
    return points

def apply_enhanced_defect(points, defect_type):
    """More realistic defect simulation"""
    if defect_type == "none":
        return points
    
    elif defect_type == "misalign":
        shift_x = random.randint(-80, 80)
        shift_y = random.randint(-40, 40)
        return [(x + shift_x, y + shift_y) for x, y in points]
    
    elif defect_type == "scaling":
        scale_x = random.uniform(0.6, 1.8)
        scale_y = random.uniform(0.6, 1.8)
        return [(x * scale_x, y * scale_y) for x, y in points]
    
    elif defect_type == "clipping":
        clip_factor = random.uniform(0.3, 0.8)
        return [(x * clip_factor, y * clip_factor) for x, y in points]
    
    elif defect_type == "missing" and len(points) > 3:
        remove_count = random.randint(1, min(3, len(points)-3))
        return points[:-remove_count]
    
    elif defect_type == "overlap":
        # Create overlapping duplicate
        original = points.copy()
        shift = random.randint(-50, 50)
        overlap_points = [(x + shift, y + shift) for x, y in points]
        return original + overlap_points[:len(overlap_points)//2]
    
    elif defect_type == "rotation_error":
        angle = random.uniform(-math.pi/4, math.pi/4)  # ±45 degrees
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        return [(x * cos_a - y * sin_a, x * sin_a + y * cos_a) for x, y in points]
    
    elif defect_type == "deformation":
        # Random deformation of points
        deformed = []
        for x, y in points:
            deform_x = x * random.uniform(0.8, 1.2)
            deform_y = y * random.uniform(0.8, 1.2)
            deformed.append((deform_x, deform_y))
        return deformed
    
    return points

def polygon_area(points):
    x, y = zip(*points)
    area = 0.0
    n = len(points)
    for i in range(n):
        j = (i + 1) % n
        area += x[i] * y[j]
        area -= x[j] * y[i]
    return abs(area) / 2.0

def save_enhanced_dxf(points, filepath):
    try:
        doc = ezdxf.new()
        msp = doc.modelspace()
        # Convert points to list of tuples for ezdxf
        dxf_points = [(x, y, 0) for x, y in points]  # Add z-coordinate
        msp.add_lwpolyline(dxf_points)
        doc.saveas(filepath)
    except Exception as e:
        print(f"Warning: Could not save DXF {filepath}: {e}")

def save_enhanced_png(points, filepath, fabric_type):
    """Enhanced PNG generation with fabric textures"""
    img = Image.new("RGB", IMG_SIZE, "white")
    draw = ImageDraw.Draw(img)
    
    if not points or len(points) < 3:
        # Generate default triangle if points are invalid
        points = [(0, 0), (100, 0), (50, 100)]
    
    # Scale points to fit image
    try:
        min_x = min(x for x, y in points)
        max_x = max(x for x, y in points)
        min_y = min(y for x, y in points)
        max_y = max(y for x, y in points)
        
        # Avoid division by zero
        if max_x == min_x:
            max_x = min_x + 1
        if max_y == min_y:
            max_y = min_y + 1
            
        scale_x = (IMG_SIZE[0] - 40) / (max_x - min_x)
        scale_y = (IMG_SIZE[1] - 40) / (max_y - min_y)
        scale = min(scale_x, scale_y) * 0.8
        
        center_x, center_y = IMG_SIZE[0] / 2, IMG_SIZE[1] / 2
        poly_center_x = (min_x + max_x) / 2
        poly_center_y = (min_y + max_y) / 2
        
        scaled_points = []
        for x, y in points:
            scaled_x = (x - poly_center_x) * scale + center_x
            scaled_y = (y - poly_center_y) * scale + center_y
            scaled_points.append((scaled_x, scaled_y))
    except:
        # Fallback scaling
        scaled_points = [(x + IMG_SIZE[0]//2, y + IMG_SIZE[1]//2) for x, y in points]
    
    # Choose color based on fabric type
    fabric_colors = {
        "cotton": (240, 240, 240),
        "denim": (70, 100, 150),
        "silk": (250, 230, 200),
        "wool": (200, 200, 200),
        "polyester": (220, 220, 240),
        "linen": (240, 240, 220),
        "knit": (230, 230, 230),
        "stretch": (210, 210, 230)
    }
    
    color = fabric_colors.get(fabric_type, (200, 200, 200))
    
    try:
        draw.polygon(scaled_points, outline="black", fill=color, width=2)
    except:
        # Fallback: draw a simple rectangle
        draw.rectangle([50, 50, IMG_SIZE[0]-50, IMG_SIZE[1]-50], outline="black", fill=color, width=2)
    
    img.save(filepath)

# ==============================
# ENHANCED MAIN GENERATION
# ==============================
def generate_enhanced_dataset():
    summary = {}
    splits = {
        "train": int(TOTAL_SAMPLES * TRAIN_RATIO),
        "val": int(TOTAL_SAMPLES * VAL_RATIO),
        "test": TOTAL_SAMPLES - int(TOTAL_SAMPLES * (TRAIN_RATIO + VAL_RATIO)),
    }

    all_annotations = []

    for split in splits:
        split_dir = os.path.join(OUTPUT_DIR, split)
        ensure_dir(os.path.join(split_dir, "images"))
        ensure_dir(os.path.join(split_dir, "dxf"))

        labels_json, labels_csv = [], []
        csv_path = os.path.join(split_dir, "labels.csv")

        for i in range(splits[split]):
            pattern_id = f"{split}_{i:04d}"
            part = random.choice(PARTS)
            defect = random.choice(DEFECT_TYPES)
            fabric_type = random.choice(FABRIC_TYPES)

            base_poly = generate_complex_polygon()
            defect_poly = apply_enhanced_defect(base_poly, defect)

            area_used = polygon_area(defect_poly)
            utilization = area_used / (FABRIC_WIDTH * FABRIC_HEIGHT)

            dxf_path = os.path.join(split_dir, "dxf", f"{pattern_id}.dxf")
            png_path = os.path.join(split_dir, "images", f"{pattern_id}.png")

            save_enhanced_dxf(defect_poly, dxf_path)
            save_enhanced_png(defect_poly, png_path, fabric_type)

            record = {
                "id": pattern_id,
                "file_name": png_path,
                "part": part,
                "defect_type": defect,
                "fabric_type": fabric_type,
                "semantic": {
                    "area_used": float(area_used),
                    "utilization": float(utilization),
                    "complexity": len(defect_poly),
                    "aspect_ratio": random.uniform(0.3, 3.0)
                }
            }
            labels_json.append(record)
            labels_csv.append([pattern_id, part, defect, fabric_type, area_used, utilization])
            all_annotations.append(record)

            if (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{splits[split]} samples for {split}")

        with open(os.path.join(split_dir, "labels.json"), "w") as f:
            json.dump(labels_json, f, indent=2)

        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "part", "defect_type", "fabric_type", "area_used", "utilization"])
            writer.writerows(labels_csv)

        summary[split] = splits[split]
        print(f"✅ Generated {splits[split]} samples for {split}")

    with open(os.path.join(OUTPUT_DIR, "annotations.json"), "w") as f:
        json.dump(all_annotations, f, indent=2)

    with open(os.path.join(OUTPUT_DIR, "summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    print(f"🎉 Enhanced dataset generation complete! Total: {TOTAL_SAMPLES} samples")
    print(f"📊 Distribution: Train: {splits['train']}, Val: {splits['val']}, Test: {splits['test']}")

if __name__ == "__main__":
    generate_enhanced_dataset()