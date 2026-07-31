# Research & Findings: Internal Engagement & Traction Dashboard

**Feature**: Internal Engagement & Traction Dashboard (Sales Evidence Tool)  
**Branch**: `018-internal-traction-dashboard`  
**Date**: 2026-07-31

## 1. Firestore Schema & Field Verification

The actual Firestore collections and document fields used in `app/firestore_client.py` and `app/main.py` were audited to ensure zero mismatch:

### Collection 1: `farm_profiles` (Document ID: `phone_number`)
- **`phone_number`** (`str`): E.g., `"+212600000000"`.
- **`crop_type`** (`str`): E.g., `"tomatoes"`, `"citrus"`, `"olives"`.
- **`acreage_hectares`** (`float`): E.g., `10.0`.
- **`preferred_language`** (`str`): `"french"` or `"darija"`.
- **`opted_out`** (`bool`): `True` if unsubscribed via `/stop`.
- **`onboarding_incomplete`** (`bool`): `True` if registered but incomplete onboarding.
- **`created_at`** (`str`): ISO-8601 UTC timestamp.
- **`last_inbound_timestamp`** (`str`): ISO-8601 UTC timestamp of last message sent by farmer.

### Collection 2: `irrigation_recommendations` (Document ID: `rec_id`)
- **`recommendation_id`** (`str`): E.g., `"rec_+212600000000_2026-07-31"`.
- **`phone_number`** (`str`): Target farm phone number.
- **`target_date`** (`str`): Format `"YYYY-MM-DD"`.
- **`dispatched_at`** (`str`): ISO-8601 UTC timestamp when advisory was sent.
- **`status`** (`str`): `"pending"`, `"approved"`, `"skipped"`, or `"modified"`.
- **`responded_at`** (`str`): ISO-8601 UTC timestamp of farmer reply ("1", "2", "3").
- **`outcome_feedback`** (`str`): Quick-reply button value recorded by farmer (`"yes"`, `"less"`, `"more"`, `"skipped"`).
- **`outcome_updated_at`** (`str`): ISO-8601 UTC timestamp when feedback button was clicked.

### Collection 3: `disease_triage_requests` (Document ID: `request_id`)
- **`request_id`** (`str`): E.g., `"triage_+212600000000_1722450000"`.
- **`phone_number`** (`str`): Target farm phone number.
- **`created_at`** (`str`): ISO-8601 UTC timestamp when CropDoctor leaf photo was submitted.

---

## 2. Metric Computation & Business Rules

1. **Total Registered Farms**: Count of documents in `farm_profiles` (excluding opted-out or including with breakdown flag).
2. **Active Farms (7d / 30d Window)**: A farm is considered active in the window if `last_inbound_timestamp` or any recommendation `responded_at`/`outcome_updated_at` or triage request `created_at` falls within the last 7 or 30 days.
3. **Daily Advisory Response Rate**: `(Count of recommendations with status != 'pending' or responded_at IS NOT NULL) / (Total dispatched recommendations)` expressed as a percentage.
4. **Outcome Feedback Distribution**: Breakdown of recorded `outcome_feedback` values mapped as:
   - `"yes"` → `Followed (100%)`
   - `"less"` → `Less Water`
   - `"more"` → `More Water`
   - `"skipped"` → `Skipped Irrigation`
   - `None / null` → `No Response Recorded`
5. **Small Sample Directional Data Rule**:
   - **Threshold**: `< 5 active farms` in any reporting time bucket.
   - **Behavior**: Prominently labels the bucket/summary with `[Early / Directional Data (Sample Size < 5)]`.

---

## 3. Technology Choice & Architecture

- **Execution Model**: Single CLI script `scripts/generate_engagement_report.py` runnable locally.
- **Dependencies**: Python 3.11, standard `google-cloud-firestore` for read-only data fetch, `matplotlib` for static chart generation, standard library (`argparse`, `json`, `html`) for rendering reports.
- **Output Artifacts**:
  - `output/engagement_report_<YYYYMMDD>.png`: High-resolution composite chart figure.
  - `output/engagement_report_<YYYYMMDD>.html`: Lightweight static HTML page for screen-shares.
- **Testing Approach**: 
  - Unit tests under `tests/test_engagement_report.py` using `pytest`.
  - Mocks Firestore client entirely to verify math calculations, percentage breakdowns, and directional warning label triggers on small sample sizes (< 5 active farms).
