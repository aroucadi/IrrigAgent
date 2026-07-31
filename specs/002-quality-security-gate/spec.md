# Feature Specification: Quality & Security Gate Module

**Feature Branch**: `002-quality-security-gate`

**Created**: 2026-07-28

**Status**: Implemented

**Input**: User description: "Create a dedicated Quality & Security Gate module for IrrigAgent using Git pre-commit hooks and automated test suites."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Automated Pre-Commit Quality & Security Verification (Priority: P1)

As a developer committing code to the repository, I want git commits to automatically run secret scanning, code formatting/linting checks, and core unit tests so that security credentials are never leaked and breaking changes never reach the repository.

**Why this priority**: Preventing credential leaks and immediate regression detection at commit time protects system security and preserves codebase integrity before code is shared or pushed.

**Independent Test**: Staging a file with a mock secret token or broken test case and attempting `git commit` must fail execution, print actionable terminal diagnostics, and abort the commit.

**Acceptance Scenarios**:

1. **Given** staged Python files containing hardcoded API keys or service account credentials, **When** the developer runs `git commit`, **Then** secret scanning blocks the commit with return code 1 and outputs a red failure message identifying the issue.
2. **Given** staged Python files with formatting or linting errors, **When** the developer runs `git commit`, **Then** the linting check flags the errors and aborts the commit until fixed or auto-formatted.
3. **Given** staged Python files where unit tests in core decision logic or regex parser fail, **When** the developer runs `git commit`, **Then** the test suite run fails and aborts the commit.
4. **Given** valid, properly formatted code with passing tests and no secrets, **When** the developer runs `git commit`, **Then** green checkmarks are displayed and the commit succeeds in under 3.0 seconds.

---

### User Story 2 - One-Touch Developer Gate Setup (Priority: P2)

As a developer checking out the codebase, I want an installation script to configure my local repository hooks automatically so that I don't have to manually copy or permission hook scripts.

**Why this priority**: Standardizes developer onboarding and guarantees that all contributors enforce identical quality and security gates without manual configuration.

**Independent Test**: Running the setup script on a clean repository clone configures the executable git pre-commit hook seamlessly.

**Acceptance Scenarios**:

1. **Given** a developer in a fresh clone of the codebase, **When** they run the setup script, **Then** `.git/hooks/pre-commit` is created/updated with proper executable permissions pointing to the versioned hook source.
2. **Given** an existing git pre-commit hook, **When** the developer runs the setup script, **Then** the hook is safely updated to the latest versioned definition.

---

### User Story 3 - Automated Test Suite Coverage for Decision Logic & Webhook Handlers (Priority: P3)

As a maintainer, I want comprehensive test coverage for response parsing edge cases and webhook integration flows so that changes to WhatsApp message interaction rules or API handlers are verified reliably.

**Why this priority**: Regressions in message parsing (options 1, 2, 3 and edge cases) directly impact farm manager decisions and system reliability.

**Independent Test**: Running the automated test suite verifies all option 1 (approve), option 2 (skip), and option 3 (modify duration/time) parsing logic along with mocked FastAPI webhook endpoints.

**Acceptance Scenarios**:

1. **Given** WhatsApp incoming text payloads matching options 1, 2, or complex option 3 variations (e.g. `3 +10 min at 05:00`, `3 -15 min`, invalid time formats), **When** evaluated by the regex parser tests, **Then** valid inputs parse expected action parameters and invalid inputs are flagged cleanly.
2. **Given** FastAPI webhook HTTP requests, **When** processed during automated integration tests with mocked database and WhatsApp Cloud API services, **Then** responses return expected HTTP status codes and payloads.

---

### Edge Cases

- What happens when a commit contains non-Python files (e.g., Markdown, JSON)? Secret scanning runs across all staged files, while Python linting/tests target Python files appropriately.
- How does the pre-commit script behave if virtualenv tools or pytest are missing? The script provides clear terminal feedback instructing the developer to activate the virtual environment or run setup.
- How are emergency commits handled if needed? Developers retain native `git commit --no-verify` capabilities, though standard commits enforce gates strictly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a versioned pre-commit hook script (`scripts/pre-commit.sh`) and install it to `.git/hooks/pre-commit`.
- **FR-002**: The pre-commit hook MUST run automatically on every `git commit` command and prevent commit execution (return code 1) if any gate fails.
- **FR-003**: Stage 1 of the hook MUST scan staged files for hardcoded secrets (including Meta WhatsApp tokens, Google Cloud service account keys, and Firestore credentials).
- **FR-004**: Stage 2 of the hook MUST run linting and code style checks on staged Python files.
- **FR-005**: Stage 3 of the hook MUST run fast unit test execution to verify core decision engine and regex parser logic without regressions.
- **FR-006**: Terminal output during hook execution MUST feature clean visual formatting (green checkmarks for pass, red markers for fail) with clear, actionable fix instructions.
- **FR-007**: System MUST provide a one-touch installation script (`scripts/install-hooks.sh`) to install or refresh executable hooks across developer machines.
- **FR-008**: The test suite MUST include comprehensive unit tests for `app/regex_parser.py` covering option 1 (approve), option 2 (skip), and option 3 edge cases (e.g., `3 +10 min at 05:00`, `3 -15 min`, invalid formats).
- **FR-009**: The test suite MUST include integration tests for FastAPI webhook handlers in `app/main.py` utilizing mocks for Firestore data access and Meta WhatsApp Cloud API network calls.

### Key Entities

- **Security & Quality Gate**: Pipeline of verification checks (Secret Scanner, Linter/Formatter, Fast Test Suite) evaluated sequentially prior to commit finalization.
- **Pre-Commit Hook Installation**: Versioned distribution mechanism ensuring local developer repository hooks match project standards.
- **Regex Parser Test Matrix**: Suite of structured inputs and expected output specifications validating user message interaction parsing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Committing code containing hardcoded credentials, linting errors, or failing unit tests MUST abort the commit operation with return code 1 (SC-009).
- **SC-002**: Total execution time for the pre-commit hook checks MUST remain under 3.0 seconds on standard commits to maintain high developer velocity (SC-010).
- **SC-003**: 100% of core regex response parsing variations (approval, skip, duration/time modification edge cases) are validated by unit test assertions.
- **SC-004**: All primary FastAPI webhook endpoints are covered by mocked integration tests without external service calls or database side effects.
- **SC-005**: Developer hook setup completes via a single script execution with 0 manual file copying steps required.

## Assumptions

- Python virtual environment with project dependencies (linting tools, pytest, FastAPI test client) is installed on developer workstations.
- Execution environment supports standard POSIX shell script syntax (`sh`/`bash`) compatible with Git hook environments.
- External services (Firestore, Meta WhatsApp Cloud API) are mocked during integration testing to guarantee deterministic execution and sub-second performance.
