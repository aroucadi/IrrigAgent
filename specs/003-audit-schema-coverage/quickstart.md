# Quickstart Validation Guide: Audit Schema & Test Coverage Extension

**Feature Branch**: `003-audit-schema-coverage`
**Spec Link**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/003-audit-schema-coverage/spec.md)

## Runnable Validation Scenarios

### 1. Execute Full Test Suite

Run the full automated test suite to ensure all 29+ unit and integration tests execute with a 100% pass rate:

```bash
pytest
```

**Expected Outcome**: 34+ passed tests with 0 failures.

---

### 2. Verify Integration Test Matrix

Run integration tests specifically for webhooks and health/jobs endpoints:

```bash
pytest tests/integration/test_webhook.py -v
```

**Expected Outcome**:
- `test_health_endpoint` PASSED
- `test_daily_advisory_alias_endpoint` PASSED
- All existing webhook tests PASSED

---

### 3. Coverage Summary Verification

Execute test coverage report targeting `app/main.py` and `app/schemas.py`:

```bash
pytest --cov=app tests/integration/test_webhook.py
```

**Expected Outcome**: 100% coverage reported for `/health` and `/api/v1/jobs/daily-advisory` handler routes.
