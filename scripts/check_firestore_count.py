import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import GCP_PROJECT_ID
from scripts.verify_credential_guard import (
    enforce_real_credentials_or_exit,
    assert_no_mock_substring,
)


async def check_firestore_farm_count() -> None:
    enforce_real_credentials_or_exit()

    sys.stdout.write(f"Connected GCP Project ID: {GCP_PROJECT_ID}\n\n")

    try:
        from google.cloud import firestore
        client = firestore.AsyncClient(project=GCP_PROJECT_ID)
    except Exception as err:
        sys.stderr.write(f"ERROR: Failed to initialize live Firestore client: {err}\n")
        sys.exit(1)

    try:
        docs = client.collection("farm_profiles").stream()
        profiles = []
        async for doc in docs:
            data = doc.to_dict()
            profiles.append((doc.id, data))
    except Exception as err:
        sys.stderr.write(f"ERROR: Failed to query live Firestore farm_profiles collection: {err}\n")
        sys.exit(1)

    assert_no_mock_substring(profiles)

    sys.stdout.write(f"Total Farm Profile Document Count: {len(profiles)}\n")
    sys.stdout.write("Document List:\n")
    for doc_id, data in profiles:
        phone = data.get("phone_number") or doc_id
        last_inbound = data.get("last_inbound_timestamp") or data.get("updated_at") or "None"
        sys.stdout.write(f"  - Phone/ID: {phone} | Last Interaction: {last_inbound}\n")


def main():
    asyncio.run(check_firestore_farm_count())


if __name__ == "__main__":
    main()
