"""
Unit tests for CropDoctor ONSSA dataset loading and static fallback logic.
"""

import os
import json
import pytest
from app.cropdoctor import lookup_onssa_product, ONSSA_STATIC_CATALOG, _load_onssa_catalog


def test_lookup_static_catalog_fallback():
    """Verify static catalog lookup works when dataset file is absent."""
    # Lookup tomato mildiou / phytophthora_infestans
    res = lookup_onssa_product("tomatoes", "phytophthora_infestans")
    assert res is not None
    assert "Copper" in res or "ONSSA" in res


def test_load_onssa_catalog_dynamic(tmp_path, monkeypatch):
    """Verify dynamic dataset loading when data/onssa_registry.json is present."""
    dataset_file = tmp_path / "onssa_registry.json"
    
    mock_data = {
        "_metadata": {"mode": "commit", "total_entries": 1},
        "entries": [
            {
                "id": "F99-1",
                "commercial_name": "DYNAMIC COPPER SUPER 50 WP",
                "active_substances": ["Cuivre 50%"],
                "authorized_crops": ["Tomate", "Tomatoes"],
                "targeted_pests": ["Mildiou", "phytophthora_infestans"],
                "dosage": "250 g/hL",
                "pre_harvest_interval_days": 15,
                "max_applications": 3,
                "toxicity_class": "Xn",
                "distributor": "DYNAMIC AGRO",
                "homologation_validity_date": "2030-12-31",
                "source_page": 1
            }
        ]
    }
    
    with open(dataset_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    # Monkeypatch dataset path in app.cropdoctor
    monkeypatch.setattr("app.cropdoctor._DATASET_PATH", str(dataset_file))

    catalog, source = _load_onssa_catalog()
    assert source == str(dataset_file)
    assert "tomate" in catalog or "tomatoes" in catalog

    res = lookup_onssa_product("tomatoes", "phytophthora_infestans")
    assert res is not None
    assert "DYNAMIC COPPER SUPER" in res


def test_load_onssa_catalog_corrupted_fallback(tmp_path, monkeypatch):
    """Verify graceful fallback to ONSSA_STATIC_CATALOG if dataset file is corrupted."""
    corrupted_file = tmp_path / "corrupted_onssa.json"
    with open(corrupted_file, "w", encoding="utf-8") as f:
        f.write("{ INVALID JSON DATA ...")

    monkeypatch.setattr("app.cropdoctor._DATASET_PATH", str(corrupted_file))

    catalog, source = _load_onssa_catalog()
    assert source == "ONSSA_STATIC_CATALOG"
    assert catalog == ONSSA_STATIC_CATALOG
