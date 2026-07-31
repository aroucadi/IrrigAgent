# Test Suite Interface & Assertion Contracts: MVP Polish — WhatsApp Client Unit Tests & Multi-Farm Batch Integration Test

**Feature Branch**: `013-mvp-polish-whatsapp-batch-tests`  
**Date**: 2026-07-31  

---

## 1. Unit Test Assertions Contract (`tests/unit/test_whatsapp.py`)

### Target Functions Tested
- `send_text_message(to: str, body: str) -> Dict[str, Any]`
- `upload_media(file_bytes: bytes, mime_type: str, filename: str) -> str`
- `extract_incoming_message(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]`

### Test Suite Contract Criteria

```python
# Unit Test Assertions Matrix
def test_send_text_message_success():
    """Asserts URL, Headers (Bearer Token), JSON Payload, and 200 Response parsing."""

def test_send_text_message_http_error():
    """Asserts raise_for_status() HTTP 400/500 error exception handling."""

def test_upload_media_success():
    """Asserts multipart form construction, media headers, and media ID extraction."""

def test_upload_media_http_error():
    """Asserts HTTP status error handling when media upload fails."""

def test_extract_incoming_message_text_image_audio():
    """Asserts parsing of incoming text, image, and voice webhook payloads."""

def test_extract_incoming_message_non_message_and_malformed():
    """Asserts status callbacks and malformed payloads return None safely."""
```

---

## 2. Integration Test Contract (`tests/integration/test_daily_batch_multi_farm.py`)

### Endpoint Contract Tested
`POST /jobs/daily-recommendations`  
Header: `Authorization: Bearer <JOB_SECRET_TOKEN>`

### Expected Response Contract (`DailyAdvisoryJobResponse`)
```json
{
  "status": "success",
  "processed_count": 2,
  "skipped_count": 0,
  "dispatched_count": 2,
  "failed_count": 0
}
```

### Fault Isolation Contract Scenario
When Farm A weather lookup fails and Farm B weather lookup succeeds:
- `processed_count`: 1 (or 2 depending on skipped_count recording)
- Farm B receives outbound message.
- Server returns HTTP 200 with job summary response without unhandled exception.
