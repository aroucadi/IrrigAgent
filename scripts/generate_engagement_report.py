#!/usr/bin/env python3
"""Internal Engagement & Traction Dashboard (Sales Evidence Tool).

Standalone, read-only script querying Firestore engagement data
(farm_profiles, irrigation_recommendations, disease_triage_requests) to produce
screen-shareable sales evidence charts and HTML reports.
"""

import os
import sys
import argparse
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Reconfigure stdout to UTF-8 on Windows consoles to prevent UnicodeEncodeError for emoji characters
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass



@dataclass
class EngagementMetrics:
    total_registered_farms: int = 0
    active_farms_7d: int = 0
    active_farms_30d: int = 0
    total_advisories_sent: int = 0
    advisories_responded: int = 0
    response_rate_pct: float = 0.0
    outcome_breakdown: Dict[str, int] = field(default_factory=lambda: {
        "followed": 0,
        "less": 0,
        "more": 0,
        "skipped": 0,
        "no_response": 0,
    })
    outcome_percentages: Dict[str, float] = field(default_factory=lambda: {
        "followed": 0.0,
        "less": 0.0,
        "more": 0.0,
        "skipped": 0.0,
        "no_response": 0.0,
    })
    is_small_sample: bool = False
    sample_threshold: int = 5
    directional_warning_label: str = ""


def get_firestore_client_read_only():
    """Attempts to initialize standard synchronous Firestore client in read-only mode."""
    from app.config import GCP_PROJECT_ID
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ or "K_SERVICE" in os.environ:
        try:
            from google.cloud import firestore
            return firestore.Client(project=GCP_PROJECT_ID)
        except Exception as e:
            print(f"[WARNING] Could not initialize Firestore Client: {e}")
            return None
    return None


