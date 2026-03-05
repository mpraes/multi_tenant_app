"""Time/date helpers used in flows and integrations."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Timezone-aware UTC now. Prefer this over datetime.utcnow() (which is naive)."""
    return datetime.now(tz=timezone.utc)


def greeting_for_hour(hour: int | None = None) -> str:
    """
    Return a time-appropriate greeting string.
    Useful in welcome flows to make responses feel less robotic.

    Example:
        prompt = f"{greeting_for_hour()}, how can I help you today?"
    """
    h = hour if hour is not None else utcnow().hour
    if 5 <= h < 12:
        return "Good morning"
    if 12 <= h < 18:
        return "Good afternoon"
    return "Good evening"
