"""
ONSSA Phytosanitary Registry Sync Tool.

Extracts Morocco's official ONSSA phytosanitary product index
(eservice.onssa.gov.ma/IndPesticide.aspx) into a structured local dataset
(data/onssa_registry.json) for CropDoctor product recommendation lookups.
"""

import sys
import os
import json
import time
import argparse
import urllib.robotparser
from urllib.parse import urlparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple

import requests
from bs4 import BeautifulSoup

USER_AGENT = "IrrigAgent-ONSSA-Sync/1.0 (+https://github.com/aroucadi/IrrigAgent)"
DEFAULT_TARGET_URL = "https://eservice.onssa.gov.ma/IndPesticide.aspx"
DEFAULT_OUTPUT_FILE = os.path.join("data", "onssa_registry.json")
CHECKPOINT_FILE = os.path.join("data", "onssa_registry.checkpoint.json")


@dataclass
class PhytosanitaryProductEntry:
    id: str
    commercial_name: str
    active_substances: List[str]
    authorized_crops: List[str]
    targeted_pests: List[str]
    dosage: str
    pre_harvest_interval_days: Optional[int]
    max_applications: Optional[int]
    toxicity_class: str
    distributor: str
    homologation_validity_date: str
    source_page: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SyncResult:
    success: bool
    mode: str
    total_entries_parsed: int
    failed_rows: List[Dict[str, Any]]
    output_file: Optional[str]
    elapsed_seconds: float
    error_message: Optional[str] = None


