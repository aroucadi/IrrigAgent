# Phase 1 Interface Contracts: ONSSA Registry Sync & CropDoctor Integration

**Branch**: `005-onssa-registry-sync` | **Date**: 2026-07-29 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/005-onssa-registry-sync/spec.md)

## 1. Command-Line Interface (CLI Contract)

### Usage

```bash
python scripts/sync_onssa_registry.py [OPTIONS]
```

### Options & Arguments

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--dry-run` | `flag` | `True` (default) | Run extraction without persisting to `data/onssa_registry.json`. Output to stdout. |
| `--commit` | `flag` | `False` | Execute full extraction and write results to `data/onssa_registry.json`. |
| `--limit N` | `integer` | `20` (dry-run) / `None` (commit) | Cap maximum entries/pages extracted. |
| `--delay S` | `float` | `2.5` | Politeness delay between sequential HTTP requests in seconds. |
| `--output-file PATH`| `string` | `data/onssa_registry.json` | Custom output path for committed JSON file. |
| `--resume / --no-resume` | `flag` | `True` | Resume commit run from existing checkpoint file if present. |

### Exit Codes

* `0`: Extraction completed successfully (or dry-run complete).
* `1`: `robots.txt` disallows access to target path.
* `2`: Invalid CLI parameters or options.
* `3`: Fatal network or parsing failure (partial checkpoint persisted).

---

## 2. Python Module API Contract (`scripts/sync_onssa_registry.py`)

Exposed importable functions for future scheduled execution (e.g., Cloud Run Job / Cron).

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class SyncResult:
    success: bool
    mode: str  # "dry-run" or "commit"
    total_entries_parsed: int
    failed_rows: List[Dict[str, Any]]
    output_file: Optional[str]
    elapsed_seconds: float
    error_message: Optional[str] = None

def run_sync(
    commit: bool = False,
    limit: Optional[int] = 20,
    delay_seconds: float = 2.5,
    output_file: str = "data/onssa_registry.json",
    resume: bool = True
) -> SyncResult:
    """
    Core entrypoint function for extracting the ONSSA phytosanitary catalog.
    
    Can be called programmatically by a scheduler or CLI wrapper.
    """
    ...
```

---

## 3. CropDoctor Integration Contract (`app/cropdoctor.py`)

Function contract for retrieving authorized product recommendations within CropDoctor triage.

```python
def get_onssa_treatments(crop: str, pathogen_or_pest: str) -> List[Dict[str, Any]]:
    """
    Returns authorized treatment products for a given crop and pest.
    
    Reads from data/onssa_registry.json if available.
    Falls back to ONSSA_STATIC_CATALOG if dataset file is absent or corrupted.
    """
    ...
```
