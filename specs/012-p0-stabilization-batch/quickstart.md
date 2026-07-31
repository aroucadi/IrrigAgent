# Quickstart Validation Guide: P0 Stabilization Batch

## Purpose

Validate end-to-end correctness of the P0 stabilization batch fixes (BUG-001 real voice transcription, BUG-003 Option A Terraform scope deletion, and BUG-004 spec status accuracy).

---

## Runnable Verification Steps

### Step 1: Execute Anti-Mock Voice STT & Full Test Suite

Run the full pytest suite to verify that the anti-mock regression test and all existing unit tests pass:

```bash
pytest tests/unit/test_voice_darija_stt.py -v
pytest tests/
```

**Expected Outcome**:
- `test_voice_darija_stt.py` passes 100%, including the anti-mock test verifying dynamic Gemini ASR responses.
- Overall pytest suite executes with a 100% pass rate and 0 broken tests.

---

### Step 2: Verify Terraform / IaC Scope Deletion (Option A)

Verify that `infra/*.tf` files have been removed from the active build:

```powershell
# In PowerShell (Windows):
Get-ChildItem -Path infra -Filter *.tf -ErrorAction SilentlyContinue
```

**Expected Outcome**:
- Zero `.tf` files found under `infra/`.
- `.specify/memory/constitution.md` Section VII contains the ratified Option A IaC deferral policy.
- No `README.md` or report file lists deferred HCL files as completed metrics.

---

### Step 3: Verify Spec Metadata Status Accuracy

Verify header statuses across spec files:

```powershell
Select-String -Path "specs\*\spec.md" -Pattern "Status:"
```

**Expected Outcome**:
- Specs 001, 002, 003, 005, 006, 007 display `Status: Implemented`.
- Spec 004 displays `Status: Implemented`.
- Spec 008 displays `Status: Blocked` (pending spec 011 real-imagery merge).
- Spec 009 displays `Status: Blocked` (pending spec 012 completion).
