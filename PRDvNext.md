# IrrigAgent AI — PRD vNext (Post-Selection Technical Roadmap)

**Extends:** IrrigAgent_AI_PRD_v0.4.md (MVP/application scope) — this document does NOT modify or supersede that PRD's scope, constitution, or Sept 13 deliverables.
**Status:** Forward-looking roadmap only. Nothing in this document is authorized for pre-submission implementation. Treat every item here the way Terraform IaC and the Darija voice-input concept have already been treated in this project: real, worth planning, explicitly deferred.
**Purpose:** Capture the technical elevation ideas proposed for making IrrigAgent a "standard-setting, pitch-ready platform" — sourced from a review of the current MVP against what would strengthen it for IAV Hassan II / UM6P scrutiny post-selection — with honest effort, risk, and sequencing assessment attached to each.

---

## 0. How to use this document

Every idea below is real and worth having on the roadmap. None of them are worth trading against the September 13 deadline or the current pilot's stability. When any of these graduates from "roadmap" to "spec," it should go through the same `/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` path as everything else, as its own properly-scoped feature — not bundled into an existing one, the way the Terraform and voice-teaser scope drift happened last time.

Each section below is tagged with a priority tier:

- **Tier 1 — Near-term, low effort, high credibility.** Safe to pick up first once the pilot is stable.
- **Tier 2 — Medium effort, real value, has a dependency to resolve first** (usually data or UX design).
- **Tier 3 — High effort or high risk, sequence last, needs its own safety design.**

---

## 1. Evapotranspiration Rigor — Correcting the Premise, Then Scoping the Real Work

**Tier 1**

### 1.1 Correction: you already have FAO-56 Penman-Monteith

The proposal to "implement standard FAO-56 Penman-Monteith" from scratch — full radiation/wind/humidity equation, `pyeto`/`ETo` libraries, custom pipeline — is solving an already-solved problem. Open-Meteo's `et0_fao_evapotranspiration` field, which `app/weather.py` already consumes, is documented by Open-Meteo as computed via the standard FAO-56 Penman-Monteith method using temperature, wind speed, humidity, and solar radiation — not a simplified temperature-only approximation like Hargreaves. Rebuilding this yourself would mean maintaining a scientific calculation engine, sourcing your own radiation/humidity/wind feeds, and validating it against a reference implementation — for a number you're already receiving, computed correctly, for free.

**Recommendation:** do not build a custom ET₀ engine. Keep Open-Meteo as the ET₀ source. If IAV Hassan II specifically wants to see the underlying methodology explained (not re-implemented) in your pitch materials, that's a documentation task, not an engineering one — a short technical appendix citing the FAO-56 standard and Open-Meteo's use of it is sufficient and honest.

### 1.2 The real gap: ET₀ → ETc via crop coefficients

This part of the original proposal is genuinely worth building, and is much smaller than it looks once 1.1 is corrected:

- Reference ET₀ describes a hypothetical well-watered grass surface, not your actual crops. Actual crop water demand is `ETc = ET0 × Kc`.
- **Scope:** implement a small, static Kc lookup table (not a model, not an API) keyed by crop type + growth stage, sourced from the FAO-56 published crop coefficient tables — same "static, cited lookup" pattern already used successfully for the ONSSA product table.
- **Growth stage tracking** is the actual new piece of state: today, farm profiles don't track planting date or growth stage at all. This needs a lightweight addition — e.g., farmer provides an approximate planting date at onboarding (or via the existing `update` command pattern), and the system derives Initial/Mid-season/Late-season stage from days-since-planting per FAO-56's typical stage-length guidance for tomatoes and citrus.
- **Effort estimate:** roughly a day — a static table (like the ONSSA one) plus one new farm profile field and a stage-lookup function. This is the correct-sized version of "industry-accurate ET calculations," not the full custom-engine version.

### 1.3 Elevation correction — verify before building

The proposal to manually elevation-correct atmospheric pressure assumes Open-Meteo's ET₀ output doesn't already account for a farm's elevation. This needs verification, not assumption, before committing effort — Open-Meteo's weather models are elevation-aware for most parameters at the coordinate level. Check this specifically (a quick comparison of ET₀ output at two known elevations for the same region) before building a redundant correction layer. Don't repeat the mistake in 1.1 of re-solving something already handled upstream.

---

## 2. CropDoctor Vision Architecture Upgrade

