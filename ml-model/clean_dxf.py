import ezdxf
from shapely.geometry import Polygon, LineString
from shapely.ops import linemerge, polygonize, unary_union
import sys
import math

TOLERANCE = 1e-2  # snapping tolerance (mm)
SCALE_TARGET = 1000.0  # normalize so largest piece ~1000mm (1m)

def detect_scale(polygons):
    """
    Auto-detect if scaling is needed.
    Returns a factor (1.0 = already mm).
    """
    if not polygons:
        return 1.0
    max_dim = max(max(p.bounds[2]-p.bounds[0], p.bounds[3]-p.bounds[1]) for p in polygons)
    if max_dim < 10:  # likely inches or pixels → too tiny
        return 25.4   # inches to mm
    elif max_dim > 5000:  # too big, shrink to ~1m
        return SCALE_TARGET / max_dim
    return 1.0

def clean_dxf(input_file, output_file):
    # Load DXF
    doc = ezdxf.readfile(input_file)
    msp = doc.modelspace()

    lines = []

    # Collect geometry
    for e in msp:
        try:
            etype = e.dxftype()
            if etype == "LINE":
                lines.append(LineString([(e.dxf.start.x, e.dxf.start.y),
                                         (e.dxf.end.x, e.dxf.end.y)]))
            elif etype == "LWPOLYLINE":
                pts = [(p[0], p[1]) for p in e.get_points()]
                if e.closed:
                    pts.append(pts[0])
                lines.append(LineString(pts))
            elif etype == "SPLINE":
                pts = [(float(x), float(y)) for x, y in e.approximate(100)]
                lines.append(LineString(pts))
        except Exception:
            continue

    if not lines:
        print("⚠️ No usable geometry found in DXF.")
        return

    # Merge + polygonize
    merged = unary_union(lines)
    merged = linemerge(merged)
    polygons = list(polygonize(merged))

    if not polygons:
        print("⚠️ No polygons built. Try increasing TOLERANCE.")
        return

    # Detect + apply scale
    scale_factor = detect_scale(polygons)
    print(f"🔎 Detected scale factor: {scale_factor:.3f}")

    scaled_polygons = []
    for poly in polygons:
        if not isinstance(poly, Polygon):
            continue
        coords = [(x * scale_factor, y * scale_factor) for x, y in poly.exterior.coords]
        scaled_polygons.append(Polygon(coords))

    # Save to new DXF
    new_doc = ezdxf.new("R2010")
    new_msp = new_doc.modelspace()

    for poly in scaled_polygons:
        coords = list(poly.exterior.coords)
        new_msp.add_lwpolyline(coords, close=True)

    new_doc.saveas(output_file)
    print(f"✅ Cleaned & scaled DXF saved to {output_file}, polygons: {len(scaled_polygons)}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python clean_dxf.py input.dxf output.dxf")
    else:
        clean_dxf(sys.argv[1], sys.argv[2])
