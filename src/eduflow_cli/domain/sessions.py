import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
from uuid import uuid4

from eduflow_cli.config import get_settings

REDACTED = "***REDACTED***"
_SECRET_KEYS = {"api_key", "token", "secret", "authorization", "password", "access_token", "refresh_token"}


def _sanitize(value: Any) -> Any:
    if isinstance(value, Mapping):
        sanitized: Dict[str, Any] = {}
        for key, item in value.items():
            sanitized[key] = REDACTED if key.lower() in _SECRET_KEYS else _sanitize(item)
        return sanitized
    if isinstance(value, list):
        return [_sanitize(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize(item) for item in value]
    return value


def sanitize_payload(payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    return _sanitize(dict(payload or {}))


def save_session(
    command: str,
    request_payload: Dict[str, Any],
    response_payload: Dict[str, Any],
    safety_payload: Dict[str, Any],
    session_id: Optional[str] = None,
) -> str:
    settings = get_settings()
    sid = session_id or f"session-{uuid4()}"
    session_dir = Path(settings.session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    path = session_dir / f"{sid}.json"
    record = {
        "session_id": sid,
        "command": command,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "request": sanitize_payload(request_payload),
        "response": sanitize_payload(response_payload),
        "safety": sanitize_payload(safety_payload),
    }
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return sid
