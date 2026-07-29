# Feature Specification: Crop-Specific ETc Calculation

**Feature Branch**: `006-crop-etc-calculation`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Implement crop-specific ETc calculation using static FAO-56 Kc stage lookup tables (Initial, Mid, Late) applied to Open-Meteo et0_fao_evapotranspiration daily pulls. REF @[PRDvNext.md]"

## Clarifications

### Session 2026-07-29

- Q: How should the system handle communication and calculation fallback when a registered farm profile has a crop type configured but no planting date set? → A: Fallback to generic reference `Kc = 1.00`, proceed with recommendation generation, and append a profile update prompt in the daily WhatsApp message encouraging planting date configuration.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Accurate Crop Water Demand Calculation (Priority: P1)

As a farm manager receiving daily irrigation recommendations, I want the system to calculate my crop's actual evapotranspiration (ETc) based on its growth stage and FAO-56 crop coefficients (Kc) rather than using reference grass evapotranspiration (ET₀) directly, so that irrigation depth and duration accurately match my specific crop's actual water requirements.

**Why this priority**: Directly solves crop water demand over- or under-estimation by transforming reference grass evapotranspiration (ET₀) into crop-specific evapotranspiration (ETc = ET₀ × Kc), providing agronomic accuracy.

**Independent Test**: Can be tested by providing daily Open-Meteo ET₀ values alongside a registered crop type and planting date, verifying that calculated daily ETc equals `ET₀ × Kc` for the calculated growth stage.

**Acceptance Scenarios**:

1. **Given** a registered farm growing tomatoes planted 45 days ago (Mid-season stage with Kc = 1.15) and a daily Open-Meteo ET₀ pull of 5.0 mm/day, **When** daily irrigation requirements are calculated, **Then** the resulting crop water demand (ETc) MUST be 5.75 mm/day (5.0 × 1.15).
2. **Given** a registered farm growing citrus trees in Initial stage (Kc = 0.70) and a daily ET₀ pull of 4.0 mm/day, **When** daily irrigation requirements are calculated, **Then** the resulting crop water demand (ETc) MUST be 2.80 mm/day (4.0 × 0.70).

---

### User Story 2 - Automated Growth Stage Determination (Priority: P2)

As a farm manager, I want the system to automatically determine my crop's current growth stage (Initial, Crop Development, Mid-Season, Late Season) based on days elapsed since planting date, so that crop coefficients update automatically over the growing season without requiring manual stage updates.

**Why this priority**: Eliminates manual daily management by deriving stage progression dynamically from planting date using standardized FAO-56 stage duration guidelines for supported crop types.

**Independent Test**: Can be tested by supplying various planting dates for a target crop and confirming that the derived growth stage and corresponding Kc coefficient match the FAO-56 stage schedule.

**Acceptance Scenarios**:

1. **Given** a tomato crop with an initial stage duration of 30 days, **When** current date is 15 days past planting date, **Then** the crop MUST be classified in the Initial growth stage with `Kc_ini`.
2. **Given** a crop progressing past its Mid-season duration into the Late season, **When** growth stage evaluation runs, **Then** the system MUST transition the crop coefficient from `Kc_mid` towards `Kc_end`.

---

### User Story 3 - Missing Growth Stage Metadata Fallback (Priority: P3)

As a system operator, I want the system to gracefully handle missing or incomplete farm profile crop parameters (such as an unrecorded planting date), so that daily recommendation runs continue operating safely with a documented fallback reference coefficient.

**Why this priority**: Guarantees system robustness and zero crash rate when onboarding new farms before complete planting metadata is recorded.

**Independent Test**: Can be tested by executing the daily ETc calculation for a farm profile with a known crop type but missing planting date, verifying that a safe default Kc of 1.0 is applied and logged.

**Acceptance Scenarios**:

