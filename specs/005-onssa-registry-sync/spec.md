# Feature Specification: ONSSA Phytosanitary Registry Sync Tool

**Feature Branch**: `005-onssa-registry-sync`  
**Created**: 2026-07-29  
**Status**: Draft  
**Input**: User description: "Create a new feature spec for an internal, standalone data tool — do not touch or modify anything in feature 001-hassan-irrigation-agent or 004-fix-critical-bugs-and-gaps. This is offline tooling, not part of the WhatsApp request path."

## Clarifications

### Session 2026-07-29

- Q: How should the relation to CropDoctor's constrained lookup table (README.md and app/cropdoctor.py) be handled in this feature spec? → A: Expand Feature 005 scope to also wire app/cropdoctor.py to read from data/onssa_registry.json (with fallback to ONSSA_STATIC_CATALOG if file is missing/empty) and update README.md accordingly.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dry-run extraction (Priority: P1)

As a developer, I want to run the ONSSA registry sync tool in dry-run mode so that I can verify it correctly navigates pagination, parses entries, and behaves politely against the live site, without writing anything to a persisted dataset — allowing me to safely test and iterate on the extraction logic before running a full sync.

**Why this priority**: Dry-run verification is essential for safety, politeness, and rapid developer iteration without risking target site disruption or corrupted local state.

**Independent Test**: Can be tested independently by running a bare invocation with no persistence flags. The command fetches up to 20 entries, displays parsed output and a summary, and verifies zero files are written to the main dataset path.

**Acceptance Scenarios**:

1. **Given** no execution mode flag is specified, **When** the developer invokes the sync tool, **Then** the tool defaults to dry-run mode, performs live requests for up to 20 entries (configurable via `--limit N`), displays parsed rows to output, logs execution summary metrics to standard output, and writes zero data to `data/onssa_registry.json`.
2. **Given** dry-run mode is active, **When** entries are processed, **Then** each entry contains all standardized fields (commercial name, active substances, authorized crops, targeted pests/diseases, dosage, pre-harvest interval, max applications, toxicological classification, distributor, homologation validity date), and an execution summary reports successful entry count, failed entry count with raw contents, and elapsed time.

---

### User Story 2 - Full one-shot extraction with explicit persistence (Priority: P2)

As a developer, I want to explicitly trigger a real, persisted extraction run when I choose to, so that writing the actual dataset file is always a deliberate action separate from testing.

**Why this priority**: Persisting the full registry dataset (~4,700+ entries) requires explicit intent, robust postback/session management, politeness controls, and failure resumption capabilities.

**Independent Test**: Can be tested independently by running with `--commit` flag. The tool verifies compliance with site rules (`robots.txt`), extracts all available pages with session state handling and retry backoffs, writes the complete dataset to `data/onssa_registry.json`, and records run metadata.

**Acceptance Scenarios**:

1. **Given** the tool is executed with the explicit commit flag (`--commit`), **When** execution starts, **Then** the tool checks the site's `robots.txt` before making content requests, enforces a 2-3 second delay between sequential requests, manages postback session state across pagination, periodically saves progress checkpoints, and produces `data/onssa_registry.json` containing all extracted entries and run metadata (timestamp, source URL, mode, total count, unparsed rows).
2. **Given** a commit run is interrupted mid-execution, **When** the tool is re-invoked with `--commit`, **Then** execution resumes from the last saved page checkpoint without re-fetching already completed pages.
3. **Given** `robots.txt` forbids access to the target path, **When** the tool evaluates site permissions, **Then** execution aborts immediately with a clear error message in both dry-run and commit modes, writing no output dataset.

---

### User Story 3 - Modular structure for scheduled re-sync (Priority: P3)

As a developer, I want the extraction logic to be structured as a reusable module so that it can be invoked later by automated background schedulers without refactoring.

**Why this priority**: Ensures long-term maintainability so periodic ONSSA catalog updates can be automated in future iterations without altering core logic.

**Independent Test**: Can be tested independently by importing the core extraction module into a separate test wrapper or script and invoking its entrypoint functions programmatically.

**Acceptance Scenarios**:

1. **Given** the core extraction codebase, **When** inspected or imported by an external script, **Then** key functions for dry-run and commit execution are cleanly exposed as an importable module without relying exclusively on script CLI execution side-effects.

---

### User Story 4 - CropDoctor Runtime Dataset Integration & Documentation Update (Priority: P3)

As a developer, I want `app/cropdoctor.py` to read product recommendations from the generated `data/onssa_registry.json` dataset (with fallback to the hardcoded static dict if absent) and update `README.md` documentation so that CropDoctor utilizes the full ONSSA authorized index at runtime.

**Why this priority**: Connects the generated dataset to the application's Leaf Photo Triage feature while preserving high availability through fallbacks.

**Independent Test**: Can be tested independently by running CropDoctor lookups with `data/onssa_registry.json` present versus absent and verifying product matching against the expanded dataset.

**Acceptance Scenarios**:

1. **Given** `data/onssa_registry.json` is present and valid, **When** CropDoctor performs a product lookup for a diagnosed pathogen, **Then** recommendations are retrieved from the extracted ONSSA registry dataset.
2. **Given** `data/onssa_registry.json` is missing or unreadable, **When** CropDoctor performs a product lookup, **Then** system falls back gracefully to `ONSSA_STATIC_CATALOG` without raising uncaught exceptions.
3. **Given** the runtime lookup integration is complete, **When** reviewing `README.md`, **Then** the product recommendation section reflects the expanded ONSSA registry dataset usage.