def fetch_firestore_data(db_client=None) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Queries existing Firestore collections read-only (farm_profiles, irrigation_recommendations, disease_triage_requests)."""
    farm_profiles = []
    recommendations = []
    triage_requests = []

    if db_client:
        try:
            # 1. farm_profiles
            docs = db_client.collection("farm_profiles").stream()
            for d in docs:
                data = d.to_dict()
                data["id"] = d.id
                farm_profiles.append(data)

            # 2. irrigation_recommendations
            docs = db_client.collection("irrigation_recommendations").stream()
            for d in docs:
                data = d.to_dict()
                data["id"] = d.id
                recommendations.append(data)

            # 3. disease_triage_requests
            docs = db_client.collection("disease_triage_requests").stream()
            for d in docs:
                data = d.to_dict()
                data["id"] = d.id
                triage_requests.append(data)
        except Exception as e:
            print(f"[ERROR] Firestore read query failed: {e}")

    return farm_profiles, recommendations, triage_requests


def _parse_iso_dt(ts_str: Optional[str]) -> Optional[datetime]:
    if not ts_str:
        return None
    try:
        # Handle 'Z' or ISO string
        cleaned = ts_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(cleaned)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def compute_engagement_metrics(
    farm_profiles: List[Dict[str, Any]],
    recommendations: List[Dict[str, Any]],
    triage_requests: List[Dict[str, Any]],
    sample_threshold: int = 5,
    now_dt: Optional[datetime] = None,
) -> EngagementMetrics:
    """Computes engagement metrics from raw Firestore record lists."""
    if now_dt is None:
        now_dt = datetime.now(timezone.utc)
    elif now_dt.tzinfo is None:
        now_dt = now_dt.replace(tzinfo=timezone.utc)

    metrics = EngagementMetrics(sample_threshold=sample_threshold)
    metrics.total_registered_farms = len(farm_profiles)

    dt_7d_ago = now_dt - timedelta(days=7)
    dt_30d_ago = now_dt - timedelta(days=30)

    active_farms_7d_set = set()
    active_farms_30d_set = set()

    # 1. Farm profile last_inbound_timestamp
    for p in farm_profiles:
        phone = p.get("phone_number") or p.get("id")
        ts = _parse_iso_dt(p.get("last_inbound_timestamp") or p.get("updated_at") or p.get("created_at"))
        if phone and ts:
            if ts >= dt_7d_ago:
                active_farms_7d_set.add(phone)
            if ts >= dt_30d_ago:
                active_farms_30d_set.add(phone)

    # 2. Recommendations activity
    metrics.total_advisories_sent = len(recommendations)

    outcome_counts = {
        "followed": 0,
        "less": 0,
        "more": 0,
        "skipped": 0,
        "no_response": 0,
    }

    for r in recommendations:
        phone = r.get("phone_number")
        disp_ts = _parse_iso_dt(r.get("dispatched_at"))
        resp_ts = _parse_iso_dt(r.get("responded_at") or r.get("outcome_updated_at"))
        status = r.get("status", "pending")
        feedback = r.get("outcome_feedback")

        # Track active farm phone by timestamps
        activity_ts = resp_ts or disp_ts
        if phone and activity_ts:
            if activity_ts >= dt_7d_ago:
                active_farms_7d_set.add(phone)
            if activity_ts >= dt_30d_ago:
                active_farms_30d_set.add(phone)

        # Advisory response rate check
        if status != "pending" or resp_ts is not None or feedback is not None:
            metrics.advisories_responded += 1

        # Outcome feedback mapping
        # FB_YES/yes -> followed
        # FB_LESS/less -> less
        # FB_MORE/more -> more
        # FB_SKIPPED/skipped -> skipped
        if feedback in ("yes", "FB_YES", "followed", "approved"):
            outcome_counts["followed"] += 1
        elif feedback in ("less", "FB_LESS"):
            outcome_counts["less"] += 1
        elif feedback in ("more", "FB_MORE"):
            outcome_counts["more"] += 1
        elif feedback in ("skipped", "FB_SKIPPED") or status == "skipped":
            outcome_counts["skipped"] += 1
        else:
            outcome_counts["no_response"] += 1

    # 3. Disease triage activity
    for t in triage_requests:
        phone = t.get("phone_number")
        t_ts = _parse_iso_dt(t.get("created_at"))
        if phone and t_ts:
            if t_ts >= dt_7d_ago:
                active_farms_7d_set.add(phone)
            if t_ts >= dt_30d_ago:
                active_farms_30d_set.add(phone)

    metrics.active_farms_7d = len(active_farms_7d_set)
    metrics.active_farms_30d = len(active_farms_30d_set)

    if metrics.total_advisories_sent > 0:
        metrics.response_rate_pct = round((metrics.advisories_responded / metrics.total_advisories_sent) * 100.0, 1)
    else:
        metrics.response_rate_pct = 0.0

    metrics.outcome_breakdown = outcome_counts

    total_outcomes = sum(outcome_counts.values())
    if total_outcomes > 0:
        metrics.outcome_percentages = {
            k: round((v / total_outcomes) * 100.0, 1)
            for k, v in outcome_counts.items()
        }
    else:
        metrics.outcome_percentages = {k: 0.0 for k in outcome_counts}

    # Directional Data Governance Check
    if metrics.active_farms_30d < sample_threshold:
        metrics.is_small_sample = True
        metrics.directional_warning_label = f"⚠️ [Early / Directional Data (Sample Size < {sample_threshold} Active Farms)]"
    else:
        metrics.is_small_sample = False
        metrics.directional_warning_label = ""

    return metrics


def generate_matplotlib_chart(metrics: EngagementMetrics, output_png_path: str) -> None:
    """Generates composite sales evidence chart figure PNG using matplotlib."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#0f172a')  # Dark slate background

    title_text = "IrrigAgent Pilot Engagement & Traction Summary"
    if metrics.is_small_sample:
        title_text += f"\n{metrics.directional_warning_label}"

    fig.suptitle(title_text, color='white', fontsize=14, fontweight='bold', y=0.98)

    # Subplot 1: Active Farm Counts & Response Rate Bar Chart
    ax1 = axes[0]
    ax1.set_facecolor('#1e293b')
    categories = ['Registered\nFarms', '30d Active\nFarms', '7d Active\nFarms']
    values = [metrics.total_registered_farms, metrics.active_farms_30d, metrics.active_farms_7d]
    colors = ['#3b82f6', '#10b981', '#f59e0b']

    bars = ax1.bar(categories, values, color=colors, width=0.5)
    ax1.set_title(f"Farm Participation (Advisory Response: {metrics.response_rate_pct}%)", color='white', fontsize=11)
    ax1.tick_params(colors='white')
    ax1.spines['bottom'].set_color('#475569')
    ax1.spines['left'].set_color('#475569')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    for bar in bars:
        height = bar.get_height()
        ax1.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom', color='white', fontweight='bold')

    # Subplot 2: Outcome Feedback Response Breakdown
    ax2 = axes[1]
    ax2.set_facecolor('#1e293b')
    fb_keys = ['Followed\n(100%)', 'Less\nWater', 'More\nWater', 'Skipped', 'No\nResponse']
    fb_vals = [
        metrics.outcome_breakdown['followed'],
        metrics.outcome_breakdown['less'],
        metrics.outcome_breakdown['more'],
        metrics.outcome_breakdown['skipped'],
        metrics.outcome_breakdown['no_response'],
    ]
    fb_colors = ['#22c55e', '#06b6d4', '#ec4899', '#ef4444', '#64748b']

    bars2 = ax2.bar(fb_keys, fb_vals, color=fb_colors, width=0.5)
    ax2.set_title("Outcome-Feedback Distribution", color='white', fontsize=11)
    ax2.tick_params(colors='white')
    ax2.spines['bottom'].set_color('#475569')
    ax2.spines['left'].set_color('#475569')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)

    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{height}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', color='white', fontweight='bold')

    plt.tight_layout(rect=[0, 0, 1, 0.92])

    os.makedirs(os.path.dirname(os.path.abspath(output_png_path)), exist_ok=True)
    plt.savefig(output_png_path, dpi=200, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)


