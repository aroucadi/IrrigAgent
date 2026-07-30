# IrrigAgent AI — Product Backlog & Roadmap

**Last updated:** 2026-07-30
**Source:** Reconciled from hands-on codebase audit + `analysis_results.md` cross-spec report
**How to read this:** Items are grouped by release horizon, not by when they were requested. An item's tier reflects how close it is to being safe/ready to ship, not how interesting it is. 🔴 items block trusting anything else in this document.

---

## 🔴 P0 — Fix Before Any Further Feature Work (Pre-Submission Risk)

These are things currently in the repo that are marked "Completed & Verified" but are not what they claim to be. Each is a live risk if triggered in a demo or by a real pilot farmer before it's fixed.

### BUG-001: Voice-to-Intent (Darija STT) has no real speech-to-text call
**File:** `app/decision.py`, `parse_voice_intent()`
**Severity:** Critical
**What's wrong:** The function returns a hardcoded transcript ("Zid 15 dqiqa f l-sqi ghadan") and fixed 0.88 confidence for any real audio input. There is no Gemini audio ASR call in the code path. Every real voice note, regardless of content, produces the identical proposed action (+15 min irrigation).
**Why it matters:** The confirmation-loop safety design around this (15-min TTL pending intent, mandatory 1/2/3 confirmation) is genuinely well-built — but it's gating a feature that doesn't exist yet. If a real farmer or a juror sends a voice note in a live demo, the response will be wrong or nonsensical relative to what they said.
**Fix:** Wire `parse_voice_intent()` to an actual Gemini 1.5 Flash audio call per the existing `research.md` in spec 009. Keep the confirmation-loop logic as-is — it doesn't need to change, only the transcription source does.
**Acceptance:** A test asserting that distinct, realistic audio inputs produce distinct transcripts — not the same string every time — must pass before this is called done.

### BUG-002: Sentinel-2 canopy heatmap uses fully synthetic, seeded-random data
**File:** `app/sentinel.py`, `fetch_sentinel2_bands()`
**Severity:** Critical
**What's wrong:** `np.random.seed(42)` plus a fixed sine/cosine pattern generates identical fake NDVI data for every farm, every request, regardless of real location. No Sentinel-2, Copernicus, or Earth Engine API is called anywhere in this module. A farmer would receive a fabricated "moderate stress in your SE sector" message describing nothing real about their field.
**Why it matters:** This directly contradicts the project's core credibility claim — every other feature (ONSSA lookups, disclaimers, confidence gating) is built around never presenting fabricated output as real. This feature currently does exactly that.
**Fix options (pick one for MVP):**
  - (a) Wire a real integration — Sentinel Hub or Google Earth Engine free tier — before this ships to any real user.
  - (b) If real integration isn't feasible before the deadline, explicitly gate the feature off (same pattern as `ENABLE_DARIJA_VOICE_TEASER`) and remove it from any demo or pitch material until real data is wired.
**Do not** demo or describe this feature as working satellite analysis until (a) is done.

### BUG-003: Terraform/IaC scope has re-appeared a third time
**File:** `infra/*.tf` (6 files), constitution Principle VII
**Severity:** Process, not code-correctness
**What's wrong:** This was explicitly deferred to post-selection twice already. It's back in the repo, and the latest analysis report counts it as a positive metric ("7 IaC Files ✅") rather than flagging it as scope that shouldn't have been touched pre-deadline.
**Fix:** Decide once, explicitly, and write the decision into the constitution so it stops re-appearing: either (a) delete `infra/` entirely until post-selection, or (b) if it's staying because it's already built and not costing further time, add an explicit constitution note: *"infra/ exists but is not used for pilot deployment; gcloud run deploy remains the only sanctioned deployment path pre-selection."* Either is fine — leaving it undecided is what's causing the repeat drift.

### BUG-004: Spec statuses stuck on "Draft" despite 100% task completion
**Severity:** Low, but worth doing alongside the above since you'll be in these files anyway
**Fix:** Update `Status: Draft` → `Status: Implemented` header in each completed spec.md (001–006, and once fixed, 009). Five minutes, referenced correctly in the analysis report as G3.

---

## 🟡 P1 — MVP Polish (Non-Blocking, Do Before Sept 13 If Time Allows)

Carried over from the analysis report's own recommendations — these are legitimately low-risk and low-effort.

### POLISH-001: Add `tests/unit/test_whatsapp.py`
Direct unit tests for `send_text_message` and `upload_media`, currently only covered indirectly via integration tests. ~30 min.

### POLISH-002: Add multi-farm batch job integration test
`POST /jobs/daily-recommendations` has no test exercising 2+ farms in a single batch run. ~45 min.

### POLISH-003: Verify real test count before quoting it anywhere
Run `pytest --collect-only -q | tail -5` and use that number in any pitch material — don't repeat "127" or my "111" without checking directly.

### POLISH-004: Record the StartGate demo video
Once BUG-001 and BUG-002 are resolved or explicitly gated off — this was always the actual deliverable.

---

## MVP+ — Immediate Post-Selection (v1.0)

Things worth doing right after acceptance, before deeper feature work — mostly closing gaps in what already exists rather than new capability.

