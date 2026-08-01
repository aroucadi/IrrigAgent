import argparse
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timezone

from scripts.verify_credential_guard import (
    enforce_real_credentials_or_exit,
    assert_no_mock_substring,
)
from app.whatsapp import send_text_message, send_template_message

RECORD_FILE = ".verify_window_last_open.json"


async def run_open_step(to_phone: str) -> None:
    enforce_real_credentials_or_exit()
    
    now_utc = datetime.now(timezone.utc).isoformat()
    raw_response = await send_text_message(to=to_phone, body="Window verification open request.")
    assert_no_mock_substring(raw_response)

    record_data = {
        "timestamp_utc": now_utc,
        "recipient": to_phone,
        "open_response": raw_response,
    }
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(record_data, f, indent=2)

    sys.stdout.write(f"Wall-Clock Timestamp (UTC): {now_utc}\n")
    sys.stdout.write("Raw Meta API Open Response:\n")
    sys.stdout.write(json.dumps(raw_response, indent=2) + "\n")
    sys.stdout.write(f"Recorded timestamp to local file {RECORD_FILE}\n")


async def run_check_step(to_phone: str) -> None:
    enforce_real_credentials_or_exit()

    sys.stdout.write("--- Step: Check Free-Form Text Send Attempt ---\n")
    text_response = None
    try:
        text_response = await send_text_message(to=to_phone, body="Window verification check request.")
        assert_no_mock_substring(text_response)
        sys.stdout.write(json.dumps(text_response, indent=2) + "\n")
    except Exception as err:
        error_body = getattr(err, "response", None)
        raw_err_output = error_body.text if error_body is not None else str(err)
        assert_no_mock_substring(raw_err_output)
        sys.stdout.write(f"Raw Text Error Response:\n{raw_err_output}\n")

    sys.stdout.write("\n--- Step: Check Template Send Attempt ---\n")
    template_response = None
    try:
        template_response = await send_template_message(to=to_phone)
        assert_no_mock_substring(template_response)
        sys.stdout.write(json.dumps(template_response, indent=2) + "\n")
    except Exception as err:
        error_body = getattr(err, "response", None)
        raw_err_output = error_body.text if error_body is not None else str(err)
        assert_no_mock_substring(raw_err_output)
        sys.stdout.write(f"Raw Template Error Response:\n{raw_err_output}\n")

    sys.stdout.write(
        "\nNOTICE: Time elapsed between window open and check steps is NOT asserted or "
        "computed by this tool. The human operator is strictly responsible for verifying "
        "real wall-clock elapsed time.\n"
    )


def main():
    parser = argparse.ArgumentParser(description="Real 24-Hour Messaging Window Verification Tool")
    parser.add_argument("--step", choices=["open", "check"], required=True, help="Verification step to execute")
    parser.add_argument("--to", required=True, help="Recipient phone number (e.g. +212600000000)")
    args = parser.parse_args()

    if args.step == "open":
        asyncio.run(run_open_step(args.to))
    elif args.step == "check":
        asyncio.run(run_check_step(args.to))


if __name__ == "__main__":
    main()
