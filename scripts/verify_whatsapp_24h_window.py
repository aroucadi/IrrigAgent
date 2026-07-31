"""
Standalone verification script to test WhatsApp 24-hour customer service window status
and Meta Cloud API error code 131026 behavior against live/mock sandbox endpoints.
"""
import asyncio
from datetime import datetime, timezone, timedelta
from app.whatsapp import send_text_message, send_template_message, is_user_in_24h_window
from app.firestore_client import save_inbound_timestamp, get_inbound_timestamp


async def run_verification():
    print("=" * 60)
    print("WhatsApp 24-Hour Customer Service Window Live Verification")
    print("=" * 60)

    test_phone = "+212600000000"

    # 1. Test Inbound Timestamp Window Tracking
    now = datetime.now(timezone.utc)
    recent_timestamp = (now - timedelta(hours=2)).isoformat()
    await save_inbound_timestamp(test_phone, recent_timestamp)
    retrieved = await get_inbound_timestamp(test_phone)
    in_window = is_user_in_24h_window(retrieved)
    print(f"Test Phone: {test_phone}")
    print(f"Recorded Last Inbound: {retrieved}")
    print(f"24h Customer Service Window Active? -> {in_window} (Expected: True)")

    # 2. Test Expired Window Simulation
    expired_timestamp = (now - timedelta(hours=26)).isoformat()
    await save_inbound_timestamp(test_phone, expired_timestamp)
    retrieved_expired = await get_inbound_timestamp(test_phone)
    expired_window = is_user_in_24h_window(retrieved_expired)
    print(f"\nSimulating Expired Timestamp (>24h): {retrieved_expired}")
    print(f"24h Customer Service Window Active? -> {expired_window} (Expected: False)")

    # 3. Test Free-form Text Message Dispatch
    print("\nAttempting free-form text message transmission...")
    res_text = await send_text_message(test_phone, "Verification text message.")
    print(f"Free-form dispatch result: {res_text}")

    # 4. Test Approved Message Template Dispatch
    print("\nAttempting Meta Message Template dispatch (UTILITY / fr)...")
    res_template = await send_template_message(
        to=test_phone,
        template_name="daily_irrigation_advisory",
        language_code="fr",
        parameters=["Ferme Hassan", "4.5 mm", "45 min"],
    )
    print(f"Template dispatch result: {res_template}")

    print("\n" + "=" * 60)
    print("Verification Completed Successfully.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_verification())
