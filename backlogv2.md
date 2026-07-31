# IrrigAgent AI — Product Backlog & Roadmap

**Last updated:** 2026-07-31 (post deep-audit of `main` @ `087f05c`)
**Source:** Reconciled from hands-on codebase audit + real test suite execution (152/152 passing) + prior `analysis_results.md` report
**How to read this:** Items are grouped by release horizon, not by when they were requested. 🔴 items block trusting anything else in this document or demoing the product live. Resolved items are kept visible with their resolution noted — deleting history is how the same bug gets reintroduced a third time.

---

## 🔴 P0 — Fix Before Any Demo or Real Pilot Use

### CRIT-005: Daily proactive advisory likely violates WhatsApp's 24-hour messaging window (NEW — highest priority)
**File:** `app/whatsapp.py`, `send_text_message()`
**Severity:** Critical — may invalidate the core hero feature outside active testing
**What's wrong:** `send_text_message()` always sends `"type": "text"` free-form messages. Meta's Cloud API only permits free-form business-initiated messages within 24 hours of the user's last inbound message; outside that window, only pre-approved Message Templates are allowed (Meta error `131026`). The daily evening advisory is an unprompted, business-initiated message sent regardless of whether the farmer replied yesterday — the exact case this policy restricts.
**Why it's dangerous:** This will not surface during active development (constant back-and-forth testing keeps the window open) — only when a real farmer trusts the system enough to stop replying every single night, which is normal and desirable usage. It could silently stop working mid-pilot with no obvious cause.
**Immediate action:** Verify directly against a real number: message the sandbox bot once, then wait 25+ hours without sending anything else, then trigger the daily job and check for a `131026` error.
**Fix (if confirmed):** Convert the daily advisory to a Meta-approved Utility-category Message Template with parameterized placeholders. Requires submitting for Meta approval — has real calendar lead time (hours to days), start this immediately, don't discover it during pilot week.

### CRIT-006: App cannot boot from a clean install — missing dependency
**File:** `requirements.txt`
**Severity:** Critical, trivial to fix
**What's wrong:** `app/main.py`'s `/cropdoctor/prefilter` endpoint uses `UploadFile = File(...)`, which requires `python-multipart`. It's missing from `requirements.txt`. Verified directly — a clean `pip install -r requirements.txt` followed by running the app/tests fails immediately.
**Fix:** Add `python-multipart` to `requirements.txt`. Five minutes; blocks everything downstream including the Docker build.

### CRIT-007: Mock media IDs are reachable as silent production fallbacks
**File:** `app/main.py` (webhook handler), `app/whatsapp.py` (`download_media`)
**Severity:** Critical
**What's wrong:** `download_media()` correctly special-cases `media_id.startswith("mock_")` to return canned test bytes — reasonable in isolation. But `main.py` itself constructs `image_id or "mock_img_1"` and `audio_id or "mock_audio_1"` as production fallback values when extraction returns nothing. If `extract_incoming_message()` ever fails to populate a real ID for a genuine incoming photo/voice note (payload parsing edge case, future WhatsApp API shape change), the system won't error — it silently processes the real user's message as if it were the canned test fixture.
**Fix:** These fallbacks must raise/log an explicit error instead of defaulting to a string the media layer treats specially. No production code path should ever be able to construct a value that a mock-detection check would match.

---

## 🟢 P0 (Previous Round) — Verified Genuinely Resolved

Kept visible with verification notes, not deleted — this is the second time mocked/fabricated data was found in this project, and the record of what actually got fixed (and how it was verified) is worth preserving.

### BUG-001: Voice-to-Intent ASR — ✅ RESOLVED, verified real
`parse_voice_intent()` now makes an actual Gemini 1.5 Flash audio call via the `google.genai` SDK, with correct fail-closed degradation on API failure. Verified by reading the implementation directly, not by trusting a "tests passed" claim. One minor bug remains inside this fix — see SMELL-001 below.

### BUG-002: Sentinel canopy heatmap — ✅ RESOLVED, verified real
Real Element84 → Copernicus STAC catalog fallback chain, real `rasterio`/`vsicurl` windowed reads against actual Sentinel-2 COG band data, real NDVI from real pixels. `np.random.seed` and all synthetic generation confirmed removed. One correctness risk remains in shape-mismatch handling — see SMELL-002 below.

