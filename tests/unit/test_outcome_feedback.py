import pytest
from unittest.mock import AsyncMock, patch
from app.main import receive_webhook
from app.firestore_client import save_recommendation, get_recommendation

@pytest.mark.asyncio
async def test_outcome_feedback_quick_reply_persistence():
    phone = "+212655443322"
    rec_id = f"rec_{phone}_2026-07-31"
    rec_data = {
        "recommendation_id": rec_id,
        "phone_number": phone,
        "dispatched_at": "2026-07-31T18:45:00Z",
        "status": "approved",
    }
    await save_recommendation(rec_data)

    # Simulate farmer tapping "Yes" outcome feedback button (FB_YES)
    fb_msg = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "type": "interactive",
                        "interactive": {
                            "type": "button_reply",
                            "button_reply": {"id": "FB_YES", "title": "Yes"}
                        }
                    }]
                }
            }]
        }]
    }

    with patch("app.main.send_text_message", new_callable=AsyncMock) as mock_send:
        res = await receive_webhook(AsyncMock(json=AsyncMock(return_value=fb_msg)), AsyncMock())
        assert res["status"] == "outcome_feedback_saved"
        assert res["feedback"] == "yes"
        mock_send.assert_called_once()
        assert "retour" in mock_send.call_args[0][1].lower()

    updated_rec = await get_recommendation(rec_id)
    assert updated_rec["outcome_feedback"] == "yes"
    assert "outcome_updated_at" in updated_rec
