# Implementation Plan: ONSSA Phytosanitary Registry Sync Tool

**Branch**: `005-onssa-registry-sync` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/005-onssa-registry-sync/spec.md)

**Input**: Feature specification from `specs/005-onssa-registry-sync/spec.md`

## Summary

Build an offline, standalone data synchronization CLI tool (`scripts/sync_onssa_registry.py`) that extracts Morocco's official ONSSA phytosanitary product catalog from `eservice.onssa.gov.ma/IndPesticide.aspx` (~4,700+ registered products across ~470 pagination pages) into a structured local dataset (`data/onssa_registry.json`). Connect `app/cropdoctor.py` to read product recommendations dynamically from this dataset at runtime with seamless fallback to `ONSSA_STATIC_CATALOG`, and update `README.md`.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `requests`, `beautifulsoup4`, `pytest`

**Storage**: Local JSON file (`data/onssa_registry.json`), checkpoint progress (`data/onssa_registry.checkpoint.json`)

**Testing**: `pytest tests/`

**Target Platform**: Developer CLI / GCP Cloud Run environment (Python 3.11 runtime)

**Project Type**: Standalone CLI tool & Python library module

**Performance Goals**: Extraction enforces configurable 2.5s politeness delay; CropDoctor runtime lookup executes in <1ms via pre-indexed in-memory dictionary.

**Constraints**: Single-threaded polite scraping, `robots.txt` compliance, `__VIEWSTATE` postback tracking, checkpoint progress resilience, zero breaking changes to existing CropDoctor behavior.

**Scale/Scope**: ~4,700+ entries, ~470 pages.

## Constitution Check

*GATE: Passed prior to Phase 0 research. Re-checked post-Phase 1 design.*

| Governance Principle | Status | Compliance Details |
| :--- | :--- | :--- |
| **I. Human-in-the-Loop Only** | **PASS** | Offline sync tool and lookup helper; no automated hardware control. |
| **II. Rule-Based First Logic** | **PASS** | Deterministic dictionary indexing for treatment lookups in CropDoctor. |
| **III. Mandatory ONSSA Disclaimer** | **PASS** | ONSSA disclaimer retained in CropDoctor triage responses. |
| **IV. WhatsApp Sandbox Tier Only** | **PASS** | No changes to messaging vendor or tier. |
| **V. Scope Boundary Enforcement** | **PASS** | No hardware control, payment, or soil sensor integrations. |
| **VI. End-to-End Demoability** | **PASS** | Verified via CLI dry-run and CropDoctor integration unit tests. |
| **VII. Infrastructure as Code** | **PASS** | Uses local file storage; zero manual GCP clicking required. |
| **VIII. Quality & Gate Enforcement**| **PASS** | 100% pytest pass rate policy maintained; zero secrets staged or committed. |

## Project Structure

### Documentation (this feature)

```text
specs/005-onssa-registry-sync/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 research findings & design decisions
├── data-model.md        # Phase 1 schema definitions
├── quickstart.md        # Phase 1 quickstart & validation guide
├── contracts/           # Phase 1 interface contracts
│   └── cli-contract.md  # CLI, python module, & CropDoctor API contracts
└── checklists/
    └── requirements.md  # Quality validation checklist
```

### Source Code (repository root)

```text
app/
├── cropdoctor.py        # Updated to load data/onssa_registry.json with fallback

scripts/
└── sync_onssa_registry.py  # [NEW] ONSSA webform scraper CLI & importable module

data/
└── onssa_registry.json     # [NEW] Generated ONSSA registry dataset (committed run)

tests/
├── test_sync_onssa_registry.py # [NEW] Scraper, parsing, & dry-run unit tests
└── test_cropdoctor_onssa.py    # [NEW] CropDoctor ONSSA dataset loading & fallback tests

README.md                # Updated documentation reflecting expanded ONSSA registry dataset
```

**Structure Decision**: Standard single project layout matching the existing `app/`, `scripts/`, `data/`, and `tests/` structure.

## Complexity Tracking

> **No Constitution violations.** (0 entries required)