def generate_html_report(metrics: EngagementMetrics, chart_rel_path: str, output_html_path: str) -> None:
    """Renders a standalone static HTML summary page for discovery call screen-sharing."""
    warning_banner = ""
    if metrics.is_small_sample:
        warning_banner = f"""
        <div style="background-color: #7f1d1d; border: 1px solid #ef4444; color: #fca5a5; padding: 12px 16px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 14px;">
            {metrics.directional_warning_label}
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IrrigAgent AI - Engagement & Traction Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 30px;
        }}
        .container {{
            max-width: 1100px;
            margin: 0 auto;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
            padding-bottom: 16px;
            margin-bottom: 24px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            color: #38bdf8;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}
        .card {{
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .card-value {{
            font-size: 32px;
            font-weight: bold;
            color: #38bdf8;
            margin-top: 8px;
        }}
        .card-label {{
            font-size: 13px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .chart-box {{
            background-color: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}
        .chart-box img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: #64748b;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🌾 IrrigAgent AI — Executive Pilot Traction Summary</h1>
                <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">Sales Evidence & Field Interaction Report</div>
            </div>
            <div style="font-size: 12px; color: #64748b;">Generated: {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}</div>
        </div>

        {warning_banner}

        <div class="grid">
            <div class="card">
                <div class="card-label">Registered Farms</div>
                <div class="card-value">{metrics.total_registered_farms}</div>
            </div>
            <div class="card">
                <div class="card-label">30-Day Active Farms</div>
                <div class="card-value" style="color: #10b981;">{metrics.active_farms_30d}</div>
            </div>
            <div class="card">
                <div class="card-label">Advisory Response Rate</div>
                <div class="card-value" style="color: #f59e0b;">{metrics.response_rate_pct}%</div>
            </div>
            <div class="card">
                <div class="card-label">Advisories Sent</div>
                <div class="card-value" style="color: #a855f7;">{metrics.total_advisories_sent}</div>
            </div>
        </div>

        <div class="chart-box">
            <img src="{chart_rel_path}" alt="Engagement & Traction Visual Charts">
        </div>

        <div class="footer">
            Internal Founder Tool — Read-Only Field Data Summary — IrrigAgent AI v1.0
        </div>
    </div>
</body>
</html>
"""
    os.makedirs(os.path.dirname(os.path.abspath(output_html_path)), exist_ok=True)
    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)


