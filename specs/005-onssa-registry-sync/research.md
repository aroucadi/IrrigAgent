# Phase 0 Research: ONSSA Phytosanitary Registry Sync Tool

**Branch**: `005-onssa-registry-sync` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/005-onssa-registry-sync/spec.md)

## Research Findings & Architecture Decisions

### 1. Target Site WebForms Scraping Mechanics (ASP.NET)

* **Context**: `eservice.onssa.gov.ma/IndPesticide.aspx` uses ASP.NET WebForms with server-side controls and state hidden fields (`__VIEWSTATE`, `__EVENTVALIDATION`, `__VIEWSTATEGENERATOR`).
* **Decision**: Use `requests.Session` paired with `BeautifulSoup` (`bs4`).
* **Rationale**: `requests.Session` automatically handles HTTP cookies across postback requests. `BeautifulSoup` enables easy extraction of `__VIEWSTATE` and table row elements.
* **Postback Flow**:
  1. `GET /IndPesticide.aspx` → Extract initial `__VIEWSTATE`, `__EVENTVALIDATION`, `__VIEWSTATEGENERATOR`.
  2. `POST /IndPesticide.aspx` with `__EVENTTARGET` set to the next page button / grid view page event, including updated state tokens from the prior response.
* **Alternatives Considered**:
  * *Playwright/Selenium*: Rejected because headless browser engines add heavy dependencies and memory overhead. HTTP session postback requests are vastly faster and lighter.

---

### 2. Politeness & Compliance Engine (`robots.txt` & Throttling)

* **Decision**: Use standard library `urllib.robotparser.RobotFileParser` alongside explicit `time.sleep(delay)` throttling.
* **User-Agent String**: `"IrrigAgent-ONSSA-Sync/1.0 (+https://github.com/aroucadi/IrrigAgent)"`
* **Politeness Delay**: Configurable default of 2.5 seconds (within 2-3s range specified in requirement FR-005). Single-threaded sequential requests only.
* **Rationale**: Guarantees zero denial-of-service or rate-limiting impact on ONSSA servers while honoring standard site crawl policies.

---

### 3. Resilience, Retries & Checkpointing Strategy

* **Decision**: File-based checkpointing at `data/onssa_registry.checkpoint.json`.
* **State Tracked**:
  * `last_completed_page`: integer index of last fully extracted page.
  * `entries`: array of extracted product dictionaries.
  * `failed_rows`: array of unparsed/malformed row objects with page number and raw text.
* **Retry Strategy**: Exponential backoff with `urllib3` / `requests` retry adapter or explicit loop retry (up to 3 retries per page with delays 2s, 4s, 8s).
* **Rationale**: A full sync (~470 pages x 2.5s = ~20 minutes) can be safely interrupted and resumed without lost progress or duplicate page requests.

---

### 4. CropDoctor Dataset Runtime Integration & Fallback

* **Decision**: Encapsulate catalog retrieval in `app/cropdoctor.py` via a thread-safe / cached loader function `_load_onssa_catalog()`.
* **Flow**:
  1. Check if `data/onssa_registry.json` exists on disk.
  2. If present, load and parse JSON entries into lookup indexing map (by active substance & authorized crop).
  3. If missing, corrupted, or empty, log a warning and return `ONSSA_STATIC_CATALOG`.
* **Rationale**: Maintains zero downtime and zero risk for CropDoctor triage even if dataset file is absent or undergoing updates.
