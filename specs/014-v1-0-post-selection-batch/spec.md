# Feature Specification: v1.0 — ONSSA Live Registry Activation, Frost Alerts, Parcel UX Hardening, and Post-Selection IaC (gated)

**Feature Branch**: `014-v1-0-post-selection-batch`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "/speckit-specify Create a new feature spec covering the MVP+ / Immediate Post-Selection batch (v1.0) from backlog.md — items V1-001 through V1-004. These are independent stories bundled into one spec for tracking, not because they share implementation. Do not begin any implementation of V1-004 until its explicit gating condition is satisfied."

## Clarifications

### Session 2026-07-31

- Q: How should CropDoctor match pathogen and crop_type keys in data/onssa_registry.json? → A: Case-insensitive matching with leading/trailing whitespace stripped (`pathogen.strip().lower()`).
- Q: Which command inputs trigger a boundary collection reset? → A: Case-insensitive multi-language command list (`"restart boundary"`, `"restart"`, `"recommencer"`, `"réinitialiser"`, `"بداية جديدة"`).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Activate Live ONSSA Registry as Primary CropDoctor Source (Priority: P1)

As the system, I want CropDoctor's product lookup to use real, scraped ONSSA registry data as its primary source, with the existing static ~15-30 entry table as a fallback, so that product coverage extends beyond the pilot's hand-curated crop/pathogen list without weakening the existing fail-closed safety guarantee.

**Why this priority**: Resolves V1-001. Expanding product lookup coverage to the full official ONSSA register significantly improves triage utility while maintaining strict regulatory compliance and safety disclaimers.

**Independent Test**: Can be independently tested by querying CropDoctor with crop/pathogen combinations present in the dynamic ONSSA dataset but absent from the static table, verifying dynamic resolution, static fallback, and fail-closed behavior on unknown combinations or file errors.

**Acceptance Scenarios**:

1. **Given** a live ONSSA registry scrape output file populated with official product data, **When** CropDoctor looks up a treatment for a crop and pathogen present in the dynamic dataset, **Then** it returns the matching ONSSA product from the dynamic registry.
2. **Given** a crop and pathogen query not present in the dynamic registry, **When** CropDoctor performs product lookup, **Then** it falls back to checking the static catalog table.
3. **Given** a crop and pathogen query absent from both the dynamic dataset and static catalog, **When** CropDoctor performs product lookup, **Then** it returns no product name (fail-closed) while retaining confidence-tiered messaging and the mandatory ONSSA regulatory disclaimer.
4. **Given** the dynamic dataset file is missing or malformed, **When** CropDoctor performs product lookup, **Then** the system gracefully falls back to static-only behavior without raising errors or crashing.

---

### User Story 2 - Extreme Weather (Frost and Heatwave) Advisory Alerts (Priority: P1)

As Hassan the farmer, I want to be warned when tomorrow's weather forecast includes extreme heat or frost risk, so I can take timely protective action using the same WhatsApp daily advisory channel I already rely on.

**Why this priority**: Resolves V1-002. Protects crops against immediate environmental damage (frost damage or thermal stress) by leveraging the existing daily advisory channel without adding new user overhead.

**Independent Test**: Can be independently tested by injecting weather forecasts exceeding the heat threshold (>40°C) or dropping below the frost threshold (<2°C) into the daily batch pipeline and verifying that warning sections and suggested actions are appended correctly to the message.

**Acceptance Scenarios**:

