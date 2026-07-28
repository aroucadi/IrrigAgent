import pytest
from app.regex_parser import parse_modification_text


def test_parse_duration_and_time():
    """Test standard Option 3 modification with both duration adjustment and clock time."""
    text = "+10 min at 05:00"
    parsed, ack = parse_modification_text(text)
    assert parsed.get("duration_delta_min") == 10
    assert parsed.get("start_time") == "05:00"
    assert "Noted: +10 min at 05:00" in ack


def test_parse_negative_duration():
    """Test Option 3 modification with negative duration delta."""
    text = "-15min"
    parsed, ack = parse_modification_text(text)
    assert parsed.get("duration_delta_min") == -15
    assert "Noted: -15 min" in ack


def test_parse_time_with_h_format():
    """Test Option 3 modification specifying start time using '06h30' format."""
    text = "06h30"
    parsed, ack = parse_modification_text(text)
    assert parsed.get("start_time") == "06h30"
    assert "Noted: at 06h30" in ack


def test_parse_combined_duration_and_h_time():
    """Test Option 3 modification with negative duration and '04h15' start time."""
    text = "-10 min at 04h15"
    parsed, ack = parse_modification_text(text)
    assert parsed.get("duration_delta_min") == -10
    assert parsed.get("start_time") == "04h15"
    assert "Noted: -10 min at 04h15" in ack


def test_parse_unmatched_fallback():
    """Test fallback behavior when text reply does not match narrow duration/time regex."""
    text = "please reduce watering a bit"
    parsed, ack = parse_modification_text(text)
    assert parsed == {}
    assert "Your modification request has been recorded" in ack


def test_parse_empty_input():
    """Test edge case handling for empty input string."""
    parsed, ack = parse_modification_text("")
    assert parsed == {}
    assert ack == "Noted, thank you."