### V1-001: Move ONSSA registry from static-only to hybrid dynamic + fallback
Spec 005's scraper is built and reportedly wired into CropDoctor with "dynamic dataset loading + static fallback" per the report — worth a direct verification pass (same standard as everything else here) once it's actually run against the live site with `--commit`, not just tested against fixtures.

### V1-002: Frost / heatwave threshold alerts
From the vNext roadmap — reuses the existing Open-Meteo + Cloud Scheduler + WhatsApp pipeline entirely, no new dependency. Still not built as of this repo snapshot. Cheapest genuinely new feature available.

### V1-003: Parcel-boundary collection UX refinement
`app/parcel_validation.py` exists (GeoJSON polygon validation) — worth confirming the actual WhatsApp-side collection flow (asking a farmer for 3–4 location pins) is farmer-tested, not just schema-validated, before leaning on it for BUG-002's real fix.

### V1-004: Terraform decision executed (see BUG-003)
Formal migration to IaC, if that's the chosen path, scoped as its own spec once genuinely post-selection.

---

## v2 — Medium-Term (Data- or Validation-Dependent)

These are legitimate, well-motivated features that are blocked on something other than engineering time — sourcing data, or getting a real partner (IAV) engaged. Don't schedule engineering sprints against these until the blocker is actually resolved.

### V2-001: Fine-tuned CropDoctor disease classifier
`scripts/ingest_iav_dataset.py` is correctly built as a gated waiting mechanism (500 verified samples/class threshold) — genuinely honest engineering, not a facade. **Blocked on:** IAV Hassan II actually providing or helping source labeled Moroccan leaf-disease images. This is a partnership-conversation blocker, not a coding one — worth raising explicitly and early during incubation, since data collection takes calendar time regardless of engineering bandwidth.

### V2-002: IoT soil-moisture monitoring (read-only)
Sensor data feeding into the recommendation engine as an additional input — improves recommendation quality without changing the human-approval safety model. Legitimate v2 candidate once there's a pilot cooperative willing to pilot hardware.

### V2-003: Farmer-to-farmer same-area disease alerts
A confirmed CropDoctor diagnosis triggers a proximity-based alert to nearby registered farms (using parcel GPS already being collected). Genuinely differentiated — this is where multi-agent coordination adds real value beyond a single-farmer chatbot. **Needs:** a confidence/verification gate before any fan-out (an unconfirmed diagnosis alerting neighbors is worse than no alert), and explicit farmer opt-in consent.

### V2-004: Authority (ONSSA / extension services) integration for verified outbreak signals
Routes confirmed, high-confidence disease clusters to a human authority for review/action — a legitimate "reviewer node" pattern. **Blocked on:** a real conversation with ONSSA or regional extension services about what obligates them to act and what IrrigAgent is liable for if they don't. This is a partnership and liability question before it's a technical one — don't build speculative integration code before that conversation happens.

### V2-005: Regional analytics / farmer clustering
Aggregated view of confirmed diagnoses and irrigation patterns by region, once real pilot volume exists. Worth being precise in any pitch material that this is data aggregation, not "AI clustering" — the honest framing is also the more credible one.

---

## v3 — Longer-Term / Strategic (Needs Its Own Deliberate Decision Process)

### V3-001: IoT command / autonomous valve control
**This is not a normal backlog item — flag before scheduling.** This directly reopens the single principle the entire project's constitution has been built around since day one: human-in-the-loop only, no autonomous hardware control. Given that two "Completed & Verified" features in this same repo turned out to be fabricated outputs (BUG-001, BUG-002), the bar for trusting an autonomous actuation feature needs to be categorically higher than anything shipped so far — a wrong signal here doesn't produce an embarrassing demo, it can physically damage a real crop or waste real water on a real farm. If this is ever pursued, it needs its own explicit constitution amendment and sign-off process, not a standard `/speckit.specify` prompt.

### V3-002: Bidirectional multi-crop expansion beyond tomatoes/citrus
Once ONSSA registry integration (V1-001) and the fine-tuned classifier (V2-001) are both real and validated, expanding supported crops becomes primarily a data/cataloging exercise rather than new architecture.

---

## Parking Lot — Explicitly Not Scheduled

Ideas worth remembering, not worth a roadmap slot yet.

- **Starlink / satellite ISP integration** — not a product feature, it's infrastructure outside IrrigAgent's control. The right move is designing for graceful degradation on poor connectivity (partially already true via the existing retry/async patterns), not integrating a specific ISP.
- **GPS "exploitation" as a standalone feature** — this is the substrate for V2-003/V2-004/V2-005, not a separate feature. Fold into those specs rather than building generic geo-infrastructure speculatively.

---

## Process Note (Add to Constitution)

Given BUG-001 and BUG-002, worth formalizing this rule so it stops recurring:

> **No feature may be marked "Completed & Verified" if its core external API/model call has a hardcoded or synthetic default path reachable in production. Every completion claim must include a test that fails when realistic (non-fixture) input hits that path with the mock still in place.**

This single rule, applied retroactively, would have caught both P0 bugs before they were reported as done.
