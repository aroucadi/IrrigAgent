import math
from typing import List, Dict, Tuple, Any
from shapely.geometry import Polygon


def calculate_shoelace_geodesic_area_ha(coordinates: List[Tuple[float, float]]) -> float:
    """Calculate precise surface area in hectares for WGS84 (lon, lat) polygon using Shoelace formula on geodesic projection."""
    if not coordinates or len(coordinates) < 3:
        return 0.0

    pts = list(coordinates)
    if pts[0] == pts[-1] and len(pts) > 3:
        pts = pts[:-1]

    if len(pts) < 3:
        return 0.0

    # Mean latitude in radians for projection scaling
    mean_lat_rad = math.radians(sum(p[1] for p in pts) / len(pts))
    r_earth = 6378137.0  # WGS84 equatorial radius in meters

    lon0, lat0 = pts[0][0], pts[0][1]
    projected_pts = []
    for lon, lat in pts:
        x = math.radians(lon - lon0) * r_earth * math.cos(mean_lat_rad)
        y = math.radians(lat - lat0) * r_earth
        projected_pts.append((x, y))

    n = len(projected_pts)
    area_m2 = 0.0
    for i in range(n):
        j = (i + 1) % n
        area_m2 += projected_pts[i][0] * projected_pts[j][1]
        area_m2 -= projected_pts[j][0] * projected_pts[i][1]

    area_m2 = abs(area_m2) / 2.0
    area_ha = area_m2 / 10000.0
    return round(area_ha, 2)


def validate_parcel_polygon(pins: List[Dict[str, float]]) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate field corner pins, check polygon simplicity, and compute Shoelace area.
    
    Returns (is_valid, error_message, geojson_dict).
    """
    if len(pins) < 3:
        return False, "At least 3 corner pins are required to form a field parcel boundary.", {}

    raw_coords = [(float(p["lon"]), float(p["lat"])) for p in pins]

    # Close linear ring if not closed
    closed_coords = list(raw_coords)
    if closed_coords[0] != closed_coords[-1]:
        closed_coords.append(closed_coords[0])

    try:
        poly = Polygon(raw_coords)
    except Exception as e:
        return False, f"Invalid geometric coordinates provided: {str(e)}", {}

    if not poly.is_valid or not poly.is_simple:
        return False, "Field boundary edges cross each other (self-intersecting polygon). Please send corner pins sequentially around your field perimeter.", {}

    area_ha = calculate_shoelace_geodesic_area_ha(raw_coords)

    MIN_AREA_HA = 0.1
    MAX_AREA_HA = 200.0

    if area_ha < MIN_AREA_HA or area_ha > MAX_AREA_HA:
        return False, f"Calculated field area ({area_ha} ha) is out of bounds. Parcel size must be between {MIN_AREA_HA} ha and {MAX_AREA_HA} ha.", {}

    geojson_parcel = {
        "type": "Polygon",
        "coordinates": [[[c[0], c[1]] for c in closed_coords]],
        "area_hectares": area_ha,
        "perimeter_m": round(poly.length * 111000, 1),
    }

    return True, "", geojson_parcel
