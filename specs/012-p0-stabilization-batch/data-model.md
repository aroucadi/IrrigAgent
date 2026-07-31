# Data Model: P0 Stabilization Batch Entities & Contracts

## Entities & Data Structures

### 1. VoiceIntentResult Tuple & Action Payload Schema

The `parse_voice_intent()` function returns a 3-element tuple:

```python
Tuple[float, str, Optional[Dict[str, Any]]]
```

#### Fields

| Field Name | Type | Description | Validation Rules |
|------------|------|-------------|------------------|
| `confidence_score` | `float` | Model confidence in transcription & intent parsing | Range `[0.0, 1.0]`. If $< 0.80$, downstream flow degrades to text fallback. |
| `transcribed_text` | `str` | Plain text Darija/French transcription of audio | Max 500 chars. On failure: `"ASR_FAILURE"`. On cap exceed: `"AUDIO_TOO_LONG"`. |
| `parsed_action` | `Optional[Dict[str, Any]]` | Structured action dictionary extracted from audio | Must contain `intent_type` and `proposed_adjustment_minutes` if confidence $\ge 0.80$. |

#### Action Dictionary Schema (`parsed_action`)

```json
{
  "intent_type": "MODIFY_IRRIGATION",
  "proposed_adjustment_minutes": 15
}
```

- **`intent_type` Enum**: `["MODIFY_IRRIGATION", "INCREASE_IRRIGATION", "DECREASE_IRRIGATION", "SKIP_IRRIGATION"]`
- **`proposed_adjustment_minutes`**: Signed integer representing time delta in minutes (e.g., `15`, `-10`, `0`).

---

### 2. Specification Metadata Header (`SpecHeaderMetadata`)

Located at the top of each `specs/NNN-*/spec.md` file:

```markdown
# Feature Specification: [Title]

**Feature Branch**: `[branch-name]`

**Created**: YYYY-MM-DD

**Status**: [Draft | Implemented | Blocked | In Progress]
```

#### Allowed Status Values

- **`Implemented`**: Feature is verified 100% complete with passing automated tests and no open P0 backlog bugs against it.
- **`Blocked`**: Feature cannot be marked implemented due to an open P0 bug or unmerged dependency spec.
- **`In Progress`**: Active development underway.
- **`Draft`**: Newly generated spec awaiting planning or implementation.

---

### 3. Constitution IaC Policy Clause (`ConstitutionIaCPolicy`)

Updated governance clause in `.specify/memory/constitution.md` under Section VII:

```markdown
### VII. Infrastructure Management (Pilot Deployment)
All v1 pilot application deployments MUST use GCP Cloud Run CLI (`gcloud run deploy`) per PRD Section 15.11. Declarative Infrastructure as Code (`infra/*.tf`) is deferred for post-selection environment scaling and is removed from the active build to eliminate scope drift and false metrics reporting.
```
