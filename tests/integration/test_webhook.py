import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.config import VERIFY_TOKEN, JOB_SECRET_TOKEN


def test_webhook_verification_success():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            params = {
                "hub.mode": "subscribe",
                "hub.verify_token": VERIFY_TOKEN,
                "hub.challenge": "CHALLENGE_ACCEPTED_123",
            }
            resp = await client.get("/webhook", params=params)
            assert resp.status_code == 200
            assert resp.text == "CHALLENGE_ACCEPTED_123"
    asyncio.run(_test())


def test_webhook_verification_failure():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            params = {
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong_token",
                "hub.challenge": "CHALLENGE",
            }
            resp = await client.get("/webhook", params=params)
            assert resp.status_code == 403
    asyncio.run(_test())


def test_webhook_receive_option_1_approve():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [{
                                "from": "+212600000000",
                                "id": "wamid_test_1",
                                "type": "text",
                                "text": {"body": "1"}
                            }]
                        }
                    }]
                }]
            }
            resp = await client.post("/webhook", json=payload)
            assert resp.status_code == 200
            assert resp.json().get("status") == "approved"
    asyncio.run(_test())


def test_webhook_receive_option_2_skip():
    """Test Option 2 reply ('2') skips tomorrow's irrigation adjustment."""
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [{
                                "from": "+212600000000",
                                "id": "wamid_test_2",
                                "type": "text",
                                "text": {"body": "2"}
                            }]
                        }
                    }]
                }]
            }
            resp = await client.post("/webhook", json=payload)
            assert resp.status_code == 200
            assert resp.json().get("status") == "skipped"
    asyncio.run(_test())


def test_webhook_receive_option_3_modify():
    """Test Option 3 reply ('3 +10 min at 05:00') parses custom modification."""
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [{
                                "from": "+212600000000",
                                "id": "wamid_test_3",
                                "type": "text",
                                "text": {"body": "3 +10 min at 05:00"}
                            }]
                        }
                    }]
                }]
            }
            resp = await client.post("/webhook", json=payload)
            assert resp.status_code == 200
            assert resp.json().get("status") == "modified"
    asyncio.run(_test())


def test_webhook_receive_profile_command_update():
    """Test webhook parsing of farm profile update command per FR-018."""
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [{
                                "from": "+212600000000",
                                "id": "wamid_test_prof",
                                "type": "text",
                                "text": {"body": "update crop citrus"}
                            }]
                        }
                    }]
                }]
            }
            resp = await client.post("/webhook", json=payload)
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("status") == "profile_command_processed"
            assert data.get("updated_fields") == {"crop_type": "citrus"}
    asyncio.run(_test())


def test_webhook_unrecognized_text_reminder():
    """Test webhook handling of unrecognized reply sending gentle reminder per FR-019."""
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [{
                                "from": "+212600000000",
                                "id": "wamid_test_unrecognized",
                                "type": "text",
                                "text": {"body": "random unrecognized message"}
                            }]
                        }
                    }]
                }]
            }
            resp = await client.post("/webhook", json=payload)
            assert resp.status_code == 200
            assert resp.json().get("status") == "reminder_sent"
    asyncio.run(_test())


def test_webhook_receive_image_cropdoctor():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [{
                                "from": "+212600000000",
                                "id": "wamid_test_img",
                                "type": "image",
                                "image": {"id": "mock_img_123"}
                            }]
                        }
                    }]
                }]
            }
            resp = await client.post("/webhook", json=payload)
            assert resp.status_code == 200
            assert resp.json().get("status") == "triage_completed"
    asyncio.run(_test())


def test_daily_batch_job_authorization():
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            headers = {"Authorization": f"Bearer {JOB_SECRET_TOKEN}"}
            resp = await client.post("/jobs/daily-recommendations", headers=headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("status") == "success"
            assert "dispatched_count" in data
    asyncio.run(_test())


def test_health_endpoint():
    """Verify GET /health returns HTTP 200 matching HealthCheckResponse schema structure."""
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("status") == "ok"
            assert data.get("app") == "IrrigAgent AI"
            assert "version" in data
            assert "voice_teaser_enabled" in data
    asyncio.run(_test())


def test_daily_advisory_alias_endpoint():
    """Verify POST /api/v1/jobs/daily-advisory returns identical status & auth behavior as /jobs/daily-recommendations."""
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Unauthorized call check
            unauth_resp = await client.post("/api/v1/jobs/daily-advisory")
            assert unauth_resp.status_code == 401

            # Authorized call check
            headers = {"Authorization": f"Bearer {JOB_SECRET_TOKEN}"}
            resp = await client.post("/api/v1/jobs/daily-advisory", headers=headers)
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("status") == "success"
            assert "processed_count" in data
            assert "skipped_count" in data
    asyncio.run(_test())


def test_webhook_missing_media_id_image():
    """Verify that an image event with a missing media ID is handled cleanly with a retry message (US5 / CRIT-007)."""
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [{
                                "from": "+212600000000",
                                "id": "wamid_test_img_no_id",
                                "type": "image",
                                "image": {}  # Missing "id"
                            }]
                        }
                    }]
                }]
            }
            resp = await client.post("/webhook", json=payload)
            assert resp.status_code == 200
            assert resp.json().get("status") == "missing_media_id_handled"
    asyncio.run(_test())


def test_webhook_missing_media_id_audio():
    """Verify that an audio event with a missing media ID is handled cleanly with a retry message (US5 / CRIT-007)."""
    async def _test():
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            payload = {
                "object": "whatsapp_business_account",
                "entry": [{
                    "changes": [{
                        "value": {
                            "messaging_product": "whatsapp",
                            "messages": [{
                                "from": "+212600000000",
                                "id": "wamid_test_audio_no_id",
                                "type": "audio",
                                "audio": {}  # Missing "id"
                            }]
                        }
                    }]
                }]
            }
            resp = await client.post("/webhook", json=payload)
            assert resp.status_code == 200
            assert resp.json().get("status") == "missing_media_id_handled"
    asyncio.run(_test())


