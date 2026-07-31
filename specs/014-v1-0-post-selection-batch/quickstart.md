# Quickstart Validation Guide: v1.0 — ONSSA Live Registry Activation, Frost Alerts, Parcel UX Hardening, and Post-Selection IaC (gated)

**Feature Branch**: `014-v1-0-post-selection-batch`
**Date**: 2026-07-31

## Prerequisites & Setup

Ensure the virtual environment is activated and dependencies are up to date:

```bash
# Verify Python & pytest environment
pytest --version
```

## Scenario 1: Execute Live ONSSA Scrape Commit Run

Run the live sync script once to populate `data/onssa_registry.json`:

```bash
python scripts/sync_onssa_registry.py --commit
```

**Verification**:
- Verify `data/onssa_registry.json` is created and contains non-empty `metadata` (`last_synced`, `total_records`) and `catalog` entries.

## Scenario 2: Test CropDoctor Primary Source Fallback Chain

Run automated unit/integration tests for ONSSA dynamic lookup, static fallback, and malformed dataset recovery:

```bash
pytest tests/unit/test_cropdoctor.py tests/test_cropdoctor_onssa.py -v
```

**Verification**:
- Product lookup queries for items present in `data/onssa_registry.json` return dynamic entries.
- Queries absent from dynamic registry fall back to static catalog.
- Absent from both returns `None` with disclaimers intact.
- Missing/malformed JSON dataset falls back gracefully without crashing.

## Scenario 3: Test Extreme Weather Advisory Alert Warnings

Run daily advisory weather threshold decision tests:

```bash
pytest tests/unit/test_decision.py tests/unit/test_weather.py -v
```

**Verification**:
- Forecasts with max temp > 40°C append heat warning section with misting guidance.
- Forecasts with min temp < 2°C append frost warning section with covering guidance.
- Forecasts between 2°C and 40°C produce standard advisories with no warning section appended.

## Scenario 4: Test Hardened Parcel Boundary Validation & Reset

Run parcel boundary collection unit tests:

```bash
pytest tests/unit/test_parcel_pin_collection.py -v
```

**Verification**:
- Submitting <3 pins triggers `INSUFFICIENT_PINS` response.
- Submitting pins <5m apart triggers `PIN_TOO_CLOSE` response.
- Submitting self-intersecting polygon triggers `SELF_INTERSECTING` response.
- Sending `"restart boundary"` / `"réinitialiser"` / `"recommencer"` resets pin state.

## Scenario 5: Full Test Suite Execution

Run the complete test suite to ensure zero regressions:

```bash
pytest tests/
```

**Expected Outcome**: 100% test pass rate across all unit and integration tests.