1. **Given** tomorrow's temperature forecast exceeds the heat threshold (default 40°C), **When** the daily advisory batch job constructs the advisory message, **Then** a distinct, clearly-labeled heat warning section is appended with actionable protective advice (e.g., "apply brief protective misting before dawn") in the farmer's preferred language.
2. **Given** tomorrow's minimum temperature forecast drops below the frost threshold (default 2°C), **When** the daily advisory batch job constructs the advisory message, **Then** a distinct, clearly-labeled frost warning section is appended with actionable protective advice (e.g., "consider frost cloth/protective covering") in the farmer's preferred language.
3. **Given** tomorrow's temperature forecast remains within normal thresholds (2°C to 40°C), **When** the daily advisory batch job constructs the message, **Then** no extreme weather warning section is appended.
4. **Given** an advisory message containing an extreme weather warning, **When** the farmer responds with standard menu options (1/2/3), **Then** interactive reply handling executes identically to standard advisory messages without branch disruption.
5. **Given** a day where both rainfall-skip logic and extreme weather warning conditions trigger, **When** decision processing runs, **Then** both decision elements co-exist harmoniously in the output advisory message.

---

### User Story 3 - Hardened Parcel Boundary Collection Guidance (Priority: P2)

As Hassan the farmer, when I share location pins to define my field boundary on WhatsApp, I want clear, actionable guidance if I share too few pins, pins that are too close together, or an invalid shape, so the system doesn't silently accept unusable boundary data or leave me stuck.

**Why this priority**: Resolves V1-003. Prevents invalid spatial boundary data entry and provides an easy recovery path for non-technical farmers sharing GPS coordinates over messaging interfaces.

**Independent Test**: Can be independently tested by sending fewer than 3 pins, sending pins less than 5m apart, sending self-intersecting polygon coordinates, or issuing a restart command, asserting specific actionable WhatsApp responses for each state.

**Acceptance Scenarios**:

1. **Given** a farmer sharing location pins for field boundary setup, **When** fewer than 3 pins are submitted to complete a boundary, **Then** the system responds with a clear explanation that at least 3 distinct pins are required to form a field polygon.
2. **Given** a farmer sharing location pins, **When** consecutive or submitted pins are implausibly close together (under ~5 meters apart), **Then** the system responds with a warning about duplicate or accidental pin placements and asks the farmer to mark distinct boundary points.
3. **Given** a set of location pins that form a self-intersecting polygon shape, **When** boundary completion is requested, **Then** the system detects the invalid geometry and responds with actionable guidance on placing perimeter pins sequentially without crossing lines.
4. **Given** a farmer who makes a mistake during pin collection, **When** they send a restart command (e.g., "restart boundary"), **Then** the system resets active boundary collection for that field and acknowledges the reset clearly.

---

### User Story 4 - Post-Selection Infrastructure as Code Authoring (Priority: P3, GATED)

As the project maintainer, once StartGate selection is explicitly confirmed, I want declarative Infrastructure as Code (IaC) for the cloud deployment authored fresh, so that environment scaling is automated and reproducible.

**Why this priority**: Resolves V1-004. Deferred post-selection infrastructure task per Constitution Section VII.

**HARD GATE — DO NOT IMPLEMENT NOW**: Tasks associated with this user story MUST NOT be executed or picked up until explicit maintainer confirmation of StartGate selection is recorded. If asked to implement this spec end-to-end prior to gate opening, this story must be skipped and reported as deferred.

**Independent Test**: Reserved for post-selection phase. Upon gate confirmation, validate via automated syntax/lint checks and plan execution against cloud provider sandbox.

**Acceptance Scenarios**:

1. **Given** StartGate selection has NOT been confirmed, **When** implementation or planning workflows process this specification, **Then** User Story 4 tasks are flagged as blocked/deferred with zero code artifacts generated.
2. **Given** explicit confirmation of StartGate selection, **When** IaC authoring is triggered in a dedicated follow-up pass, **Then** clean, declarative scripts are authored covering application service deployment, database instances, daily scheduler jobs, and minimum required service accounts.

---

### Edge Cases