def check_robots_allowed(target_url: str, user_agent: str = USER_AGENT) -> bool:
    """
    Fetches and parses robots.txt from target domain to verify scraping permissions.
    """
    parsed = urlparse(target_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    
    try:
        resp = requests.get(robots_url, headers={"User-Agent": user_agent}, timeout=10)
        if resp.status_code == 200:
            rp.parse(resp.text.splitlines())
            return rp.can_fetch(user_agent, target_url)
        elif resp.status_code in (401, 403):
            return False
        # 404 or other status code means no robots restriction specified
        return True
    except Exception:
        # If robots.txt cannot be fetched due to network issue, assume allowed unless blocked
        return True


def extract_webform_hidden_fields(soup: BeautifulSoup) -> Dict[str, str]:
    """
    Extracts ASP.NET WebForm state tokens (__VIEWSTATE, __EVENTVALIDATION, etc.)
    """
    fields = {}
    for hidden_id in ["__VIEWSTATE", "__EVENTVALIDATION", "__VIEWSTATEGENERATOR", "__EVENTTARGET", "__EVENTARGUMENT"]:
        elem = soup.find("input", {"id": hidden_id})
        if elem and elem.get("value") is not None:
            fields[hidden_id] = elem.get("value", "")
        else:
            elem_name = soup.find("input", {"name": hidden_id})
            if elem_name and elem_name.get("value") is not None:
                fields[hidden_id] = elem_name.get("value", "")
    return fields


def parse_phi_days(raw_text: str) -> Optional[int]:
    """Parses pre-harvest interval days from text string."""
    if not raw_text:
        return None
    cleaned = "".join(c for c in raw_text if c.isdigit())
    if cleaned:
        try:
            return int(cleaned)
        except ValueError:
            return None
    return None


def parse_onssa_table_rows(html_content: str, page_num: int) -> Tuple[List[PhytosanitaryProductEntry], List[Dict[str, Any]], Dict[str, str]]:
    """
    Parses product table rows and WebForm state fields from ONSSA HTML page.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    hidden_fields = extract_webform_hidden_fields(soup)
    
    entries: List[PhytosanitaryProductEntry] = []
    failed_rows: List[Dict[str, Any]] = []

    # Locate GridView or main table containing product data
    tables = soup.find_all("table")
    target_table = None
    for tbl in tables:
        # ONSSA table usually contains product header strings
        text = tbl.text.lower()
        if "commercial" in text or "produit" in text or "substance" in text or "homolog" in text:
            target_table = tbl
            break
            
    if not target_table and tables:
        target_table = tables[0]

    if not target_table:
        return entries, failed_rows, hidden_fields

    rows = target_table.find_all("tr")
    for r_idx, row in enumerate(rows):
        cells = [c.text.strip() for c in row.find_all(["td", "th"])]
        if not cells or len(cells) < 3:
            continue
            
        # Skip header row if identified by text
        header_check = "".join(cells).lower()
        if "nom commercial" in header_check or "substance active" in header_check:
            continue

        try:
            # Flexible cell mapping based on ONSSA GridView column order
            commercial_name = cells[0] if len(cells) > 0 else ""
            if not commercial_name:
                failed_rows.append({
                    "page": page_num,
                    "row_index": r_idx,
                    "raw_text": " | ".join(cells),
                    "error": "Missing commercial name"
                })
                continue

            active_sub = [cells[1]] if len(cells) > 1 and cells[1] else []
            crop = [cells[2]] if len(cells) > 2 and cells[2] else []
            pest = [cells[3]] if len(cells) > 3 and cells[3] else []
            dosage = cells[4] if len(cells) > 4 else ""
            phi_raw = cells[5] if len(cells) > 5 else ""
            max_app_raw = cells[6] if len(cells) > 6 else ""
            toxicity = cells[7] if len(cells) > 7 else ""
            distributor = cells[8] if len(cells) > 8 else ""
            validity = cells[9] if len(cells) > 9 else ""
            entry_id = cells[10] if len(cells) > 10 else f"P{page_num}-R{r_idx}"

            entry = PhytosanitaryProductEntry(
                id=entry_id,
                commercial_name=commercial_name,
                active_substances=active_sub,
                authorized_crops=crop,
                targeted_pests=pest,
                dosage=dosage,
                pre_harvest_interval_days=parse_phi_days(phi_raw),
                max_applications=parse_phi_days(max_app_raw),
                toxicity_class=toxicity,
                distributor=distributor,
                homologation_validity_date=validity,
                source_page=page_num
            )
            entries.append(entry)
        except Exception as e:
            failed_rows.append({
                "page": page_num,
                "row_index": r_idx,
                "raw_text": " | ".join(cells),
                "error": str(e)
            })

    return entries, failed_rows, hidden_fields


def request_with_retry(
    session: requests.Session,
    method: str,
    url: str,
    data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = 3,
    backoff_factor: float = 2.0
) -> requests.Response:
    """Executes HTTP request with exponential backoff retries."""
    for attempt in range(1, max_retries + 1):
        try:
            resp = session.request(method, url, data=data, headers=headers, timeout=15)
            if resp.status_code == 200:
                return resp
            elif resp.status_code in (429, 502, 503, 504):
                if attempt == max_retries:
                    resp.raise_for_status()
            else:
                resp.raise_for_status()
        except (requests.RequestException, Exception) as e:
            if attempt == max_retries:
                raise e
        time.sleep(backoff_factor ** (attempt - 1))
    raise RuntimeError(f"Failed to fetch {url} after {max_retries} retries")


def save_checkpoint(checkpoint_path: str, page_idx: int, entries: List[PhytosanitaryProductEntry], failed_rows: List[Dict[str, Any]]):
    """Saves extraction progress checkpoint to disk."""
    os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
    payload = {
        "extraction_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "last_completed_page": page_idx,
        "accumulated_entries_count": len(entries),
        "failed_rows": failed_rows,
        "entries": [e.to_dict() for e in entries]
    }
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def load_checkpoint(checkpoint_path: str) -> Optional[Dict[str, Any]]:
    """Loads existing extraction checkpoint if present."""
    if os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def clear_checkpoint(checkpoint_path: str):
    """Removes completed checkpoint file."""
    if os.path.exists(checkpoint_path):
        try:
            os.remove(checkpoint_path)
        except OSError:
            pass


def run_sync(
    commit: bool = False,
    limit: Optional[int] = 20,
    delay_seconds: float = 2.5,
    output_file: str = DEFAULT_OUTPUT_FILE,
    resume: bool = True,
    target_url: str = DEFAULT_TARGET_URL
) -> SyncResult:
    """
    Main extraction runner for the ONSSA phytosanitary catalog.
    Supports dry-run (commit=False) and committed persistence (commit=True).
    """
    start_time = time.time()
    mode = "commit" if commit else "dry-run"

    # Step 1: Check robots.txt compliance
    if not check_robots_allowed(target_url):
        err_msg = f"Access to {target_url} is disallowed by site robots.txt policy."
        print(f"ERROR: {err_msg}", file=sys.stderr)
        return SyncResult(
            success=False,
            mode=mode,
            total_entries_parsed=0,
            failed_rows=[],
            output_file=None,
            elapsed_seconds=round(time.time() - start_time, 2),
            error_message=err_msg
        )

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    all_entries: List[PhytosanitaryProductEntry] = []
    failed_rows: List[Dict[str, Any]] = []
    start_page = 1

    # Check for resume checkpoint in commit mode
    if commit and resume:
        checkpoint = load_checkpoint(CHECKPOINT_FILE)
        if checkpoint:
            start_page = checkpoint.get("last_completed_page", 0) + 1
            raw_entries = checkpoint.get("entries", [])
            for re in raw_entries:
                all_entries.append(PhytosanitaryProductEntry(**re))
            failed_rows = checkpoint.get("failed_rows", [])
            print(f"Resuming sync from checkpoint at page {start_page} ({len(all_entries)} entries loaded)")

    current_page = start_page
    current_hidden_fields: Dict[str, str] = {}

    try:
        # Initial GET request for page 1
        resp = request_with_retry(session, "GET", target_url)
        page_entries, page_failed, current_hidden_fields = parse_onssa_table_rows(resp.text, page_num=1)
        
        if start_page == 1:
            all_entries.extend(page_entries)
            failed_rows.extend(page_failed)

        # Pagination loop if limit permits further requests
        max_entries_to_fetch = limit if (limit is not None and limit > 0) else float("inf")
        
        while len(all_entries) < max_entries_to_fetch:
            current_page += 1
            time.sleep(delay_seconds)

            # Construct WebForms postback payload for next page
            post_data = {
                "__VIEWSTATE": current_hidden_fields.get("__VIEWSTATE", ""),
                "__EVENTVALIDATION": current_hidden_fields.get("__EVENTVALIDATION", ""),
                "__VIEWSTATEGENERATOR": current_hidden_fields.get("__VIEWSTATEGENERATOR", ""),
                "__EVENTTARGET": current_hidden_fields.get("__EVENTTARGET", f"GridView1$ctl00$ctl02$ctl00$PageButton{current_page}"),
                "__EVENTARGUMENT": current_hidden_fields.get("__EVENTARGUMENT", "")
            }

            try:
                post_resp = request_with_retry(session, "POST", target_url, data=post_data)
                p_entries, p_failed, current_hidden_fields = parse_onssa_table_rows(post_resp.text, page_num=current_page)
                
                if not p_entries and not p_failed:
                    # No more entries returned; reached last page
                    break

                all_entries.extend(p_entries)
                failed_rows.extend(p_failed)

                # Periodically checkpoint progress during commit runs
                if commit and (current_page % 5 == 0):
                    save_checkpoint(CHECKPOINT_FILE, current_page, all_entries, failed_rows)

            except Exception as page_err:
                print(f"Warning: Failed to fetch page {current_page}: {page_err}", file=sys.stderr)
                break

    except Exception as fatal_err:
        err_msg = f"Sync failed during execution: {str(fatal_err)}"
        print(f"ERROR: {err_msg}", file=sys.stderr)
        return SyncResult(
            success=False,
            mode=mode,
            total_entries_parsed=len(all_entries),
            failed_rows=failed_rows,
            output_file=None,
            elapsed_seconds=round(time.time() - start_time, 2),
            error_message=err_msg
        )

    # Trim entries to explicit limit if set
    if limit is not None and limit > 0:
        all_entries = all_entries[:limit]

    elapsed = round(time.time() - start_time, 2)

    # If commit mode, write output dataset file and clear checkpoint
    output_path_written: Optional[str] = None
    if commit:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        final_payload = {
            "_metadata": {
                "extraction_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "source_url": target_url,
                "mode": mode,
                "total_entries": len(all_entries),
                "user_agent": USER_AGENT,
                "failed_rows_count": len(failed_rows),
                "failed_rows": failed_rows
            },
            "entries": [e.to_dict() for e in all_entries]
        }
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_payload, f, ensure_ascii=False, indent=2)
        output_path_written = output_file
        clear_checkpoint(CHECKPOINT_FILE)

    # Print human-readable summary to stdout
    print(f"\n--- ONSSA Sync Execution Summary ({mode.upper()}) ---")
    print(f"Total Entries Parsed : {len(all_entries)}")
    print(f"Failed Rows Count    : {len(failed_rows)}")
    print(f"Elapsed Time         : {elapsed} seconds")
    if output_path_written:
        print(f"Output Dataset File  : {output_path_written}")
    else:
        print("Output Dataset File  : None (Dry-run mode - zero files written)")
    print("---------------------------------------------------\n")

    return SyncResult(
        success=True,
        mode=mode,
        total_entries_parsed=len(all_entries),
        failed_rows=failed_rows,
        output_file=output_path_written,
        elapsed_seconds=elapsed
    )


def main():
    parser = argparse.ArgumentParser(description="ONSSA Phytosanitary Registry Sync Tool")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Default dry-run mode (no file written)")
    parser.add_argument("--commit", action="store_true", help="Persist dataset to output file")
    parser.add_argument("--limit", type=int, default=20, help="Cap number of entries extracted (default: 20 for dry-run)")
    parser.add_argument("--delay", type=float, default=2.5, help="Politeness delay between requests in seconds (default: 2.5)")
    parser.add_argument("--output-file", type=str, default=DEFAULT_OUTPUT_FILE, help="Path for committed output dataset")
    parser.add_argument("--no-resume", action="store_true", help="Disable checkpoint resume for commit mode")

    args = parser.parse_args()

    # If --commit is explicitly passed, disable dry-run
    commit_mode = args.commit
    limit_val = args.limit
    if commit_mode and args.limit == 20 and "--limit" not in sys.argv:
        # If commit mode without explicit --limit flag, pull full registry
        limit_val = None

    result = run_sync(
        commit=commit_mode,
        limit=limit_val,
        delay_seconds=args.delay,
        output_file=args.output_file,
        resume=not args.no_resume
    )

    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    main()
