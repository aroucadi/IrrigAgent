import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.sentinel import generate_canopy_report

def main():
    print("[Sentinel-2] Generating Sentinel-2 Canopy Heatmap Demo...")

    sample_parcel = {
        "type": "Polygon",
        "coordinates": [[
            [-9.5981, 30.4278],
            [-9.5950, 30.4280],
            [-9.5952, 30.4250],
            [-9.5983, 30.4251],
            [-9.5981, 30.4278]
        ]],
        "area_hectares": 8.4
    }

    report = generate_canopy_report(
        phone_number="+212600000000",
        parcel_geojson=sample_parcel,
        farm_name="Agadir Tomato Farm",
        crop_type="Tomatoes"
    )

    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sample_heatmap_output.png")

    with open(out_path, "wb") as f:
        f.write(report.image_bytes)

    print(f"[SUCCESS] Demo Heatmap PNG saved to: {out_path}")
    print(f"Field Area: {report.parcel_area_ha} ha | Crop: {report.crop_type}")
    print(f"NDVI Mean: {report.ndvi_mean} | Healthy: {report.healthy_percent}% | Moderate: {report.moderate_percent}% | Stressed: {report.stressed_percent}%")
    print(f"Recommendation:\n{report.recommendation}")

if __name__ == "__main__":
    main()
