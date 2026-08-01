import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import Any, Dict, Union
from app.config import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, GCP_PROJECT_ID
from app.whatsapp import _is_mock_token


def is_real_credential_configured() -> bool:
    """Positively verify that environment credentials are configured and are not mock/dev placeholders.
    
    Reuses app.whatsapp._is_mock_token to ensure zero logic drift.
    """
    if not WHATSAPP_TOKEN or _is_mock_token(WHATSAPP_TOKEN):
        return False
    if not WHATSAPP_PHONE_NUMBER_ID or WHATSAPP_PHONE_NUMBER_ID.lower().startswith("mock_"):
        return False
    if not GCP_PROJECT_ID or GCP_PROJECT_ID.lower() in ["mock_project", "test_project"]:
        return False
    return True


def assert_no_mock_substring(payload: Union[str, Dict[str, Any], list]) -> None:
    """Tripwire: Raise RuntimeError if any response payload contains the literal substring 'mock'."""
    payload_str = str(payload).lower()
    if "mock" in payload_str:
        raise RuntimeError(
            "ERROR: Response payload contains the substring 'mock'. "
            "Execution refused to prevent synthetic data reporting."
        )


def enforce_real_credentials_or_exit() -> None:
    """Refuse execution immediately with an explicit error if real credentials are missing."""
    if not is_real_credential_configured():
        sys.stderr.write(
            "ERROR: Real credentials are not configured (mock/placeholder token or project ID detected). "
            "Refusing execution. Verification cannot proceed in mock mode.\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    enforce_real_credentials_or_exit()
    masked_token = WHATSAPP_TOKEN[:6] + "..." if len(WHATSAPP_TOKEN) > 6 else "***"
    sys.stdout.write(
        f"Real credentials confirmed:\n"
        f"  GCP Project ID: {GCP_PROJECT_ID}\n"
        f"  Phone Number ID: {WHATSAPP_PHONE_NUMBER_ID}\n"
        f"  Token Prefix: {masked_token}\n"
    )
