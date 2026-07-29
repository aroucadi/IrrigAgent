# Research: Crop-Specific ETc Calculation (FAO-56)

**Feature**: `006-crop-etc-calculation`
**Date**: 2026-07-29

## Executive Summary

This research establishes the agronomic and software design patterns for transforming reference evapotranspiration ($\text{ET}_0$) sourced from Open-Meteo into crop-specific evapotranspiration ($\text{ET}_c = \text{ET}_0 \times K_c$) using static FAO-56 crop coefficient lookup tables and dynamic growth stage tracking.

---

## Technical Decisions & Rationale

### 1. Data Structure for FAO-56 Crop Lookup Tables

- **Decision**: Implement a static, immutable Python module (`app/fao56.py`) containing crop coefficient values ($K_{c,\text{ini}}$, $K_{c,\text{mid}}$, $K_{c,\text{end}}$) and stage lengths (in days) for Initial ($L_{\text{ini}}$), Development ($L_{\text{dev}}$), Mid-Season ($L_{\text{mid}}$), and Late-Season ($L_{\text{late}}$).
- **Rationale**: Reuses the proven "static cited lookup" pattern established for the ONSSA phytosanitary product table. Fast ($<1\text{ms}$ lookup), deterministic, and requiring no database calls or external API dependencies.
- **Supported Initial Catalog**:
  - **Tomatoes**: $K_{c,\text{ini}}=0.60$, $K_{c,\text{mid}}=1.15$, $K_{c,\text{end}}=0.80$; Stage lengths: 30, 40, 45, 30 days.
  - **Citrus (Mature Orchard)**: $K_{c,\text{ini}}=0.70$, $K_{c,\text{mid}}=0.65$, $K_{c,\text{end}}=0.70$; Year-round perennial schedule.
  - **Watermelon**: $K_{c,\text{ini}}=0.40$, $K_{c,\text{mid}}=1.00$, $K_{c,\text{end}}=0.75$; Stage lengths: 20, 30, 30, 20 days.
  - **Olives (Adult)**: $K_{c,\text{ini}}=0.65$, $K_{c,\text{mid}}=0.70$, $K_{c,\text{end}}=0.65$; Year-round perennial schedule.
  - **Potatoes**: $K_{c,\text{ini}}=0.50$, $K_{c,\text{mid}}=1.15$, $K_{c,\text{end}}=0.75$; Stage lengths: 25, 30, 45, 30 days.
- **Alternatives Considered**:
  - External FAO API or remote database lookup: Rejected because external network calls introduce unnecessary latency, failure points, and breaking offline capabilities.

---

### 2. Growth Stage Progression & Linear Interpolation

- **Decision**: Calculate days elapsed since planting date ($\Delta d = \text{Date}_{\text{calc}} - \text{Date}_{\text{planting}}$). Determine active growth stage and apply piecewise linear interpolation during transition stages per FAO-56 methodology:
  - **Initial Stage** ($0 \le \Delta d \le L_{\text{ini}}$): $K_c = K_{c,\text{ini}}$.
  - **Development Stage** ($L_{\text{ini}} < \Delta d \le L_{\text{ini}} + L_{\text{dev}}$):
    $$K_c = K_{c,\text{ini}} + \frac{\Delta d - L_{\text{ini}}}{L_{\text{dev}}} \times (K_{c,\text{mid}} - K_{c,\text{ini}})$$
  - **Mid-Season Stage** ($L_{\text{ini}} + L_{\text{dev}} < \Delta d \le L_{\text{ini}} + L_{\text{dev}} + L_{\text{mid}}$): $K_c = K_{c,\text{mid}}$.
  - **Late-Season Stage** ($L_{\text{ini}} + L_{\text{dev}} + L_{\text{mid}} < \Delta d \le L_{\text{total}}$):
    $$K_c = K_{c,\text{mid}} + \frac{\Delta d - (L_{\text{ini}} + L_{\text{dev}} + L_{\text{mid}})}{L_{\text{late}}} \times (K_{c,\text{end}} - K_{c,\text{mid}})$$
  - **Post-Harvest** ($\Delta d > L_{\text{total}}$): Maintain $K_c = K_{c,\text{end}}$ and flag post-season cycle.
- **Rationale**: Strict compliance with standard FAO-56 Penman-Monteith crop water calculation guidelines.
- **Alternatives Considered**:
  - Step-wise constant $K_c$ assignment per stage without interpolation: Rejected because it causes artificial sharp jumps in daily crop water recommendations at stage boundaries.

---

### 3. Fallback and Notice Integration

- **Decision**: When `planting_date` is missing from the farm profile or `crop_type` is unrecognized, return $K_c = 1.00$, set stage to `"unknown"`, and append a WhatsApp profile update prompt:
  `"⚠️ Notice: Planting date unrecorded. Using baseline grass ET₀ (Kc=1.00). Update your planting date to get crop-specific precision."`
- **Rationale**: Fulfills Constitution Principle II (deterministic rule-based fallback) and user clarification Q1. Daily recommendation pipeline continues safely without error.
