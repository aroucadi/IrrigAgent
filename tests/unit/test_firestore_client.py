import asyncio
from app.firestore_client import detect_arabizi_or_arabic, save_recommendation, get_latest_recommendation_for_user


def test_detect_arabizi_or_arabic_strict_word_internal():
    # 1. Standalone option digit "3", clock times "06h30", and quantities "30 min" MUST NOT trigger Arabizi flipping
    assert detect_arabizi_or_arabic("3") is False
    assert detect_arabizi_or_arabic("06h30") is False
    assert detect_arabizi_or_arabic("30 min") is False
    assert detect_arabizi_or_arabic("1") is False
    assert detect_arabizi_or_arabic("2") is False

    # 2. Word-internal Arabizi digits ('m3ak', '7na', '9dim') MUST trigger Arabizi flipping
    assert detect_arabizi_or_arabic("m3ak khoya") is True
    assert detect_arabizi_or_arabic("7na f l'ferme") is True
    assert detect_arabizi_or_arabic("koulshi 9dim") is True

    # 3. Arabic script MUST trigger Arabizi flipping
    assert detect_arabizi_or_arabic("مرحبا بك") is True


def test_get_latest_recommendation_for_user():
    async def _test():
        phone = "+212611223344"
        rec1 = {
            "recommendation_id": f"rec_{phone}_1",
            "phone_number": phone,
            "dispatched_at": "2026-07-28T18:00:00Z",
            "status": "pending",
        }
        rec2 = {
            "recommendation_id": f"rec_{phone}_2",
            "phone_number": phone,
            "dispatched_at": "2026-07-28T19:00:00Z",
            "status": "pending",
        }
        await save_recommendation(rec1)
        await save_recommendation(rec2)

        latest = await get_latest_recommendation_for_user(phone)
        assert latest is not None
        assert latest["recommendation_id"] == f"rec_{phone}_2"

    asyncio.run(_test())
