# Interface Contract: Gemini 1.5 Flash Audio ASR (`parse_voice_intent`)

## Function Signature

```python
async def parse_voice_intent(
    audio_bytes: bytes,
    duration_seconds: int = 0
) -> Tuple[float, str, Optional[Dict[str, Any]]]:
```

## Contract Rules

### 1. Duration Bounding
- **Condition**: `duration_seconds > 60`
- **Return**: `(0.0, "AUDIO_TOO_LONG", None)`
- **Behavior**: Short-circuits immediately without calling external ASR service.

### 2. Test Fixture Bypass
- **Condition**: `audio_bytes in (b"fake_low_confidence", b"garbled")`
- **Return**: `(0.65, "Sqi m3a 5h hhh...", None)`
- **Behavior**: Reserved for deterministic unit testing of low-confidence text fallback menus without requiring mocked external SDK wrappers.

### 3. Real Audio Processing via Vertex AI SDK
- **Input Payload**: Raw `.ogg` (opus) audio bytes sent to Gemini 1.5 Flash.
- **Model Target**: `gemini-1.5-flash`
- **System Instruction**: Constrain output strictly to JSON schema:
  ```json
  {
    "transcribed_text": "<transcription_string>",
    "confidence_score": 0.88,
    "intent_type": "MODIFY_IRRIGATION",
    "proposed_adjustment_minutes": 15
  }
  ```
- **High-Confidence Threshold ($\ge 0.80$)**:
  - Return: `(confidence_score, transcribed_text, {"intent_type": intent_type, "proposed_adjustment_minutes": mins})`
  - Downstream (`process_voice_note`): Stores pending intent in Firestore and returns confirmation prompt with reply choices `1` (Confirm), `2` (Cancel), `3` (Discard).

### 4. API Exception / Timeout / Low Confidence Degradation
- **Condition**: Vertex AI SDK raises exception, returns non-200 status, returns malformed JSON, or computes `confidence_score < 0.80`.
- **Return**: `(confidence_score, transcribed_text, None)` (or `(0.0, "ASR_FAILURE", None)` on exception).
- **Downstream (`process_voice_note`)**: Degrades cleanly to standard text menu fallback (*"I couldn't hear clearly. Please reply: 1 - Approve (+15 min), 2 - Skip today, 3 - Modify"*). Zero pending intent written to Firestore.

### 5. Anti-Mock Regression Rule
- Unit tests mocking the Vertex AI SDK client MUST prove that two distinct audio inputs (e.g. `mock_audio_input_a` and `mock_audio_input_b`) produce distinct transcripts or confidence scores.
- A hardcoded return value for non-fixture audio inputs MUST cause this unit test to fail.
