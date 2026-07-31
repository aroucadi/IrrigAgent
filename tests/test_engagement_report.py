import os
import tempfile
from datetime import datetime, timezone, timedelta
import pytest

from scripts.generate_engagement_report import (
    compute_engagement_metrics,
    generate_matplotlib_chart,
    generate_html_report,
)


def test_compute_engagement_metrics_math():
    now = datetime(2026, 7, 31, 12, 0, 0, tzinfo=timezone.utc)
    mock_profiles = [
        {"phone_number": "+212600000001", "created_at": (now - timedelta(days=20)).isoformat(), "last_inbound_timestamp": (now - timedelta(days=2)).isoformat()},
        {"phone_number": "+212600000002", "created_at": (now - timedelta(days=15)).isoformat(), "last_inbound_timestamp": (now - timedelta(days=5)).isoformat()},
        {"phone_number": "+212600000003", "created_at": (now - timedelta(days=10)).isoformat(), "last_inbound_timestamp": (now - timedelta(days=1)).isoformat()},
    ]
    mock_recs = [
        {"phone_number": "+212600000001", "dispatched_at": (now - timedelta(days=2)).isoformat(), "status": "approved", "outcome_feedback": "yes", "responded_at": (now - timedelta(days=2)).isoformat()},
        {"phone_number": "+212600000002", "dispatched_at": (now - timedelta(days=5)).isoformat(), "status": "modified", "outcome_feedback": "less", "responded_at": (now - timedelta(days=5)).isoformat()},
        {"phone_number": "+212600000003", "dispatched_at": (now - timedelta(days=1)).isoformat(), "status": "skipped", "outcome_feedback": "skipped", "responded_at": (now - timedelta(days=1)).isoformat()},
        {"phone_number": "+212600000001", "dispatched_at": (now - timedelta(days=1)).isoformat(), "status": "pending", "outcome_feedback": None},
    ]
    mock_triages = [
        {"phone_number": "+212600000001", "created_at": (now - timedelta(days=3)).isoformat()},
    ]

    metrics = compute_engagement_metrics(mock_profiles, mock_recs, mock_triages, sample_threshold=5, now_dt=now)

    assert metrics.total_registered_farms == 3
    assert metrics.active_farms_7d == 3
    assert metrics.active_farms_30d == 3
    assert metrics.total_advisories_sent == 4
    assert metrics.advisories_responded == 3
    assert metrics.response_rate_pct == 75.0
    assert metrics.outcome_breakdown["followed"] == 1
    assert metrics.outcome_breakdown["less"] == 1
    assert metrics.outcome_breakdown["skipped"] == 1
    assert metrics.outcome_breakdown["no_response"] == 1


def test_directional_label_triggered_for_small_sample():
    now = datetime(2026, 7, 31, 12, 0, 0, tzinfo=timezone.utc)
    mock_profiles = [
        {"phone_number": f"+21260000000{i}", "last_inbound_timestamp": (now - timedelta(days=2)).isoformat()}
        for i in range(3)  # 3 active farms < 5 threshold
    ]
    metrics = compute_engagement_metrics(mock_profiles, [], [], sample_threshold=5, now_dt=now)

    assert metrics.active_farms_30d == 3
    assert metrics.is_small_sample is True
    assert "[Early / Directional Data (Sample Size < 5 Active Farms)]" in metrics.directional_warning_label


def test_directional_label_suppressed_for_large_sample():
    now = datetime(2026, 7, 31, 12, 0, 0, tzinfo=timezone.utc)
    mock_profiles = [
        {"phone_number": f"+21260000000{i}", "last_inbound_timestamp": (now - timedelta(days=2)).isoformat()}
        for i in range(6)  # 6 active farms >= 5 threshold
    ]
    metrics = compute_engagement_metrics(mock_profiles, [], [], sample_threshold=5, now_dt=now)

    assert metrics.active_farms_30d == 6
    assert metrics.is_small_sample is False
    assert metrics.directional_warning_label == ""


def test_empty_dataset_handling():
    metrics = compute_engagement_metrics([], [], [], sample_threshold=5)

    assert metrics.total_registered_farms == 0
    assert metrics.active_farms_7d == 0
    assert metrics.active_farms_30d == 0
    assert metrics.total_advisories_sent == 0
    assert metrics.advisories_responded == 0
    assert metrics.response_rate_pct == 0.0
    assert metrics.is_small_sample is True


def test_chart_and_html_generation():
    now = datetime(2026, 7, 31, 12, 0, 0, tzinfo=timezone.utc)
    mock_profiles = [
        {"phone_number": "+212600000001", "last_inbound_timestamp": (now - timedelta(days=1)).isoformat()}
    ]
    metrics = compute_engagement_metrics(mock_profiles, [], [], sample_threshold=5, now_dt=now)

    with tempfile.TemporaryDirectory() as tmpdir:
        png_path = os.path.join(tmpdir, "chart.png")
        html_path = os.path.join(tmpdir, "report.html")

        generate_matplotlib_chart(metrics, png_path)
        generate_html_report(metrics, "chart.png", html_path)

        assert os.path.exists(png_path)
        assert os.path.getsize(png_path) > 0

        assert os.path.exists(html_path)
        assert os.path.getsize(html_path) > 0
        with open(html_path, "r", encoding="utf-8") as f:
            html_text = f.read()
            assert "IrrigAgent AI" in html_text
            assert "Early / Directional Data" in html_text
