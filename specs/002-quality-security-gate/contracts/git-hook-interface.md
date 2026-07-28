# Interface Contract: Git Pre-Commit Hook & Installation Script

## Interface 1: `.git/hooks/pre-commit` Execution Contract

### Invocation
Triggered automatically by Git prior to completing any `git commit` command.

### Environment Requirements
- POSIX shell compatibility (`/bin/sh` or `/usr/bin/env bash`).
- Access to `git`, `python`, `pytest`, `ruff`, `black` in PATH.

### Exit Codes & Terminal Behavior
- **Exit Code 0 (Success)**:
  - Prints stage success markers with green checkmarks `[✓]`.
  - Git commit proceeds cleanly.
- **Exit Code 1 (Failure)**:
  - Prints failure indicator `[✗]` and detailed error diagnostics.
  - Aborts the `git commit` command immediately (SC-009).

---

## Interface 2: `scripts/install-hooks.sh` Setup Contract

### Invocation
Executed by developers from repository root: `bash scripts/install-hooks.sh` or `./scripts/install-hooks.sh`.

### Behavior
1. Checks for `.git` directory presence.
2. Copies `scripts/pre-commit.sh` to `.git/hooks/pre-commit`.
3. Grants executable permissions (`chmod +x .git/hooks/pre-commit`).
4. Emits confirmation output in terminal.
