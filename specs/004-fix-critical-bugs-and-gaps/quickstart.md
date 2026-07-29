# Quickstart Validation Guide: 004-fix-critical-bugs-and-gaps

## Prerequisites
- Active Python 3.13 virtual environment (`.venv`).
- All dependencies installed (`pip install -r requirements.txt`).

## Validation Scenarios

### Scenario 1: Verify CropDoctor Real JPEG Processing
```bash
.venv\Scripts\python.exe -m pytest tests/unit/test_cropdoctor.py -k test_cropdoctor_triage
```
**Expected Outcome**: Real JPEG photo bytes do not trigger hardcoded mock diagnosis. Mock responses are strictly triggered by `fake_high_confidence` or `force_confidence`.

---

### Scenario 2: Verify Arabizi Clock-Time Exclusion
```bash
.venv\Scripts\python.exe -m pytest tests/unit/test_firestore_client.py -k test_detect_arabizi
```
**Expected Outcome**: Clock times such as `07h00` or `19h00` do not flip language detection to Darija.

---

### Scenario 3: Verify FarmProfile Schema Validation
```bash
.venv\Scripts\python.exe -m pytest tests/unit/test_schemas.py
```
**Expected Outcome**: Profile updates validate against `FarmProfile` (`phone_number`, `location`, `crop_type`, `acreage_hectares`, `preferred_language`) and reject invalid inputs.

---

### Scenario 4: Full Automated Test Suite Verification
```bash
.venv\Scripts\python.exe -m pytest tests/
```
**Expected Outcome**: 100% pass rate across all unit and integration tests with zero errors and zero warnings.
