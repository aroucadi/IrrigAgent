import re
from typing import Dict, Any, Tuple


def parse_modification_text(text: str) -> Tuple[Dict[str, Any], str]:
    """Parse custom modification text reply from user (Option 3).
    
    Uses narrow regex patterns:
    - Duration: [+-]\\d+\\s*min (e.g. "+10 min", "-5min")
    - Clock time: \\d{1,2}:\\d{2}|\\d{1,2}h\\d{0,2} (e.g. "05:00", "06h30")
    
    Returns (parsed_dict, acknowledgment_message).
    """
    if not text:
        return {}, "Noted, thank you."

    parsed: Dict[str, Any] = {}
    
    # 1. Match duration pattern
    duration_match = re.search(r'([+-]?\d+)\s*min', text, re.IGNORECASE)
    if duration_match:
        try:
            parsed["duration_delta_min"] = int(duration_match.group(1))
        except ValueError:
            pass

    # 2. Match clock time pattern
    time_match = re.search(r'(\d{1,2}:\d{2}|\d{1,2}h\d{0,2})', text, re.IGNORECASE)
    if time_match:
        parsed["start_time"] = time_match.group(1)

    # Build confirmation message
    if parsed:
        details = []
        if "duration_delta_min" in parsed:
            delta = parsed["duration_delta_min"]
            sign = "+" if delta > 0 else ""
            details.append(f"{sign}{delta} min")
        if "start_time" in parsed:
            details.append(f"at {parsed['start_time']}")
        
        detail_str = " ".join(details)
        ack_msg = f"Noted: {detail_str} for tomorrow's schedule."
    else:
        # Fallback to raw text logging acknowledgment if narrow regex unmatched
        ack_msg = "Noted, thank you. Your modification request has been recorded."

    return parsed, ack_msg


def is_parcel_start_command(text: str) -> bool:
    if not text:
        return False
    raw = text.strip().lower()
    return bool(re.search(r'^(?:/parcel|/boundary|add boundary)$', raw))


def is_parcel_done_command(text: str) -> bool:
    if not text:
        return False
    raw = text.strip().lower()
    return bool(re.search(r'^(?:done|finish|fin)$', raw))


def is_parcel_cancel_command(text: str) -> bool:
    if not text:
        return False
    raw = text.strip().lower()
    return bool(re.search(r'^(?:/cancel|/reset|cancel)$', raw))


def is_heatmap_command(text: str) -> bool:
    if not text:
        return False
    raw = text.strip().lower()
    return bool(re.search(r'^(?:/heatmap|heatmap|/sentinel|canopy map|canopy)$', raw))
