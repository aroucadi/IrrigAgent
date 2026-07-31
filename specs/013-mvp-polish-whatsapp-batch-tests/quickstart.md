# Quickstart & Test Execution Guide: MVP Polish — WhatsApp Client Unit Tests & Multi-Farm Batch Integration Test

**Feature Branch**: `013-mvp-polish-whatsapp-batch-tests`  
**Date**: 2026-07-31  

---

## Environment Setup & Prerequisites

All tests run locally using the project's standard Python 3.11+ virtual environment and `pytest`. No live API tokens or network connections are required.

### 1. Execute Isolated WhatsApp Client Unit Tests

To run the newly added WhatsApp unit test suite:

```bash
pytest tests/unit/test_whatsapp.py -v
```

**Expected Outcome**: All assertions pass 100% in < 1.0 second, covering outbound text request formatting, authorization headers, media upload multipart payloads, HTTP error status handling, and inbound webhook extraction (text, image, audio, non-message callbacks).

---

## 2. Execute Multi-Farm Batch Integration Tests

To run the multi-farm daily batch job integration test suite:

```bash
pytest tests/integration/test_daily_batch_multi_farm.py -v
```

**Expected Outcome**: All assertions pass 100% in < 2.0 seconds, verifying multi-farm recommendation generation, profile input isolation, zero cross-contamination, and fault isolation when a single farm lookup encounters a simulated failure.

---

## 3. Execute Full Project Verification Suite

To verify zero regressions across the entire codebase per Constitution Principle VIII:

```bash
pytest tests/
```

**Expected Outcome**: 100% pass rate across all unit and integration tests.
