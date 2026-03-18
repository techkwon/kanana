import json
from typing import Any, Dict, Optional

from .common import Audience, OutputOptions, RequestEnvelope, SafetyOptions, SessionOptions
from .errors import InputValidationError

_ALLOWED_LEVELS = {"elementary", "middle", "high", "adult"}
_ALLOWED_MODES = {"strict", "standard"}
_ALLOWED_VERBOSITY = {"brief", "standard", "detailed"}


def _ensure_mapping(value: Any, field_name: str) -> Dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise InputValidationError(f"{field_name} must be an object", {"field": field_name})
    return value


def parse_input_json(raw: str) -> Dict[str, Any]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InputValidationError("input must be valid JSON", {"position": exc.pos})
    if not isinstance(value, dict):
        raise InputValidationError("top-level JSON input must be an object")
    return value


def build_request_envelope(source: Optional[Dict[str, Any]] = None, overrides: Optional[Dict[str, Any]] = None) -> RequestEnvelope:
    payload = dict(source or {})
    overrides = overrides or {}

    base_input = _ensure_mapping(payload.get("input"), "input")
    audience_data = payload.get("audience") or {}
    safety_data = payload.get("safety") or {}
    session_data = payload.get("session") or {}
    output_data = payload.get("output") or {}

    if overrides.get("input"):
        base_input.update(overrides["input"])
    audience_data = {**audience_data, **overrides.get("audience", {})}
    safety_data = {**safety_data, **overrides.get("safety", {})}
    session_data = {**session_data, **overrides.get("session", {})}
    output_data = {**output_data, **overrides.get("output", {})}

    learner_level = audience_data.get("learner_level", "elementary")
    if learner_level not in _ALLOWED_LEVELS:
        raise InputValidationError("audience.learner_level is invalid", {"allowed": sorted(_ALLOWED_LEVELS)})

    mode = safety_data.get("mode", "strict")
    if mode not in _ALLOWED_MODES:
        raise InputValidationError("safety.mode is invalid", {"allowed": sorted(_ALLOWED_MODES)})

    verbosity = output_data.get("verbosity", "standard")
    if verbosity not in _ALLOWED_VERBOSITY:
        raise InputValidationError("output.verbosity is invalid", {"allowed": sorted(_ALLOWED_VERBOSITY)})

    output_format = output_data.get("format", "json")
    if output_format != "json":
        raise InputValidationError("output.format must be json", {"provided": output_format})

    return RequestEnvelope(
        input=base_input,
        audience=Audience(
            role=audience_data.get("role", "educator"),
            learner_level=learner_level,
        ),
        safety=SafetyOptions(
            mode=mode,
            block_on_unsafe=bool(safety_data.get("block_on_unsafe", True)),
        ),
        session=SessionOptions(
            id=session_data.get("id"),
            save=bool(session_data.get("save", True)),
        ),
        output=OutputOptions(
            format="json",
            verbosity=verbosity,
        ),
    )
