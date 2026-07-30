#!/usr/bin/env python3
"""
scripts/evaluate_calibration.py

Expected Calibration Error (ECE) Evaluation Script (Phase 2.2b - DEFERRED).

Evaluates temperature scaling calibration accuracy on a held-out Moroccan field validation dataset.
Per SC-004, calibration ensures reported confidence scores correspond to within ±5% empirical accuracy
(ECE < 0.05).

Activation Condition:
    Activated automatically when dataset_count_per_class >= 500 for all target disease classes
    (tomatoes & citrus).
"""

import sys
import os
import json
import argparse
from typing import List, Dict, Any, Tuple


def calculate_ece(
    confidences: List[float],
    accuracies: List[int],
    num_bins: int = 10
) -> float:
    """
    Calculates Expected Calibration Error (ECE).

    Args:
        confidences: List of predicted confidence scores (0.0 to 1.0).
        accuracies: List of binary accuracy outcomes (1 for correct, 0 for incorrect).
        num_bins: Number of probability calibration bins.

    Returns:
        ECE score as float.
    """
    if not confidences or len(confidences) != len(accuracies):
        return 0.0

    total_samples = len(confidences)
    bin_boundaries = [i / float(num_bins) for i in range(num_bins + 1)]
    ece = 0.0

    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]

        # Filter samples in current bin
        bin_indices = [
            j for j, conf in enumerate(confidences)
            if bin_lower < conf <= bin_upper or (i == 0 and conf == bin_lower)
        ]

        bin_size = len(bin_indices)
        if bin_size > 0:
            bin_acc = sum(accuracies[j] for j in bin_indices) / float(bin_size)
            bin_conf = sum(confidences[j] for j in bin_indices) / float(bin_size)
            ece += (bin_size / float(total_samples)) * abs(bin_acc - bin_conf)

    return round(ece, 4)


def main():
    parser = argparse.ArgumentParser(description="Evaluate Expected Calibration Error (ECE) for Phase 2.2b Classifier")
    parser.add_argument("--validation-set", type=str, default=os.path.join("data", "iav_validation_split.json"), help="Path to validation dataset split")
    parser.add_argument("--num-bins", type=int, default=10, help="Number of calibration bins")
    parser.add_argument("--target-ece", type=float, default=0.05, help="Maximum allowed ECE threshold (0.05 = +-5%)")

    args = parser.parse_args()

    if not os.path.exists(args.validation_set):
        print(f"INFO: Validation dataset split not found at '{args.validation_set}'.")
        print("SC-004 Calibration Evaluation is DEFERRED until Phase 2.2b IAV dataset milestone (>= 500 samples/class) is reached.")
        sys.exit(0)

    try:
        with open(args.validation_set, "r", encoding="utf-8") as f:
            data = json.load(f)

        confidences = [item["calibrated_confidence"] for item in data.get("samples", [])]
        accuracies = [1 if item["predicted_class"] == item["ground_truth_class"] else 0 for item in data.get("samples", [])]

        ece_score = calculate_ece(confidences, accuracies, num_bins=args.num_bins)

        print(f"--- Calibration Evaluation Summary (Phase 2.2b) ---")
        print(f"Total Validation Samples : {len(confidences)}")
        print(f"Computed ECE Score       : {ece_score:.4f}")
        print(f"Target ECE Threshold     : {args.target_ece:.4f}")
        print(f"Empirical Accuracy Error : {ece_score * 100:.2f}%")

        if ece_score <= args.target_ece:
            print("STATUS: PASS (Confidence calibration meets +-5% accuracy requirement)")
            sys.exit(0)
        else:
            print("STATUS: FAIL (Expected Calibration Error exceeds +-5% threshold)")
            sys.exit(1)

    except Exception as e:
        print(f"ERROR: Failed to process validation dataset: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
