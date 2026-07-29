import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_whatsapp_location_and_heatmap_full_flow():
    phone = "+212611223344"

    # 1. Trigger /parcel pin collection
    payload_start = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "wba_123",
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "id": "msg_001",
                        "timestamp": "1785254400",
                        "type": "text",
                        "text": {"body": "/parcel"}
                    }]
                }
            }]
        }]
    }
    resp1 = client.post("/webhook", json=payload_start)
    assert resp1.status_code == 200
    assert resp1.json()["status"] == "pin_collection_started"

    # 2. Send 4 corner location pins
    pins = [
        {"latitude": 30.4278, "longitude": -9.5981},
        {"latitude": 30.4280, "longitude": -9.5950},
        {"latitude": 30.4250, "longitude": -9.5952},
        {"latitude": 30.4251, "longitude": -9.5983},
    ]

    for idx, pin in enumerate(pins, 1):
        loc_payload = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "wba_123",
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": phone,
                            "id": f"msg_pin_{idx}",
                            "timestamp": "1785254400",
                            "type": "location",
                            "location": pin
                        }]
                    }
                }]
            }]
        }
        resp = client.post("/webhook", json=loc_payload)
        assert resp.status_code == 200
        assert resp.json()["status"] == "pin_recorded"
        assert resp.json()["pin_count"] == idx

    # 3. Send "DONE" to close polygon & validate
    done_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "wba_123",
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "id": "msg_done",
                        "timestamp": "1785254400",
                        "type": "text",
                        "text": {"body": "DONE"}
                    }]
                }
            }]
        }]
    }
    resp_done = client.post("/webhook", json=done_payload)
    assert resp_done.status_code == 200
    assert resp_done.json()["status"] == "parcel_registered"
    assert 7.0 <= resp_done.json()["area_hectares"] <= 10.0

    # 4. Trigger /heatmap command
    heatmap_payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "wba_123",
            "changes": [{
                "value": {
                    "messages": [{
                        "from": phone,
                        "id": "msg_heatmap",
                        "timestamp": "1785254400",
                        "type": "text",
                        "text": {"body": "/heatmap"}
                    }]
                }
            }]
        }]
    }
    resp_heatmap = client.post("/webhook", json=heatmap_payload)
    assert resp_heatmap.status_code == 200
    assert resp_heatmap.json()["status"] == "heatmap_dispatched"
    assert "media_id" in resp_heatmap.json()
