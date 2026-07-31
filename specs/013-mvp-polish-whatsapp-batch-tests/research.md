# Phase 0 Research & Technical Decisions: MVP Polish — WhatsApp Client Unit Tests & Multi-Farm Batch Integration Test

**Feature Branch**: `013-mvp-polish-whatsapp-batch-tests`  
**Date**: 2026-07-31  

---

## 1. HTTP Client Mocking Pattern for `tests/unit/test_whatsapp.py`

### Decision
Use `unittest.mock.patch` (or `pytest-asyncio` + `unittest.mock.AsyncMock`) on `httpx.AsyncClient` alongside fixture-level overriding of `WHATSAPP_TOKEN` (e.g., setting `WHATSAPP_TOKEN = "test_real_graph_token"` during tests).

### Rationale
In `app/whatsapp.py`, the internal helper function `_is_mock_token(token)` checks if `WHATSAPP_TOKEN` starts with placeholder prefixes (`mock_`, `your_`, `eaag_your_`) or is empty. If true, `send_text_message` and `upload_media` return hardcoded mock dicts without invoking `httpx.AsyncClient`. 

To achieve true unit test coverage of request formatting (Graph API URL, `Authorization: Bearer` headers, `messaging_product`, JSON schema, multipart form fields) and HTTP error branches (4xx/5xx `raise_for_status()` handling), tests must:
1. Temporarily patch `WHATSAPP_TOKEN` to a non-mock string (e.g., `"test_real_graph_token"`).
2. Intercept `httpx.AsyncClient.post` and `httpx.AsyncClient.get` calls using `AsyncMock` to verify outgoing URL, headers, JSON body / multipart files, and to simulate 200 OK or 400/500 HTTP status code exceptions (`httpx.HTTPStatusError`).

### Alternatives Considered
- **Live Graph API Sandbox Calls**: Rejected. Requires live Meta credentials, network connectivity, and violates FR-009 (offline/rapid local execution) and Constitution Principle VIII (zero secrets in code).
- **Testing Only with Default `_is_mock_token` = True**: Rejected. Short-circuits prior to `httpx.AsyncClient` construction, failing the No-Facade Rule (Constitution VIII) and leaving Graph API payload assembly unverified.

---

## 2. Multi-Farm Batch Integration Testing Pattern for `tests/integration/test_daily_batch_multi_farm.py`

### Decision
Use FastAPI `TestClient` (or `httpx.AsyncClient` bound to `app`) to invoke `POST /jobs/daily-recommendations` with header `Authorization: Bearer <JOB_SECRET_TOKEN>`. Mock underlying async dependencies (`list_active_farm_profiles`, `get_et0_forecast`, `save_recommendation`, `send_text_message`) using `unittest.mock.patch`.

### Rationale
- Seeding 2+ distinct farm profiles (e.g., Farm A: Tomatoes in Agadir / French; Farm B: Citrus in Berkane / Darija) in `list_active_farm_profiles` allows testing:
  1. **Data Differentiation**: Farm A receives ET₀ recommendation tailored to tomatoes/Agadir; Farm B receives ET₀ recommendation tailored to citrus/Berkane.
  2. **Fault Isolation**: Simulating a weather lookup failure (`get_et0_forecast` raising an exception or returning error quality) for Farm A allows validating whether processing for Farm B continues.
  3. **Batch Reporting**: Verifying `DailyAdvisoryJobResponse` fields (`processed_count`, `skipped_count`, `dispatched_count`, `failed_count`).

### Alternatives Considered
- **Direct function call to `trigger_daily_recommendations`**: Secondary option, but using `TestClient` tests endpoint HTTP authentication (`JOB_SECRET_TOKEN`), header validation, and serialization end-to-end.

---

## 3. Strict Scope & Zero Production Code Changes Guardrail

### Decision
All deliverables under `013-mvp-polish-whatsapp-batch-tests` are strictly confined to test files:
- `tests/unit/test_whatsapp.py`
- `tests/integration/test_daily_batch_multi_farm.py`
- `specs/013-mvp-polish-whatsapp-batch-tests/*`

### Rationale
Per FR-008, no production files (`app/whatsapp.py`, `app/main.py`) may be modified. If test execution uncovers any edge-case logic flaw in production, it will be documented in `plan.md` / `research.md` as a separate backlog item rather than patched within this feature.
