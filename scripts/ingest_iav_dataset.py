#!/usr/bin/env python3
"""
scripts/ingest_iav_dataset.py

IAV Hassan II Dataset Ingestion Script.

Validates and imports a JSON batch of Moroccan field leaf photos annotated
per the IAV Hassan II annotation schema, then reports ingestion results.

Usage:
    python scripts/ingest_iav_dataset.py --input data/iav_batch_001.json [--dry-run]

Schema (per record):
    - sample_id (str): Unique record ID.
    - crop_type (str): 'tomatoes' or 'citrus'.
    - disease_onssa_code (str): ONSSA registration code.
    - severity_index (int): Grade 1 to 5.
    - bounding_boxes (list): [{xmin, ymin, xmax, ymax}] normalized 0.0-1.0.
    - region (str): 'Souss-Massa' or 'Gharb'.
    - cultivar (str, optional): e.g. 'Moneymaker', 'Nadorcott'.
"""

import argparse
import json
import sys
from typing import Dict, Any

from app.cropdoctor import validate_iav_dataset_record


IAV_MILESTONE_THRESHOLD = 500  # Minimum per-disease-class count to activate Phase 2.2b


def load_batch(filepath: str) -> list[Dict[str, Any]]:
    """Load a batch JSON file containing IAV dataset records."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    records = data.get("records", data) if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise ValueError(f"Expected JSON array of records, got: {type(records)}")
    return records


def ingest_batch(records: list[Dict[str, Any]], dry_run: bool = False) -> Dict[str, Any]:
    """
    Validates each IAV dataset record and reports ingestion results.

    Args:
        records: List of raw record dictionaries.
        dry_run: If True, only validate; do not persist.

    Returns:
        Summary dict: valid_count, invalid_count, disease_class_counts, errors.
    """
    valid_count = 0
    invalid_count = 0
    errors = []
    disease_class_counts: Dict[str, int] = {}

    for i, record in enumerate(records):
        is_valid, record_errors = validate_iav_dataset_record(record)
        if is_valid:
            valid_count += 1
            disease_code = record.get("disease_onssa_code", "unknown")
            disease_class_counts[disease_code] = disease_class_counts.get(disease_code, 0) + 1
        else:
            invalid_count += 1
            errors.append({
                "record_index": i,
                "sample_id": record.get("sample_id", "<missing>"),
                "errors": record_errors,
            })

    # Milestone check
    milestone_ready = all(
        count >= IAV_MILESTONE_THRESHOLD
        for count in disease_class_counts.values()
    ) if disease_class_counts else False

    return {
        "dry_run": dry_run,
        "total_records": len(records),
        "valid_count": valid_count,
        "invalid_count": invalid_count,
        "disease_class_counts": disease_class_counts,
        "milestone_ready": milestone_ready,
        "validation_errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description="Ingest IAV Hassan II dataset batch")
    parser.add_argument("--input", required=True, help="Path to JSON batch file")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, do not persist")
    args = parser.parse_args()

    print(f"📂 Loading IAV dataset batch: {args.input}")
    try:
        records = load_batch(args.input)
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"❌ Error loading batch file: {e}")
        sys.exit(1)

    print(f"📋 Validating {len(records)} records...")
    result = ingest_batch(records, dry_run=args.dry_run)

    print(f"\n{'[DRY RUN] ' if result['dry_run'] else ''}Ingestion Summary:")
    print(f"  ✅ Valid records   : {result['valid_count']}")
    print(f"  ❌ Invalid records : {result['invalid_count']}")
    print(f"\nDisease class counts:")
    for code, count in result["disease_class_counts"].items():
        status = "✅" if count >= IAV_MILESTONE_THRESHOLD else f"⏳ ({count}/{IAV_MILESTONE_THRESHOLD})"
        print(f"  {code}: {count} {status}")

    if result["milestone_ready"]:
        print("\n🎯 MILESTONE REACHED: All disease classes have ≥500 verified samples.")
        print("   → Phase 2.2b fine-tuned model activation is authorized.")
    else:
        print(f"\n⏳ MILESTONE PENDING: Minimum {IAV_MILESTONE_THRESHOLD} verified samples per class required.")

    if result["validation_errors"]:
        print(f"\n⚠️  Validation errors ({len(result['validation_errors'])} invalid records):")
        for err in result["validation_errors"][:10]:
            print(f"  Record [{err['record_index']}] {err['sample_id']}: {'; '.join(err['errors'])}")
        if len(result["validation_errors"]) > 10:
            print(f"  ... and {len(result['validation_errors']) - 10} more.")

    if result["invalid_count"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