### BUG-003: Terraform/IaC scope — ✅ RESOLVED
Option A (full deletion) executed. `infra/` directory confirmed absent from the repo. Recorded here explicitly because this is the third time this exact scope item was raised — if it reappears a fourth time, that's a process problem worth escalating beyond a backlog note.

### BUG-004: Spec status accuracy — ⚠️ NOT RE-VERIFIED THIS ROUND
Was scoped in spec 012. Not directly re-checked in this audit pass — verify spec.md headers directly before assuming this is closed.

---

## 🟡 P1 — Real UX Gaps for the Actual User (Illiterate/Low-Literacy Moroccan Farmer)

These came out of walking the full customer journey against the persona this product is explicitly built for, not from a features checklist. Several represent scope drift that quietly undermined the project's own founding "zero-friction" design principle.

### UX-001: No WhatsApp interactive buttons anywhere — highest-leverage single fix available
**Severity:** High
**What's wrong:** The entire 1/2/3 reply loop, and even voice-intent confirmation, require the farmer to type a digit or word. WhatsApp Cloud API natively supports tappable interactive reply buttons (up to 3 per message) — confirmed via direct search, zero usage anywhere in this codebase.
**Why it matters:** This is the one part of the daily journey every farmer touches every day. Converting it to tap-buttons removes the typing/literacy requirement from the hero loop entirely, and as a side benefit eliminates the regex-parsing surface for the core three options — a tap returns a clean button ID, not free text needing interpretation.
**Recommendation:** Prioritize this above UX-002/UX-003 below — it's the change that touches the most farmer-interactions per day.

### UX-002: Parcel/heatmap/profile features reintroduce the literacy barrier the core loop avoided
**Severity:** High
**What's wrong:** `/parcel`, `DONE`, `/heatmap`, `update crop tomatoes` — all typed Latin-script English commands. For a farmer who can't read/write Latin script, these features are as inaccessible as a dashboard would have been. This is real scope drift: each feature was reasonable in isolation, the aggregate undermined the WhatsApp-native premise.
**Recommendation:** At minimum, offer these as tap-button menu options reachable from a `help` command (see UX-003) rather than requiring the exact command string to be typed from memory.

### UX-003: No help/menu command exists
**Severity:** Medium-High
**What's wrong:** Confirmed via direct search — zero matches for any help/menu command anywhere in the codebase. A confused farmer has no way to rediscover what the bot can do short of waiting for tomorrow's message.
**Fix:** A simple, always-available command (ideally also a persistent button) listing capabilities in the farmer's preferred language.

### UX-004: No opt-out/unsubscribe mechanism
**Severity:** Medium
**What's wrong:** No in-product way to stop the daily messages. Also worth checking against WhatsApp Business policy expectations around honoring user opt-outs, not just a UX nicety.

### UX-005: Onboarding silently defaults every new farmer to Agadir coordinates, tomatoes, 10 hectares
**Severity:** Medium-High
**What's wrong:** `main.py`'s new-user path hardcodes these values with zero prompt or confirmation, and the bilingual greeting never mentions defaults were assumed. Every recommendation for a farmer who doesn't know to type `update crop X` / `update area Y` is computed against the wrong location's weather and the wrong crop's Kc curve — a correctness problem, not just a UX one.
**Fix:** Either prompt for real values at onboarding (even simply: "share your location pin"), or at minimum tell the farmer explicitly what was assumed and how to correct it, in the first message.

---

## 🟡 P1 — Code Quality (Real but Lower Severity)

### SMELL-001: Fragile JSON extraction in the (now-real) ASR parser
**File:** `app/decision.py`, inside `parse_voice_intent()`
`response.text.strip().strip("```json").strip("```")` uses `str.strip()`, which removes arbitrary characters in that set from both ends — not the literal prefix/suffix string. Works by coincidence on typical model output. Replace with `removeprefix`/`removesuffix`.

