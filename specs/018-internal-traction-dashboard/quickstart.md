# Quickstart Guide: Internal Engagement & Traction Dashboard

**Feature**: Internal Engagement & Traction Dashboard (Sales Evidence Tool)  
**Branch**: `018-internal-traction-dashboard`  

## 1. Overview
The Internal Engagement & Traction Dashboard is a standalone local script designed for the founder to generate screen-shareable sales evidence (active farm counts, response rates, outcome feedback breakdown) before packing-house discovery calls.

## 2. Prerequisites
- Python 3.11+
- Virtual environment activated with project dependencies (`matplotlib`, `google-cloud-firestore`)
- Optional: GCP application credentials configured for live Firestore querying (if running against real database)

## 3. Running the Report Generator
To generate a static engagement report and chart figure locally:

```bash
# Generate report using default output directory (output/)
python scripts/generate_engagement_report.py

# Specify custom output directory
python scripts/generate_engagement_report.py --output-dir sales_collateral/
```

### Expected Output Files:
1. `output/engagement_report_<YYYYMMDD>.png`: High-resolution matplotlib chart figure.
2. `output/engagement_report_<YYYYMMDD>.html`: Static HTML dashboard page for screen sharing.

## 4. Running Automated Tests
To run unit tests verifying report calculation math and small-sample warning triggers:

```bash
pytest tests/test_engagement_report.py -v
```
