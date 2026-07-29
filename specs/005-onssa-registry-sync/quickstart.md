# Phase 1 Quickstart & Validation Guide: ONSSA Registry Sync Tool

**Branch**: `005-onssa-registry-sync` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/005-onssa-registry-sync/spec.md)

## Validation Workflows

### Scenario 1: Dry-Run Extraction Verification (Default Mode)

Validate that a bare invocation runs safely in dry-run mode, fetches up to 20 sample entries, logs a summary, and writes zero data to `data/onssa_registry.json`.

```bash
# 1. Ensure output file does not exist initially
rm -f data/onssa_registry.json

# 2. Run bare CLI invocation
python scripts/sync_onssa_registry.py

# Expected Outcome:
# - Performs live fetch of up to 20 entries
# - Displays parsed product rows in stdout
# - Logs execution summary (Parsed: 20, Failed: 0, Elapsed time)
# - File data/onssa_registry.json DOES NOT exist
```

---

### Scenario 2: Sample Dry-Run with Custom Limit

```bash
python scripts/sync_onssa_registry.py --dry-run --limit 5
```

---

### Scenario 3: Explicit Full Commit Run & Persistence

```bash
# Execute committed extraction
python scripts/sync_onssa_registry.py --commit --delay 2.5

# Expected Outcome:
# - Checks robots.txt compliance
# - Extracts pages sequentially with 2.5s delay
# - Saves checkpoint progress to data/onssa_registry.checkpoint.json
# - Produces final data/onssa_registry.json with _metadata and entries array
```

---

### Scenario 4: CropDoctor Runtime Integration & Fallback Test

```bash
# Test 1: Run pytest when data/onssa_registry.json exists
pytest tests/test_cropdoctor_onssa.py

# Test 2: Temporarily hide data/onssa_registry.json and verify static fallback
mv data/onssa_registry.json data/onssa_registry.json.bak
pytest tests/test_cropdoctor_onssa.py
mv data/onssa_registry.json.bak data/onssa_registry.json
```
