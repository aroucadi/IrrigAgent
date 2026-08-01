import argparse
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import httpx
from app.config import WHATSAPP_TOKEN, GRAPH_API_VERSION
from scripts.verify_credential_guard import (
    enforce_real_credentials_or_exit,
    assert_no_mock_substring,
)


async def check_template_status(waba_id: str, template_name: str) -> None:
    enforce_real_credentials_or_exit()

    if not waba_id:
        sys.stderr.write("ERROR: WhatsApp Business Account ID (WABA ID) is required.\n")
        sys.exit(1)

    sys.stdout.write(f"Target WABA ID Queried: {waba_id}\n")
    sys.stdout.write(f"Target Template Name: {template_name}\n\n")

    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{waba_id}/message_templates"
    params = {"name": template_name}
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, headers=headers, params=params)
            raw_json = resp.json()
            assert_no_mock_substring(raw_json)
            sys.stdout.write("Raw Meta Template Management API Response:\n")
            sys.stdout.write(json.dumps(raw_json, indent=2) + "\n")
        except Exception as err:
            error_body = getattr(err, "response", None)
            raw_err_output = error_body.text if error_body is not None else str(err)
            assert_no_mock_substring(raw_err_output)
            sys.stdout.write("Raw Meta Template Management API Error Response:\n")
            sys.stdout.write(raw_err_output + "\n")


def main():
    parser = argparse.ArgumentParser(description="Real Meta Template Approval Status Check Tool")
    default_waba = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    parser.add_argument("--waba-id", default=default_waba, help="WhatsApp Business Account ID (WABA ID)")
    parser.add_argument("--name", default="irrigagent_daily_advisory", help="Template name to query")
    args = parser.parse_args()

    asyncio.run(check_template_status(args.waba_id, args.name))


if __name__ == "__main__":
    main()