1. **Given** a farm profile with a registered crop type but no planting date specified, **When** daily ETc calculation is invoked, **Then** the system MUST fall back to a default reference crop coefficient (`Kc = 1.00`), append a profile update prompt in the daily WhatsApp message encouraging planting date configuration, and complete the daily recommendation cycle without failure.

---

### Edge Cases

- **Post-Harvest / Out of Bounds Planting Date**: What happens when the days since planting exceed the total cumulative growth period defined for the crop? The system MUST maintain the `Kc_end` coefficient for post-season maintenance and log a prompt for the user to update or reset their crop cycle.
- **Negative or Zero Daily ET₀ Pull**: What happens when Open-Meteo returns 0.0 mm/day or missing weather data? The ETc MUST compute to 0.0 mm/day without division-by-zero or calculation errors, preserving minimum threshold logic.
- **Perennial vs. Annual Crops**: How does the system handle perennial crops (e.g., adult citrus or olive orchards) where planting date occurred years prior? For mature perennials, the system MUST use seasonal calendar month ranges (or active stage lookup) rather than days-since-planting.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST compute daily crop evapotranspiration (`ETc`) using the formula `ETc = ET₀ × Kc`, where `ET₀` is sourced directly from the Open-Meteo daily `et0_fao_evapotranspiration` pull.
- **FR-002**: System MUST maintain a static, verified lookup table of FAO-56 crop coefficients (`Kc_ini`, `Kc_mid`, `Kc_end`) and stage durations (Initial, Development, Mid-Season, Late-Season) for supported crops (including Tomatoes, Citrus, Watermelon, Olives, and Potatoes).
- **FR-003**: System MUST dynamically determine the active growth stage for annual crops using the elapsed number of days between the farm's recorded planting date and the calculation date.
- **FR-004**: System MUST apply linear interpolation for crop coefficient `Kc` during the Crop Development stage (transitioning from `Kc_ini` to `Kc_mid`) and Late-Season stage (transitioning from `Kc_mid` to `Kc_end`) in adherence with FAO-56 specifications.
- **FR-005**: System MUST provide a deterministic fallback crop coefficient (`Kc = 1.00`) and append a profile update prompt in the daily WhatsApp message when a farm profile lacks planting date metadata or specifies an unrecognized crop type.
- **FR-006**: System MUST persist the calculated `ETc`, derived `Kc`, and active growth stage in the daily calculation execution log for auditability and verification.

### Key Entities *(include if feature involves data)*

- **Crop Coefficient Table (FAO-56 Reference)**: Static reference table mapping crop types to stage lengths (days for Initial, Dev, Mid, Late) and stage coefficient values (`Kc_ini`, `Kc_mid`, `Kc_end`).
- **Farm Crop Profile**: Entity storing farm crop parameters, including crop type, planting date (or maturity status for perennials), and optional custom stage overrides.
- **Daily Water Demand Record**: Computed result storing date, pulled reference `ET₀`, applied `Kc`, active growth stage, derived `ETc` (mm/day), and final net irrigation requirement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of daily irrigation calculations for farms with valid crop profiles utilize stage-adjusted ETc instead of unadjusted ET₀.
- **SC-002**: ETc calculation execution completes in under 10 milliseconds per farm profile, adding zero noticeable latency to daily batch recommendation jobs.
- **SC-003**: 100% deterministic test coverage for all stage transitions (Initial, Development interpolation, Mid-season, Late-season interpolation, and post-harvest bounds) across all supported FAO-56 crop types.

## Assumptions

- Reference evapotranspiration `ET₀` pulled from Open-Meteo (`et0_fao_evapotranspiration`) is already calculated according to the standard FAO-56 Penman-Monteith equation (as documented in PRD vNext Section 1.1).
- Farm profiles provide crop type and planting date during onboarding or profile updates.
- Initial supported crop catalog focuses on primary Moroccan agricultural crops: Tomatoes, Citrus, Watermelon, Olives, and Potatoes.
- Water requirement calculations assume non-stressed crop conditions (stress coefficient `Ks = 1.0` for standard baseline recommendation).
