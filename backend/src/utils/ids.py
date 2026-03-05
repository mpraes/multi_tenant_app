"""ID generation helpers for sessions, events, and traceability."""

import uuid


def new_session_id() -> str:
    """Generate a unique session/conversation identifier."""
    return f"sess_{uuid.uuid4().hex}"


def new_event_id() -> str:
    """Generate a unique event/message identifier for tracing."""
    return f"evt_{uuid.uuid4().hex}"


def new_user_id() -> str:
    """Generate an anonymous user identifier (use only when no channel ID is available)."""
    return f"usr_{uuid.uuid4().hex}"
