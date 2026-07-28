# Feature Specification: Audit Schema & Test Coverage Extension

**Feature Branch**: `003-audit-schema-coverage`

**Created**: 2026-07-28

**Status**: Draft

**Input**: User description: "Extend app architecture and test coverage to address Audit Report recommendations for IrrigAgent AI."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enforce Strict Data Validation Schemas (Priority: P1)

As a developer and system operator, I want all incoming webhooks, job requests, farm profiles, and health status responses to be strictly validated against structured schemas so that invalid data is rejected early and response shapes remain contract-compliant.

**Why this priority**: Preventing malformed data payloads and unvalidated response formats guarantees API reliability, audit compliance, and system stability across webhooks and background jobs.

**Independent Test**: Can be tested independently by submitting valid and invalid payloads to API endpoints and validating that structured responses conform exactly to defined schema types.

**Acceptance Scenarios**:

1. **Given** a request to the system health endpoint, **When** a `GET /health` request is received, **Then** the service responds with HTTP 200 and a payload containing status, application name, version string, and Darija voice teaser state.
2. **Given** a farm profile submission or lookup request, **When** payload attributes are processed, **Then** phone number, region, crop type, flow rate in liters per hour, and baseline duration in minutes are strictly validated.
3. **Given** a daily advisory job trigger request, **When** the job finishes processing, **Then** the response strictly returns processing status, count of processed farms, and count of skipped farms.
4. **Given** an incoming WhatsApp webhook verification challenge, **When** verification parameters are provided, **Then** hub mode, hub challenge, and hub verify token are validated against the verification schema.

---

### User Story 2 - Complete Integration Test Coverage Matrix (Priority: P2)

As a QA engineer and developer, I want comprehensive automated integration test cases for health checking and job alias routes so that regressions in core endpoints are caught immediately in the verification pipeline.

**Why this priority**: Completing the test coverage matrix guarantees compliance with Constitution Principle VIII (Zero-Broken-Tests Policy & Automated Verification Gates).

**Independent Test**: Can be tested independently by executing the integration test suite and verifying that health and job alias tests pass with complete endpoint coverage.

**Acceptance Scenarios**:

1. **Given** the automated test runner, **When** `test_health_endpoint()` is executed, **Then** it asserts HTTP status 200 and verifies schema structure compliance for `GET /health`.
2. **Given** the automated test runner, **When** `test_daily_advisory_alias_endpoint()` is executed, **Then** it verifies that `POST /api/v1/jobs/daily-advisory` returns identical status codes, body response, and authorization rules as `POST /jobs/daily-recommendations`.

---

### Edge Cases

- What happens when a request to `/health` occurs while optional features (e.g., Darija voice teaser) are disabled? The response must strictly return `voice_teaser_enabled: false` while maintaining HTTP 200.
- How does the system handle numeric float/int conversions in `FarmProfile` (e.g., non-numeric flow rate or negative baseline minutes)? Validation must fail cleanly with descriptive field error messages without crashing the server.
- What happens if an unauthenticated request hits `POST /api/v1/jobs/daily-advisory`? It must be rejected with identical authorization error credentials as `POST /jobs/daily-recommendations`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST define strict data validation models for health checks (`HealthCheckResponse`), farm profiles (`FarmProfile`), daily advisory job responses (`DailyAdvisoryJobResponse`), and webhook verifications (`WebhookVerification`).
- **FR-002**: System MUST enforce input payload validation and output response serialization using strict data schemas across all API endpoints in the main application module.
- **FR-003**: System MUST provide explicit health endpoint automated test coverage (`test_health_endpoint`) validating HTTP status 200 and structured response attributes.
- **FR-004**: System MUST provide explicit job alias automated test coverage (`test_daily_advisory_alias_endpoint`) ensuring `/api/v1/jobs/daily-advisory` exhibits identical status and authorization behavior as `/jobs/daily-recommendations`.
- **FR-005**: All system unit and integration tests (29+ total test cases) MUST execute with a 100% pass rate under automated testing.
- **FR-006**: Both `GET /health` and `POST /api/v1/jobs/daily-advisory` routes MUST reach 100% test coverage in automated coverage summary reports.

### Key Entities *(include if feature involves data)*

- **HealthCheckResponse**: Represents system operational status, application identifier, version, and voice teaser status.
- **FarmProfile**: Represents farm configuration parameters including recipient phone, geographical region, crop type, irrigation flow rate (LPH), and baseline duration (minutes).
- **DailyAdvisoryJobResponse**: Represents execution metrics for automated advisory runs, including status, processed count, and skipped count.
- **WebhookVerification**: Represents Meta WhatsApp webhook challenge verification parameters (hub mode, hub challenge, hub verify token).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% pass rate across all 29+ unit and integration tests in the test suite.
- **SC-002**: 100% automated test line coverage reported for both `GET /health` and `POST /api/v1/jobs/daily-advisory` endpoints.
- **SC-003**: 0 payload validation bypasses or unhandled schema exceptions across all API endpoints.

## Assumptions

- Target environment uses Python 3.11+ with Pydantic v2 support.
- Existing authorization header requirements for background job endpoints remain consistent across original and alias routes.
- Test suite framework relies on `pytest` and standard HTTP client test runners.