def main():
    parser = argparse.ArgumentParser(description="Generate Internal Engagement & Traction Report")
    parser.add_argument("--output-dir", default="output", help="Directory path to save report artifacts")
    parser.add_argument("--sample-threshold", type=int, default=5, help="Minimum active farms threshold for directional labeling")
    parser.add_argument("--mock", action="store_true", help="Generate report using synthetic mock pilot data")
    args = parser.parse_args()

    if args.mock:
        print("[INFO] Running report generator using synthetic mock pilot data...")
        now = datetime.now(timezone.utc)
        mock_profiles = [
            {"phone_number": "+212600000001", "created_at": (now - timedelta(days=20)).isoformat(), "last_inbound_timestamp": (now - timedelta(days=2)).isoformat()},
            {"phone_number": "+212600000002", "created_at": (now - timedelta(days=15)).isoformat(), "last_inbound_timestamp": (now - timedelta(days=5)).isoformat()},
            {"phone_number": "+212600000003", "created_at": (now - timedelta(days=10)).isoformat(), "last_inbound_timestamp": (now - timedelta(days=1)).isoformat()},
        ]
        mock_recs = [
            {"phone_number": "+212600000001", "dispatched_at": (now - timedelta(days=2)).isoformat(), "status": "approved", "outcome_feedback": "yes"},
            {"phone_number": "+212600000002", "dispatched_at": (now - timedelta(days=5)).isoformat(), "status": "modified", "outcome_feedback": "less"},
            {"phone_number": "+212600000003", "dispatched_at": (now - timedelta(days=1)).isoformat(), "status": "skipped", "outcome_feedback": "skipped"},
            {"phone_number": "+212600000001", "dispatched_at": (now - timedelta(days=1)).isoformat(), "status": "pending", "outcome_feedback": None},
        ]
        mock_triages = [
            {"phone_number": "+212600000001", "created_at": (now - timedelta(days=3)).isoformat()},
        ]
        farm_profiles, recommendations, triage_requests = mock_profiles, mock_recs, mock_triages
    else:
        print("[INFO] Fetching read-only data from Firestore...")
        db_client = get_firestore_client_read_only()
        if not db_client:
            print("[WARNING] Firestore client unavailable. Use --mock or set GOOGLE_APPLICATION_CREDENTIALS.")
            farm_profiles, recommendations, triage_requests = [], [], []
        else:
            farm_profiles, recommendations, triage_requests = fetch_firestore_data(db_client)

    metrics = compute_engagement_metrics(farm_profiles, recommendations, triage_requests, sample_threshold=args.sample_threshold)

    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    png_filename = f"engagement_report_{date_str}.png"
    html_filename = f"engagement_report_{date_str}.html"

    png_path = os.path.join(args.output_dir, png_filename)
    html_path = os.path.join(args.output_dir, html_filename)

    print(f"[INFO] Rendering chart PNG figure: {png_path}")
    generate_matplotlib_chart(metrics, png_path)

    print(f"[INFO] Rendering static HTML report: {html_path}")
    generate_html_report(metrics, png_filename, html_path)

    print("\n--- Summary Metrics ---")
    print(f"Registered Farms: {metrics.total_registered_farms}")
    print(f"7d Active Farms: {metrics.active_farms_7d}")
    print(f"30d Active Farms: {metrics.active_farms_30d}")
    print(f"Advisory Response Rate: {metrics.response_rate_pct}% ({metrics.advisories_responded}/{metrics.total_advisories_sent})")
    print(f"Outcome Feedback Breakdown: {metrics.outcome_breakdown}")
    if metrics.is_small_sample:
        print(f"Governance Label: {metrics.directional_warning_label}")
    print("\nReport generation completed successfully!")


if __name__ == "__main__":
    main()