### SMELL-002: `np.resize` can silently misalign Red/NIR pixels on shape mismatch
**File:** `app/sentinel.py`, `fetch_sentinel2_bands()`
If windowed reads of the Red and NIR bands return different shapes, `np.resize` wraps/repeats a flattened buffer rather than spatially realigning data — this could corrupt NDVI values without erroring. Pass `out_shape` to the `rasterio` read call instead to force consistent dimensions correctly.

### SMELL-003: Unnecessary `importlib.import_module` indirection
**File:** `app/decision.py`, inside `parse_voice_intent()`
`google.genai` is already a hard dependency in `requirements.txt` — importing it via `importlib.import_module` instead of a normal import obscures the dependency from static analysis and tooling for no runtime benefit. Low priority, easy cleanup.

---

## MVP+ — Immediate Post-Selection (v1.0)

### V1-001: ONSSA live registry as CropDoctor's primary source
**Status:** Likely implemented — `data/onssa_registry.json` exists (60KB) and spec 005/014 tasks are present in-repo. **Not independently re-verified this round** — confirm the fallback chain (dynamic dataset → static table → None) behaves correctly with a live test before trusting it in a demo.

### V1-002: Frost/heatwave threshold alerts
**Status:** Not verified this round — check whether this shipped; it wasn't part of this audit's focus area. Still cheap to build if not (reuses the existing weather/scheduler/WhatsApp pipeline entirely).

### V1-003: Parcel boundary collection UX hardening
**Status:** Partially confirmed — pin collection state machine (`/parcel`, pin recording, `DONE`, `/cancel`) exists and is wired into `main.py`. Whether the specific invalid-input cases (too few pins, near-duplicate pins, self-intersecting polygon) are all handled wasn't individually re-verified this round.

### V1-004: Post-selection Terraform/IaC authoring
**Status:** Correctly not started. Gate condition (confirmed StartGate selection) unmet — do not begin.

---

## v2 — Medium-Term (Data- or Validation-Dependent)

Unchanged from prior backlog — no new findings against these this round.

### V2-001: Fine-tuned CropDoctor disease classifier
Blocked on IAV Hassan II providing/sourcing labeled Moroccan leaf-disease images. `scripts/ingest_iav_dataset.py`'s gated-waiting design remains correct and honest — verify it's still gated, not silently bypassed.

### V2-002: IoT soil-moisture monitoring (read-only)
Still a reasonable v2 candidate once a pilot cooperative is willing to pilot hardware. No change.

### V2-003: Farmer-to-farmer same-area disease alerts
Still legitimately differentiated — needs a confidence/verification gate before fan-out and explicit farmer opt-in consent.

### V2-004: Authority (ONSSA/extension services) integration
Still a partnership/liability conversation before an engineering one.

### V2-005: Regional analytics/farmer clustering
Still data aggregation, not "AI clustering" — keep the honest framing.

---

## v3 — Longer-Term / Strategic

### V3-001: IoT command / autonomous valve control
**Still not a normal backlog item.** Given this round found a second instance of mocked/fabricated data reaching production paths (this time via the mock-ID fallback in CRIT-007), the bar for trusting any autonomous actuation feature is, if anything, higher than when this was first flagged. Requires its own constitution amendment and sign-off, not a standard spec pass.

### V3-002: Multi-crop expansion beyond tomatoes/citrus
Unchanged — depends on V1-001 and V2-001 both being real and validated first.

---

## Parking Lot — Explicitly Not Scheduled

- **Starlink/satellite ISP integration** — not a product feature, design for graceful degradation instead.
- **GPS "exploitation" as a standalone feature** — substrate for V2-003/004/005, not its own feature.

---

## Process Notes (Constitution Candidates)

Two rules now, given this round's findings:

> **Rule 1 (existing):** No feature may be marked "Completed & Verified" if its core external API/model call has a hardcoded or synthetic default path reachable in production. Every completion claim must include a test that fails when realistic (non-fixture) input hits that path with the mock still in place.

> **Rule 2 (new, from CRIT-007):** No function may construct a fallback/default value that coincides with a string another function in the codebase treats as a test-mode or mock-mode signal. If a real value is missing at runtime, fail loudly (log/error), never silently substitute a value that happens to match a test-detection pattern.

Both rules would have caught issues found in this and the prior audit round before they were merged.