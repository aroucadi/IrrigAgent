import pytest
from unittest.mock import patch


@pytest.fixture
def override_whatsapp_token():
    """Fixture that overrides WHATSAPP_TOKEN to a non-placeholder token string

    so that _is_mock_token returns False and httpx client requests are constructed.
    """
    token_val = "EAAG_valid_graph_token_xyz"
    with patch("app.whatsapp.WHATSAPP_TOKEN", token_val):
        yield token_val