---

### Edge Cases

- **Target Site Structural Changes**: What happens when ONSSA updates page HTML structure or WebForm postback field names? The parser records unparsed or malformed rows in the error list within run metadata and standard output without crashing the entire run.
- **Network Interruption / Timeouts**: How does the system handle transient network drops during a multi-page sync? The tool applies exponential backoff retries per page request before persisting the last successful page index to disk.
- **robots.txt Disallow**: What happens if `robots.txt` blocks the index path? The tool aborts immediately prior to page scraping and alerts standard error output.
- **Empty / 0-Entry Response**: What happens if the site returns zero matching entries during a search postback? The tool records 0 extracted entries and logs a warning in the summary.
- **Missing / Corrupted JSON Dataset at Runtime**: What happens if CropDoctor tries to read `data/onssa_registry.json` and it is missing or malformed? CropDoctor logs a warning and falls back to `ONSSA_STATIC_CATALOG`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST default to dry-run mode when invoked without explicit execution flags, performing live requests without creating or modifying the target dataset file (`data/onssa_registry.json`).
- **FR-002**: Dry-run mode MUST accept a configurable sample size limit (`--limit N`, default 20) and output human-readable parsed entries along with a execution summary (successful count, failed count with raw content, total elapsed time).
- **FR-003**: System MUST require an explicit commit flag (e.g. `--commit`) to persist extracted entries to `data/onssa_registry.json`.
- **FR-004**: System MUST check target site `robots.txt` before issuing content requests and abort immediately with an error if the target path is disallowed, operating identically in dry-run and commit modes.
- **FR-005**: System MUST identify itself with a custom User-Agent header (including "IrrigAgent-ONSSA-Sync" and contact info) and enforce a configurable politeness delay (default 2-3 seconds) between sequential single-threaded requests.
- **FR-006**: System MUST maintain WebForms ASP.NET session state (`__VIEWSTATE`, `__EVENTVALIDATION`, etc.) across paginated postback requests.
- **FR-007**: System MUST support automatic retry with exponential backoff on transient request failures and support resuming interrupted commit runs from the last checkpointed page.
- **FR-008**: System MUST extract 10 key product fields per entry: commercial product name, active substance(s), authorized crop(s), targeted pest/disease, application dosage, pre-harvest interval (délai avant récolte), maximum application count, toxicological classification, distributor, and homologation validity date.
- **FR-009**: System MUST embed execution metadata in committed JSON outputs, including extraction timestamp, source URL, execution mode, total entry count, and any unparsed row content for manual audit.
- **FR-010**: System extraction tool MUST exist as an offline developer CLI command and importable module, without being executed automatically by FastAPI startup or webhooks.
- **FR-011**: `app/cropdoctor.py` MUST load and parse authorized product recommendations from `data/onssa_registry.json` at runtime when available, falling back gracefully to `ONSSA_STATIC_CATALOG` if the dataset file is missing, empty, or unreadable.
- **FR-012**: System documentation in `README.md` MUST be updated to reflect that product recommendations utilize the expanded ONSSA phytosanitary registry dataset with static fallback.

### Key Entities

- **Phytosanitary Product Entry**: Represents an officially registered plant protection product. Key fields: commercial name, active substances, authorized crops, targeted pests, application dosage, pre-harvest interval (PHI), max application count, toxicity class, distributor, homologation validity date.
- **Sync Execution Metadata**: Metadata accompanying saved registry datasets. Key fields: extraction timestamp, source URL, run mode (commit/dry-run), total entry count, checkpoint page index, unparsed row log.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A default (flagless) invocation performs a dry run fetching up to 20 entries, displays summary stats, and leaves `data/onssa_registry.json` uncreated/unmodified 100% of the time.
- **SC-002**: Executing with `--commit` successfully generates `data/onssa_registry.json` containing structured entries for all available index items, provided site rules permit access.
- **SC-003**: Resuming an interrupted `--commit` execution skips 100% of previously completed pages and continues directly from the last saved page checkpoint.
- **SC-004**: 100% of output entries in the committed dataset include the source extraction timestamp and page traceability metadata.
- **SC-005**: The sync tool completes full extraction without encountering IP rate-limiting or HTTP 429/403 blocks from the target site by adhering strictly to the configured request delay.
- **SC-006**: CropDoctor successfully retrieves product recommendations from `data/onssa_registry.json` when present, and seamlessly falls back to `ONSSA_STATIC_CATALOG` when absent without throwing unhandled exceptions in 100% of test cases.

## Non-Goals

- Does NOT write to Firestore or any production cloud database — output is restricted to local JSON file persistence.
- Does NOT expose extracted registry data via FastAPI endpoints or LLM tools.
- Does NOT execute extraction automatically during application startup, WhatsApp webhooks, or recommendation jobs.
- Does NOT attempt real-time/per-request web scraping during user queries.

## Assumptions

- Target website publishes the phytosanitary product catalog at `eservice.onssa.gov.ma/IndPesticide.aspx`.
- The dataset schema supports local JSON file storage suitable for offline batch generation.
- Integrating this local dataset into CropDoctor's active triage lookup logic (with static fallback) and updating `README.md` is included in this feature scope.
