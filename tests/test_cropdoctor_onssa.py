"""
Unit tests for CropDoctor ONSSA dataset loading and static fallback logic.
"""

import os
import json
import pytest
from app.cropdoctor import lookup_onssa_product, ONSSA_STATIC_CATALOG, _load_onssa_catalog


def test_lookup_static_catalog_fallback():
    """Verify static catalog lookup works when dataset file is absent."""
    res = lookup_onssa_product("tomatoes", "phytophthora_infestans")
    assert res is not None
    assert "Copper" in res or "ONSSA" in res


def test_lookup_dynamic_primary_over_static(tmp_path, monkeypatch):
    """Verify dynamic dataset lookup takes priority over static table and handles dynamic-only combos."""
    dataset_file = tmp_path / "onssa_registry.json"
    
    mock_data = {
        "_metadata": {"mode": "commit", "total_entries": 2},
        "entries": [
            {
                "id": "F99-1",
                "commercial_name": "DYNAMIC COPPER SUPER 50 WP",
                "active_substances": ["Cuivre 50%"],
                "authorized_crops": ["Tomatoes"],
                "targeted_pests": ["phytophthora_infestans"],
                "source_page": 1
            },
            {
                "id": "F99-2",
                "commercial_name": "DYNAMIC SPECIAL NEW PRODUCT",
                "active_substances": ["New Molecule 10%"],
                "authorized_crops": ["Tomatoes"],
                "targeted_pests": ["rare_pathogen_xyz"],
                "source_page": 1
            }
        ]
    }
    
    with open(dataset_file, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)

    monkeypatch.setattr("app.cropdoctor._DATASET_PATH", str(dataset_file))
    monkeypatch.setenv("ONSSA_REGISTRY_PATH", str(dataset_file))

    # (a) Combination present in dynamic dataset returns dynamic result
    res_dynamic = lookup_onssa_product("tomatoes", "rare_pathogen_xyz")
    assert res_dynamic is not None
    assert "DYNAMIC SPECIAL NEW PRODUCT" in res_dynamic

    # (b) Combination absent from both returns None (fail-closed)
    res_absent = lookup_onssa_product("tomatoes", "completely_unknown_pest")
    assert res_absent is None


def test_load_onssa_catalog_corrupted_fallback(tmp_path, monkeypatch):
    """Verify (c) graceful fallback to ONSSA_STATIC_CATALOG if dataset file is missing or corrupted."""
    corrupted_file = tmp_path / "corrupted_onssa.json"
    with open(corrupted_file, "w", encoding="utf-8") as f:
        f.write("{ INVALID JSON DATA ...")

    monkeypatch.setattr("app.cropdoctor._DATASET_PATH", str(corrupted_file))
    monkeypatch.setenv("ONSSA_REGISTRY_PATH", str(corrupted_file))

    catalog, source = _load_onssa_catalog()
    assert source == "ONSSA_STATIC_CATALOG"
    assert catalog == ONSSA_STATIC_CATALOG

    # Should fall back to static catalog without crashing
    res = lookup_onssa_product("tomatoes", "phytophthora_infestans")
    assert res is not None
    assert "Copper" in res or "ONSSA" in res