- What happens if the dynamic ONSSA JSON dataset is corrupted or empty? System catches file loading errors and silently falls back to static catalog lookups without crashing or dropping disclaimers.
- What happens if a weather forecast provider returns null or out-of-bounds temperature values? System logs a warning and omits extreme weather alerts while continuing normal advisory delivery.
- What happens if a farmer shares non-location messages or media while boundary collection is in progress? System prompts the user with active boundary status and instructions to either send valid location pins or type the restart command.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST execute the ONSSA registry sync tool once in commit mode against the live registry as part of feature delivery, logging run timestamp, total record count, and parse failure metadata into `data/onssa_registry.json`.
- **FR-002**: CropDoctor product lookup MUST query `data/onssa_registry.json` as its primary lookup source, using case-insensitive and whitespace-stripped key matching (`pathogen.strip().lower()`, `crop_type.strip().lower()`) for crop type and pathogen.
- **FR-003**: CropDoctor product lookup MUST fall back to `ONSSA_STATIC_CATALOG` if no match is found in the dynamic registry, and MUST return `None` (fail-closed) if no match exists in either source.
- **FR-004**: System MUST preserve all existing confidence-tiered messaging rules (no product name emitted on Low confidence) and verbatim mandatory ONSSA regulatory disclaimers regardless of lookup source.
- **FR-005**: Daily advisory engine MUST evaluate tomorrow's forecasted maximum and minimum temperatures against configurable heat (default 40°C) and frost (default 2°C) threshold constants.
- **FR-006**: When forecasted temperatures cross heat or frost thresholds, system MUST append a clearly labeled extreme weather section with localized protective action guidance to the existing daily WhatsApp advisory message.
- **FR-007**: Extreme weather warnings MUST NOT alter existing interactive reply processing (1/2/3 menu actions) or suppress rainfall-skip logic when both conditions apply.
- **FR-008**: Parcel boundary validation MUST check and reject boundary pin sets containing fewer than 3 pins, pins closer than 5 meters apart, or self-intersecting geometries.
- **FR-009**: Parcel boundary collector MUST return specific, user-friendly WhatsApp response messages for each boundary validation error case with actionable instructions.
- **FR-010**: System MUST provide text commands supporting English, French, and Darija (`"restart boundary"`, `"restart"`, `"recommencer"`, `"réinitialiser"`, `"بداية جديدة"`) allowing users to clear in-progress parcel boundary pin buffers and start over.
- **FR-011**: Post-selection Infrastructure as Code (V1-004) MUST remain explicitly gated and blocked from execution until formal StartGate confirmation.

### Key Entities

- **ONSSARegistryEntry**: Dynamic record containing crop type, pathogen, active ingredient, commercial product name, ONSSA authorization number, and source metadata.
- **WeatherThresholdConfig**: Configuration parameters defining heatwave max temperature threshold (°C), frost min temperature threshold (°C), and associated advisory messaging strings per language.
- **ParcelBoundaryBuffer**: In-memory/persisted transient state holding collected GPS coordinates, pin count, validation status, and error state for a farm field boundary setup.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of CropDoctor product lookups prioritize the dynamic ONSSA registry with flawless fallback to static catalog or fail-closed state on missing/malformed dataset files.
- **SC-002**: Extreme weather alerts appear in 100% of daily advisories where forecasted temperatures exceed 40°C or drop below 2°C, with zero disruption to reply menu parsing.
- **SC-003**: 100% of invalid boundary input scenarios (insufficient pins, clustered pins, self-intersection) trigger specific actionable guidance messages rather than generic errors or silent acceptance.
- **SC-004**: Boundary collection state can be reset in under 1 second via user command during active collection workflows.
- **SC-005**: User Story 4 produces zero code artifacts in this pass and remains explicitly recorded as a gated placeholder.
- **SC-006**: 100% pass rate maintained across all automated test suites with zero regression on existing core functionality.

## Assumptions

- The live ONSSA public registry website structure remains accessible to `scripts/sync_onssa_registry.py`.
- Open-Meteo weather API returns valid daily min/max temperature forecasts alongside existing precipitation and ET₀ data.
- WhatsApp location sharing sends standard lat/lon geographic coordinates consumable by polygon geometry helpers.
- Infrastructure as code authoring (V1-004) will be executed in a dedicated future spec cycle once StartGate selection is confirmed by project maintainers.