**Tier 2 — real value, blocked on data, not on engineering time alone**

### 2.1 What's proposed vs. what the pilot needs

The suggested architecture (fine-tuned ViT/EfficientNet-B4, PlantVillage + region-specific training data, temperature-scaled calibration, quality-gate + classifier two-stage pipeline) is a legitimate, credible v2 direction — this is genuinely what a "world-class" version of CropDoctor looks like. It is also a real ML project, not a scoped feature, and it depends on something IrrigAgent doesn't currently have: **labeled, region-specific training and evaluation data for Moroccan tomato/citrus disease presentations.** PlantVillage alone is a well-known, heavily-studied but non-Moroccan dataset — leaf disease presentation varies by cultivar, climate, and regional pest pressure, which is exactly the gap the PRD's IAV Hassan II ask was already built around.

**This reframes the ask to IAV Hassan II, productively:** instead of (or in addition to) validating the existing static ONSSA lookup table, the incubation-period ask could explicitly include help sourcing or creating a small labeled Moroccan leaf-disease image set — turning a stated program resource into the actual unblocking dependency for this roadmap item, not just a review pass.

### 2.2 Split into two genuinely separable pieces

**2.2a — Quality gate (Tier 1, doable now-ish, no training data needed):** a lightweight pre-check — is there a leaf in this photo at all, is it in focus, is exposure usable — can be built with a small pretrained model or even simple heuristics (blur detection via image variance, basic object presence) without any fine-tuning or labeled disease data. This is a good near-term candidate on its own, and it directly strengthens the "unreadable/non-plant photo" handling already in the MVP spec, rather than replacing it.

