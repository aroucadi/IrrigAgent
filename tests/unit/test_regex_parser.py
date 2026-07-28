from app.regex_parser import parse_modification_text


def test_parse_duration_and_time():
    text = "+10 min at 05:00"
    parsed, ack = parse_modification_text(text)
    assert parsed.get("duration_delta_min") == 10
    assert parsed.get("start_time") == "05:00"
    assert "Noted: +10 min at 05:00" in ack


def test_parse_negative_duration():
    text = "-15min"
    parsed, ack = parse_modification_text(text)
    assert parsed.get("duration_delta_min") == -15
    assert "Noted: -15 min" in ack


def test_parse_unmatched_fallback():
    text = "please reduce watering a bit"
    parsed, ack = parse_modification_text(text)
    assert parsed == {}
    assert "Your modification request has been recorded" in ack
