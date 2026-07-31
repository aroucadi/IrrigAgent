# Feature Specification: MVP Polish — WhatsApp Client Unit Tests & Multi-Farm Batch Integration Test

**Feature Branch**: `013-mvp-polish-whatsapp-batch-tests`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "/speckit-specify Create a new feature spec — do not modify or bundle this into the P0 stabilization spec (voice ASR / Terraform / spec status) or the Sentinel real-imagery spec, both of which are separate in-flight work. This spec is purely additive test coverage with zero production code changes, and should be safe to implement in parallel with either of those without conflict. Feature name: MVP Polish — WhatsApp Client Unit Tests & Multi-Farm Batch Integration Test"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Direct Unit Test Coverage for WhatsApp Client (Priority: P2)

As a developer maintaining the IrrigAgent platform, I want direct isolated unit test coverage for the core WhatsApp integration functions, so that messaging payload parsing, API endpoint request formatting, auth headers, and media upload handling can be verified independently, making regressions fast to catch and failure points simple to localize.

**Why this priority**: Resolves backlog item POLISH-001. Direct unit coverage prevents regression blindspots in WhatsApp outbound messaging and inbound webhook parsing that currently rely only on indirect integration tests.

**Independent Test**: Can be verified in isolation by executing `pytest tests/unit/test_whatsapp.py` without live network calls or active Cloud API sandbox credentials.

**Acceptance Scenarios**:

1. **Given** mock HTTP requests to Meta Graph API for outbound text messaging, **When** `send_text_message()` is called with valid recipient and payload inputs, **Then** the test asserts correct Graph API URL construction, correct Bearer auth header presence, exact JSON request structure, and successful handling of HTTP 200 responses.
2. **Given** mock HTTP requests returning non-2xx HTTP status codes (e.g., 400 Bad Request or 500 Internal Error), **When** `send_text_message()` or `upload_media()` is called, **Then** the functions handle the failure gracefully according to design (e.g. logging/returning error status or false) without unhandled connection exceptions.
3. **Given** mock binary media data, **When** `upload_media()` is called, **Then** the test verifies multipart/form-data payload structure, media headers, and handles both HTTP success and upload failure responses without real network access.
4. **Given** realistic WhatsApp webhook payload structures for text messages, image messages, and audio/voice messages, **When** `extract_incoming_message()` is invoked, **Then** it correctly parses message fields (sender ID, message body/media ID, message type) into internal representations.
5. **Given** non-message webhook payloads (such as delivery status receipts, read receipts, or status callbacks), **When** `extract_incoming_message()` parses the payload, **Then** it returns `None` without error, locking in existing correct non-message payload handling.

---

### User Story 2 - Multi-Farm Daily Batch Job Integration Test (Priority: P2)

As a developer maintaining batch processing, I want an integration test that triggers the daily recommendation dispatch against multiple farm profiles in a single execution pass, so that the batch dispatch logic is verified to handle multi-farm batches without dropping profiles, mixing up profile inputs, or aborting the entire batch when a single farm fails.

**Why this priority**: Resolves backlog item POLISH-002. Single-farm integration tests cannot detect cross-contamination between farms or batch-level partial failure handling during daily recommendations.

**Independent Test**: Can be verified independently by running `pytest tests/integration/test_daily_batch_multi_farm.py` (or designated multi-farm integration test file) with all external services (Open-Meteo, WhatsApp Graph API, Firestore) mocked.

**Acceptance Scenarios**:

1. **Given** a mock database pre-seeded with at least 2 distinct farm profiles having differing crop types, geographical locations, and preferred communication languages, **When** `POST /jobs/daily-recommendations` is invoked once, **Then** each farm receives its own correctly-differentiated recommendation output corresponding to its specific crop and location profile.
2. **Given** a multi-farm batch execution where an external weather data lookup for one farm encounters a mock network/service failure, **When** the batch job runs, **Then** processing continues for the remaining farms, successfully generating and delivering their recommendations rather than aborting all-or-nothing.
3. **Given** a multi-farm batch run, **When** recommendations are generated and saved, **Then** mock persistence records each recommendation against its corresponding farm document, verifying zero data cross-contamination or state leakage between farms in the same batch execution pass.

