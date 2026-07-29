"""
Unit tests for ONSSA phytosanitary registry sync tool.
"""

import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from scripts.sync_onssa_registry import (
    PhytosanitaryProductEntry,
    SyncResult,
    check_robots_allowed,
    parse_onssa_table_rows,
    save_checkpoint,
    load_checkpoint,
    clear_checkpoint,
    run_sync,
)

SAMPLE_ONSSA_HTML = """
<!DOCTYPE html>
<html>
<head><title>Index Phytosanitaire</title></head>
<body>
    <form id="form1">
        <input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="VS_TOKEN_123" />
        <input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="EV_TOKEN_456" />
        <input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="GEN_TOKEN_789" />

        <table id="GridView1">
            <tr>
                <th>Nom Commercial</th>
                <th>Substance Active</th>
                <th>Culture</th>
                <th>Ravageur</th>
                <th>Dose</th>
                <th>DAR (jours)</th>
                <th>Nbr App</th>
                <th>Toxicite</th>
                <th>Societe</th>
                <th>Validity</th>
                <th>N Homologation</th>
            </tr>
            <tr>
                <td>COPPER SUPER 50 WP</td>
                <td>Cuivre 50%</td>
                <td>Tomate</td>
                <td>Mildiou</td>
                <td>250 g/hL</td>
                <td>15 jours</td>
                <td>3</td>
                <td>Nocif (Xn)</td>
                <td>AGRO-CHEMICALS</td>
                <td>2028-12-31</td>
                <td>F02-3-019</td>
            </tr>
            <tr>
                <td>INSECTICIDE X 20 EC</td>
                <td>Deltamethrine 20g/L</td>
                <td>Agrumes</td>
                <td>Pucerons</td>
                <td>50 cc/hL</td>
                <td>7</td>
                <td>2</td>
                <td>Toxique (T)</td>
                <td>AGRI-SUPPLY</td>
                <td>2027-06-30</td>
                <td>F05-1-042</td>
            </tr>
        </table>
    </form>
</body>
</html>
"""


def test_parse_onssa_table_rows():
    entries, failed, hidden_fields = parse_onssa_table_rows(SAMPLE_ONSSA_HTML, page_num=1)
    
    assert hidden_fields.get("__VIEWSTATE") == "VS_TOKEN_123"
    assert hidden_fields.get("__EVENTVALIDATION") == "EV_TOKEN_456"
    assert hidden_fields.get("__VIEWSTATEGENERATOR") == "GEN_TOKEN_789"

    assert len(entries) == 2
    assert len(failed) == 0

    e1 = entries[0]
    assert e1.commercial_name == "COPPER SUPER 50 WP"
    assert e1.active_substances == ["Cuivre 50%"]
    assert e1.authorized_crops == ["Tomate"]
    assert e1.targeted_pests == ["Mildiou"]
    assert e1.pre_harvest_interval_days == 15
    assert e1.max_applications == 3
    assert e1.distributor == "AGRO-CHEMICALS"
    assert e1.id == "F02-3-019"

    e2 = entries[1]
    assert e2.commercial_name == "INSECTICIDE X 20 EC"
    assert e2.pre_harvest_interval_days == 7


def test_checkpoint_lifecycle(tmp_path):
    checkpoint_file = str(tmp_path / "test_checkpoint.json")
    
    entries = [
        PhytosanitaryProductEntry(
            id="T1",
            commercial_name="TEST PRODUCT",
            active_substances=["Active 1"],
            authorized_crops=["Tomate"],
            targeted_pests=["Mildiou"],
            dosage="100g/hL",
            pre_harvest_interval_days=10,
            max_applications=2,
            toxicity_class="Xn",
            distributor="TEST DIST",
            homologation_validity_date="2030-01-01",
            source_page=1
        )
    ]

    save_checkpoint(checkpoint_file, page_idx=1, entries=entries, failed_rows=[])
    assert os.path.exists(checkpoint_file)

    loaded = load_checkpoint(checkpoint_file)
    assert loaded is not None
    assert loaded["last_completed_page"] == 1
    assert loaded["accumulated_entries_count"] == 1
    assert loaded["entries"][0]["commercial_name"] == "TEST PRODUCT"

    clear_checkpoint(checkpoint_file)
    assert not os.path.exists(checkpoint_file)


@patch("scripts.sync_onssa_registry.check_robots_allowed")
@patch("scripts.sync_onssa_registry.request_with_retry")
def test_run_sync_dry_run(mock_request, mock_robots, tmp_path):
    mock_robots.return_value = True
    
    mock_resp = MagicMock()
    mock_resp.text = SAMPLE_ONSSA_HTML
    mock_resp.status_code = 200
    mock_request.return_value = mock_resp

    output_file = str(tmp_path / "data" / "onssa_registry.json")

    # Run dry-run mode
    res = run_sync(commit=False, limit=2, delay_seconds=0.0, output_file=output_file)

    assert res.success is True
    assert res.mode == "dry-run"
    assert res.total_entries_parsed == 2
    assert res.output_file is None
    # Crucial: zero file written in dry-run mode
    assert not os.path.exists(output_file)


@patch("scripts.sync_onssa_registry.check_robots_allowed")
@patch("scripts.sync_onssa_registry.request_with_retry")
def test_run_sync_commit(mock_request, mock_robots, tmp_path):
    mock_robots.return_value = True
    
    mock_resp = MagicMock()
    mock_resp.text = SAMPLE_ONSSA_HTML
    mock_resp.status_code = 200
    mock_request.return_value = mock_resp

    output_file = str(tmp_path / "data" / "onssa_registry.json")

    # Run commit mode
    res = run_sync(commit=True, limit=2, delay_seconds=0.0, output_file=output_file, resume=False)

    assert res.success is True
    assert res.mode == "commit"
    assert res.total_entries_parsed == 2
    assert res.output_file == output_file
    assert os.path.exists(output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "_metadata" in data
    assert data["_metadata"]["mode"] == "commit"
    assert data["_metadata"]["total_entries"] == 2
    assert len(data["entries"]) == 2
    assert data["entries"][0]["commercial_name"] == "COPPER SUPER 50 WP"


@patch("scripts.sync_onssa_registry.check_robots_allowed")
def test_run_sync_robots_disallowed(mock_robots, tmp_path):
    mock_robots.return_value = False
    output_file = str(tmp_path / "onssa_registry.json")

    res = run_sync(commit=False, limit=2, output_file=output_file)

    assert res.success is False
    assert "disallowed by site robots.txt" in res.error_message
    assert not os.path.exists(output_file)
