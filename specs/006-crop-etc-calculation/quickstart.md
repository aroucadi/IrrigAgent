# Quickstart & Verification Guide: Crop-Specific ETc Calculation

**Feature**: `006-crop-etc-calculation`
**Date**: 2026-07-29

## Prerequisites & Setup

Ensure unit testing environment is active:
```bash
pytest --version
```

## Runnable Verification Scenarios

### 1. Execute FAO-56 & Decision Unit Tests

Run the dedicated test suite validating FAO-56 lookup table values, interpolation boundaries, and fallback handling:

```bash
pytest tests/unit/test_fao56.py tests/unit/test_decision.py -v
```

### 2. Full Test Suite Gate Check

Confirm zero regressions across the entire application test suite (Constitution Principle VIII):

```bash
pytest tests/ -v
```

---

## Example Test Case Scenarios

| Test Case | Inputs | Expected $K_c$ | Expected $\text{ET}_c$ | Stage |
|---|---|---|---|---|
| Tomato Initial | `crop="tomatoes"`, `ET0=5.0`, `days=15` | `0.60` | `3.00 mm/day` | `initial` |
| Tomato Mid-Season | `crop="tomatoes"`, `ET0=5.0`, `days=80` | `1.15` | `5.75 mm/day` | `mid_season` |
| Tomato Dev Interpolated | `crop="tomatoes"`, `ET0=5.0`, `days=50` | `0.88` | `4.38 mm/day` | `development` |
| Missing Planting Date | `crop="tomatoes"`, `ET0=5.0`, `planting_date=None` | `1.00` | `5.00 mm/day` | `unknown` |
| Perennial Citrus | `crop="citrus"`, `ET0=4.0` | `0.70` | `2.80 mm/day` | `perennial` |