**2.2b — Fine-tuned disease classifier (Tier 3, genuinely blocked):** this is the part that needs a real dataset, a training/eval pipeline, and calibration work (temperature scaling requires a held-out labeled validation set — you can't calibrate confidence without data to calibrate against). Don't schedule this until 2.1's data dependency has a real answer. Committing engineering time to model architecture before the data exists is effort spent on the wrong bottleneck.

### 2.3 On "fail-closed" thresholds

The proposed 75% confidence cutoff for showing a product name is a reasonable number to test, but it shouldn't be treated as settled without calibration data — an uncalibrated model's "75%" and a properly temperature-scaled model's "75%" mean different things. Keep the existing confidence-tier logic (already fail-closed by design in the MVP) as the mechanism; treat the specific threshold as something to tune once 2.2b produces real calibration data, not before.

---

## 3. "Wow Factor" Feature Candidates — Assessed Individually

None of these are equally sized. Treating them as a uniform "pick one or two" menu undersells how differently they should be sequenced.

### 3.1 Option A — Extreme Weather / Frost Early-Warning Alerts

**Tier 1 — the strongest near-term candidate of the three.**

This reuses infrastructure you already have end-to-end: same Open-Meteo weather pull, same daily batch job, same WhatsApp text-delivery path, same Firestore farm profile. The only new work is a threshold check (`>40°C` or `<2°C` forecast) and a distinct message template. No new external dependency, no new data problem, no new safety design needed. This is the one item on this whole list that's closer to "a few hours of work" than "a project" — genuinely worth prioritizing first once the core pilot loop is stable, precisely because it demonstrates local agronomic awareness (Chergui heatwaves, frost risk) without adding any new risk surface.

*Keep the Darija-audio delivery mentioned in the original proposal decoupled* — text delivery alone captures the core value; audio delivery for frost alerts should reuse the existing (already-built) TTS teaser infrastructure once that's validated on its own, rather than being bundled into this feature's initial build.

### 3.2 Option B — Bidirectional Voice Notes (Darija Speech-to-Text)

**Tier 3 — sequence last, and design its safety model before writing any code.**

This is not the same scope as the voice-*output* teaser already in the codebase. Voice input means transcribing an incoming Darija voice note into an intent (`1`/`2`/`3`/"update crop") and acting on it — and this is precisely the category of feature the project's constitution was written to keep out of this phase, for good reason:

- **Darija ASR is a genuinely hard, under-resourced problem.** A Whisper checkpoint "fine-tuned on Moroccan Darija" isn't an off-the-shelf integration — sourcing or training a production-quality Darija ASR model is itself a project, with real risk of both dialectal variation and code-switching (French/Darija mixed in the same sentence, which is common) degrading accuracy.
- **Misrecognized intent has a worse failure mode than a text misparse.** Today, an unparseable reply falls through to a safe "here are your options" fallback (Constitution-consistent, no wrong action taken). A misheard voice note could silently transcribe "skip" as "approve" — the system would then confidently act on the wrong intent instead of gracefully asking again. Any voice-input feature needs its own explicit confidence-gated fallback, mirroring the CropDoctor low-confidence pattern (if ASR confidence is low, don't guess — ask Hassan to type 1/2/3 instead), not a bolt-on to the existing regex parser.
- **Recommendation if this is pursued:** scope it explicitly as "voice-to-intent for the three known reply options only, with mandatory human-readable confirmation before any action is logged" — never as open-ended free-form voice command parsing — and treat a failed/low-confidence transcription as functionally identical to today's "unrecognized reply" path, not as a best-guess action.

### 3.3 Option C — Satellite NDVI/NDWI Canopy Heatmap (Sentinel-2)

**Tier 2 — good jury appeal, blocked on a real UX gap, not just engineering.**

Technically approachable — Sentinel-2 10m imagery is free (Copernicus / Google Earth Engine / Sentinel Hub), and NDVI/NDWI computation from it is well-documented, unglamorous engineering. The actual blocker is upstream of the imagery: **today, a farm profile stores a single lat/lon point, not a parcel boundary**, and NDVI-per-pixel needs a boundary polygon to be meaningful (a point tells you nothing about *which* pixels are the farmer's field). Before any satellite integration work, this needs a boundary-collection UX decision — plausibly: ask the farmer to share 3–4 WhatsApp location pins at the corners of their plot during onboarding, store them as a simple polygon. That's a small, real design task in its own right, and should be scoped as its own prerequisite spec before the imagery pipeline is touched.

Delivery is more solved than it looks: the existing `upload_media`/audio-send infrastructure built for the voice teaser already proves out sending binary media to WhatsApp — sending a static NDVI map image reuses that same mechanism (image instead of audio), not a new integration pattern.

**Sequencing note:** because this genuinely showcases UM6P's remote-sensing strengths and requires no new AI/ML risk (it's data pipeline + image generation, not a model), this is a reasonable second priority after the frost-alert feature — but only once the parcel-boundary UX is deliberately designed, not improvised.

---

## 4. Suggested Roadmap Sequencing (Post-Selection)

| Order | Item | Tier | Why here |
|---|---|---|---|
| 1 | Kc-based ETc refinement (Section 1.2) | 1 | Small, correctly-scoped, strengthens a claim you're already making |
| 2 | Frost/heatwave threshold alerts (Section 3.1) | 1 | Reuses existing pipeline entirely, near-zero new risk |
| 3 | CropDoctor quality gate — leaf/blur pre-check (Section 2.2a) | 1–2 | No training data needed, strengthens existing safety behavior |
| 4 | IAV Hassan II ask expanded to include Moroccan disease image sourcing (Section 2.1) | 2 | Unblocks the higher-value vision upgrade; start this conversation early since data sourcing takes calendar time regardless of engineering capacity |
| 5 | Parcel-boundary collection UX + Sentinel-2 NDVI overlay (Section 3.3) | 2 | Real jury appeal, needs its own small spec first |
| 6 | Fine-tuned disease classifier + calibration (Section 2.2b) | 3 | Depends entirely on item 4 landing first |
| 7 | Darija voice-input with confidence-gated fallback (Section 3.2) | 3 | Highest risk, needs its own safety-first spec before any code |

---

## 5. What NOT to do with this document

- Do not let any single item here become a `/speckit.specify` target without first checking it against the active MVP constitution — the pattern that already happened twice (Terraform, voice-output) is exactly what led to the audit findings in this project so far.
- Do not treat "the jury will love this" as sufficient justification on its own — every item above needed a real technical or UX justification beyond novelty, and two of the seven (frost alerts, ETc refinement) are worth doing specifically *because* they're cheap and safe, not because they're impressive.
- Do not start Section 2.2b (fine-tuned classifier) or Section 3.2 (voice input) before their stated dependencies are actually resolved — both are the kind of "looks like a coding task, is actually blocked on something else" work that's easy to start prematurely and hard to finish well.

---

*This document is a planning artifact. It does not authorize implementation of any item within it. Graduating an item to active work means writing it as its own spec, scoped and clarified the same way every prior feature in this project has been.*