---

### Edge Cases

- What happens when a WhatsApp webhook contains valid JSON metadata but missing expected message body fields? `extract_incoming_message` returns `None` safely.
- What happens when an outbound media upload receives an empty response body or invalid JSON from Meta Graph API? `upload_media` handles error responses without throwing uncaught deserialization exceptions.
- What happens when all farm profiles fail their weather lookup during a multi-farm batch? The batch endpoint completes gracefully with zero successful dispatches, returning an appropriate summary response without crashing the server process.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The test suite MUST include dedicated unit tests in `tests/unit/test_whatsapp.py` that cover `send_text_message()`, `upload_media()`, and `extract_incoming_message()` in isolation without live network access.
- **FR-002**: Unit tests for `send_text_message()` MUST assert correct Graph API URL formatting, authorization header format, outbound JSON schema structure, and handling of both success (2xx) and error (4xx/5xx) responses using the project's standard HTTP mocking pattern.
- **FR-003**: Unit tests for `upload_media()` MUST assert multipart form construction and failure handling when media upload endpoints return errors.
- **FR-004**: Unit tests for `extract_incoming_message()` MUST verify parsing of text, image, and audio message payloads, and MUST verify that non-message payloads (e.g. status updates) evaluate to `None`.
- **FR-005**: The test suite MUST include a multi-farm batch integration test under `tests/integration/` that seeds at least 2 distinct farm profiles with differing crop types, locations, and languages.
- **FR-006**: The multi-farm batch test MUST verify that triggering `POST /jobs/daily-recommendations` produces distinct, farm-specific recommendations for each seeded farm without cross-contaminating farm profile data.
- **FR-007**: The multi-farm batch test MUST verify fault isolation such that a failure while fetching weather or processing one farm profile does NOT halt or cancel recommendation processing for other farm profiles in the batch.
- **FR-008**: The implementation MUST NOT introduce any modifications to production codebase files (`app/whatsapp.py`, `app/main.py`, or core business logic). If a underlying code defect is uncovered during test creation, it MUST be logged as a separate backlog item rather than patched within this test-only scope.
- **FR-009**: All test execution MUST complete rapidly using local mocks for Open-Meteo, WhatsApp Graph API, and Firestore persistence, requiring no external network connectivity or real API tokens.

### Key Entities *(include if feature involves data)*

- **WhatsApp Outbound Payload**: Internal request representation sent to Graph API containing recipient phone number, message type (text/media), message content, and media ID.
- **WhatsApp Webhook Inbound Payload**: External JSON payload structure received from Meta webhooks containing entry changes, messages (text, image, audio), or status notifications.
- **Farm Batch Record**: Test entity representing a collection of distinct farm profile documents containing crop type, coordinates, and language preferences processed during a single daily recommendation run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Unit test file `tests/unit/test_whatsapp.py` exists, executes in isolation, and achieves 100% test pass rate covering `send_text_message`, `upload_media`, and `extract_incoming_message` across success and error branches.
- **SC-002**: Multi-farm integration test file exists under `tests/integration/`, executes in isolation, and achieves 100% test pass rate validating multi-farm differentiation and single-farm failure resilience.
- **SC-003**: Zero changes to production code files (spec diff contains exclusively test files, test fixtures, and test mocks).
- **SC-004**: Execution of full suite (`pytest tests/`) passes with 100% success rate and zero regressions against existing tests.

## Assumptions

- Project-standard HTTP mocking patterns established in existing tests (such as `test_weather.py` or `test_cropdoctor.py`) are suitable for mocking Graph API HTTP requests in `test_whatsapp.py`.
- FastAPI `TestClient` or equivalent test runner setup in `tests/integration/` provides the standard framework for testing `POST /jobs/daily-recommendations`.
- POLISH-003 (pytest count verification) and POLISH-004 (recording demo video) are manual operational tasks and are explicitly excluded from this specification.
- Production batch processing logic in `app/` is expected to already support multi-farm loops and fault isolation; test creation will validate this assumption.
