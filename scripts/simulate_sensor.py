#!/usr/bin/env python3
"""
CLI Telemetry Simulator Utility for IrrigAgent AI
Fires mock IoT soil moisture probe readings to the IrrigAgent REST API endpoint.
"""
import argparse
import datetime
import sys
import httpx


def simulate_sensor_telemetry(
    farm_id: str,
    vwc: float,
    depth: int = 15,
    battery: int = 95,
    base_url: str = "http://localhost:8000"
) -> dict:
    url = f"{base_url.rstrip('/')}/telemetry/sensor"
    payload = {
        "farm_id": farm_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "soil_moisture_vwc": vwc,
        "depth_cm": depth,
        "battery_level": battery
    }
    print(f"📡 Transmitting soil moisture telemetry to {url}...")
    print(f"  • Farm ID : {farm_id}")
    print(f"  • VWC %   : {vwc:.1f}%")
    print(f"  • Depth   : {depth} cm")
    print(f"  • Battery : {battery}%")

    with httpx.Client(timeout=10.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        print(f"✅ Telemetry successfully recorded! Response: {data}")
        return data


def main():
    parser = argparse.ArgumentParser(description="IrrigAgent IoT Soil Moisture Telemetry Simulator")
    parser.add_argument("--farm", "-f", default="+212600000000", help="Farm recipient phone number ID")
    parser.add_argument("--vwc", "-v", type=float, default=16.5, help="Volumetric Water Content percentage (VWC %%)")
    parser.add_argument("--depth", "-d", type=int, default=15, help="Soil probe depth (cm)")
    parser.add_argument("--battery", "-b", type=int, default=95, help="Sensor battery level percentage (%%)")

    parser.add_argument("--url", "-u", default="http://localhost:8000", help="IrrigAgent API base URL")

    args = parser.parse_args()

    try:
        simulate_sensor_telemetry(
            farm_id=args.farm,
            vwc=args.vwc,
            depth=args.depth,
            battery=args.battery,
            base_url=args.url
        )
    except Exception as err:
        print(f"❌ Error transmitting telemetry: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
