import pytest
import sys
from unittest.mock import patch
from app.whatsapp import _is_mock_token
from scripts.verify_credential_guard import (
    is_real_credential_configured,
    assert_no_mock_substring,
    enforce_real_credentials_or_exit,
)


def test_is_mock_token_detection():
    """Verify that _is_mock_token correctly flags placeholder and dev tokens."""
    assert _is_mock_token("") is True
    assert _is_mock_token("eaag_your_token_123") is True
    assert _is_mock_token("your_token_here") is True
    assert _is_mock_token("mock_access_token") is True
    assert _is_mock_token("test_token_xyz") is True
    assert _is_mock_token("EAAB123456789REALTOKEN") is False


def test_is_real_credential_configured_rejects_mock_token():
    """Verify that is_real_credential_configured returns False for mock tokens."""
    with patch("scripts.verify_credential_guard.WHATSAPP_TOKEN", "mock_token_123"):
        assert is_real_credential_configured() is False


def test_assert_no_mock_substring_tripwire():
    """Verify that response bodies containing 'mock' trigger an immediate RuntimeError."""
    clean_payload = {"messaging_product": "whatsapp", "messages": [{"id": "wamid.HBgL..."}]}
    assert_no_mock_substring(clean_payload)  # Should not raise exception

    mock_payload = {"messaging_product": "whatsapp", "messages": [{"id": "mock_wamid_123"}]}
    with pytest.raises(RuntimeError) as exc_info:
        assert_no_mock_substring(mock_payload)
    assert "mock" in str(exc_info.value).lower()


def test_enforce_real_credentials_or_exit_exits_on_mock():
    """Verify that enforce_real_credentials_or_exit exits with code 1 when mock credentials are present."""
    with patch("scripts.verify_credential_guard.WHATSAPP_TOKEN", "your_token"):
        with pytest.raises(SystemExit) as exc_info:
            enforce_real_credentials_or_exit()
        assert exc_info.value.code == 1
