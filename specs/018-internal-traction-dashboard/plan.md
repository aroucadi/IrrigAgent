# Implementation Plan - Internal Engagement & Traction Dashboard

**Feature Name**: Internal Engagement & Traction Dashboard (Sales Evidence Tool)  
**Feature Branch**: `018-internal-traction-dashboard`  
**Created**: 2026-07-31  
**Status**: Draft  

---

## Technical Context

- **Language/Version**: Python 3.11+, matching project convention.
- **Primary Dependencies**: `google-cloud-firestore` (read-only queries), `matplotlib` (chart generation), standard library (`argparse`, `dataclasses`, `html`, `json`).
- **Target Architecture**: Isolated standalone CLI script (`scripts/generate_engagement_report.py`) executed locally by the founder prior to discovery calls.
- **Storage**: Read-only access against existing Firestore collections (`farm_profiles`, `irrigation_recommendations`, `disease_triage_requests`). Zero writes, zero schema modifications.
- **Testing**: `pytest` tests in `tests/test_engagement_report.py` with 100% mocked Firestore data to verify metric calculations and directional data warning tags.
- **Non-Goals & Isolation**: Zero changes to `app/` application codebase. No new web servers, no live dashboards, no public deployment. No speculative water savings or yield metrics.

---

## Constitution Check

- **I. Human-in-the-Loop Only**: Verified. Tool is founder-facing and read-only.
- **V. Strict Scope Boundary**: Verified. No hardware, payments, or farmer-facing changes.
- **VIII. Quality, Security & Automated Verification Gates**:
  - **Zero-Broken-Tests**: All tests under `tests/` must pass cleanly.
  - **No-Facade Rule / No-Ambiguous-Mock-Fallback**: Fully respected. Report explicitly flags small sample sizes (< 5 active farms) as "early/directional data" and never interpolates or fabricates synthetic data for missing periods.
- **Credibility & Overclaiming Safeguard**: Report presents raw engagement numbers and self-reported override ratios only. No unverified water savings or yield claims.

---

## Proposed Changes

### Component 1: CLI Report Generation Script & Data Aggregator

#### [NEW] [scripts/generate_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/scripts/generate_engagement_report.py)
- Standalone executable Python script.
- Contains read-only Firestore data fetch logic (or takes injected dict/mock data for testing).
- Computes registered farms count, 7d/30d active farms, daily advisory response rate, and outcome-feedback percentage breakdown.
- Automatically evaluates sample size per bucket (threshold < 5 active farms) and injects `[Early / Directional Data (Sample Size < 5)]` label on output charts and HTML cards.
- Renders and saves PNG chart (`output/engagement_report_<YYYYMMDD>.png`) and static HTML summary (`output/engagement_report_<YYYYMMDD>.html`).

---

### Component 2: Automated Unit Tests

#### [NEW] [tests/test_engagement_report.py](file:///d:/rouca/DVM/workPlace/IrrigAgent/tests/test_engagement_report.py)
- Unit test suite testing aggregation logic and export features against synthetic mocked datasets.
- Test 1 (`test_aggregation_math`): Verifies exact active farm counts, response rate percentages, and outcome feedback distribution ratios.
- Test 2 (`test_directional_label_triggered_for_small_sample`): Verifies that sample sizes < 5 active farms trigger the "early/directional data" label.
- Test 3 (`test_directional_label_not_triggered_for_large_sample`): Verifies that sample sizes >= 5 active farms omit the warning label.
- Test 4 (`test_empty_dataset_handling`): Verifies clean error/empty handling when Firestore collections have zero documents.

---

## Verification Plan

### Automated Tests
Execute full test suite via `pytest`:
```bash
pytest tests/test_engagement_report.py -v
pytest tests/ -v
```

### Manual Verification
Run the standalone CLI script locally in dry-run/mock mode or against real credentials:
```bash
python scripts/generate_engagement_report.py --output-dir output/
```
Verify generated PNG image and static HTML report in `output/` visually for clean formatting and accurate sample size labeling.
