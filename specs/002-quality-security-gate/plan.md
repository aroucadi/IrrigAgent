# Implementation Plan: Quality & Security Gate Module

**Branch**: `002-quality-security-gate` | **Date**: 2026-07-28 | **Spec**: [spec.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/spec.md)

**Input**: Feature specification from `/specs/002-quality-security-gate/spec.md`

## Summary

Implement a dedicated Quality & Security Gate module for IrrigAgent using Git pre-commit hooks (`scripts/pre-commit.sh`, installed to `.git/hooks/pre-commit` via `scripts/install-hooks.sh`) and an expanded Pytest suite (`tests/unit/test_regex_parser.py`, `tests/integration/test_webhook.py`). The gate automatically executes Secret Scanning, Code Linting & Formatting, and Fast Unit Tests on every commit, preventing security token leaks or regressions with sub-3.0 second execution time.

## Technical Context

**Language/Version**: Python 3.11+, POSIX Shell (`sh`/`bash`)

**Primary Dependencies**: `pytest`, `ruff`, `black`, `FastAPI` (with `httpx`/`TestClient`)

**Storage**: N/A (Firestore mocked during test suite execution)

**Testing**: `pytest` (`pytest tests/unit/ -v`)

**Target Platform**: Linux, macOS, Windows (Git Bash / WSL shell environment)

**Project Type**: Developer tooling & web service test suite

**Performance Goals**: Pre-commit hook execution time < 3.0 seconds (SC-010)

**Constraints**: Abort git commit with exit code 1 if secrets, linting, or unit tests fail (SC-009)

**Scale/Scope**: Repository pre-commit hook scripts and test suite enhancements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Human-in-the-Loop Only**: Pass (no hardware control or automated actions).
- **Rule-Based First Logic**: Pass (deterministic regex parser and shell scripts).
- **Mandatory ONSSA Regulatory Disclaimer**: Pass (no changes to ONSSA disclaimer logic).
- **WhatsApp Cloud API Sandbox Tier Only**: Pass (external APIs mocked in tests).
- **Strict Scope Boundary & Cut List Enforcement**: Pass (no cut list features introduced).
- **Infrastructure as Code**: Pass (scripted developer tooling).

## Project Structure

### Documentation (this feature)

```text
specs/002-quality-security-gate/
├── spec.md              # Feature specification
├── plan.md              # Implementation plan (this file)
├── research.md          # Technical decisions & research
├── data-model.md        # Architecture & component layout
├── quickstart.md        # Quickstart & verification guide
├── contracts/           # Interface definitions
│   └── git-hook-interface.md
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code & Test Layout

```text
scripts/
├── pre-commit.sh        # Versioned git pre-commit hook script
└── install-hooks.sh     # One-touch developer hook setup script

.git/hooks/
└── pre-commit          # Executable hook (installed copy of scripts/pre-commit.sh)

tests/
├── unit/
│   ├── test_regex_parser.py      # Expanded regex parser unit tests (options 1, 2, 3)
│   ├── test_decision.py
│   ├── test_cropdoctor.py
│   ├── test_weather.py
│   ├── test_firestore_client.py
│   └── test_tts_voice.py
└── integration/
    └── test_webhook.py           # FastAPI webhook endpoint integration tests
```

## Generated Design Artifacts

- [research.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/research.md) - Research & technical decisions
- [data-model.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/data-model.md) - Gate component layout and stage specifications
- [git-hook-interface.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/contracts/git-hook-interface.md) - Interface contracts
- [quickstart.md](file:///d:/rouca/DVM/workPlace/IrrigAgent/specs/002-quality-security-gate/quickstart.md) - Verification guide
