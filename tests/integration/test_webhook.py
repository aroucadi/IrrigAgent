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


def test_webhook_receive_option_1():
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
