import argparse
import json
import sys
import time
from typing import Any, Dict, Optional

from eduflow_cli.config import get_settings
from eduflow_cli.contracts.errors import InputValidationError
from eduflow_cli.contracts.requests import build_request_envelope, parse_input_json
from eduflow_cli.contracts.responses import ResponseEnvelope, ResponseMeta
from eduflow_cli.domain.audience import guidance_for_level
from eduflow_cli.domain.prompts import build_prompt
from eduflow_cli.domain.sessions import save_session
from eduflow_cli.output.quality import clean_generated_text
from eduflow_cli.output.structured import (
    render_explain_fallback,
    render_quiz_fallback,
    render_quiz_template,
    render_review_fallback,
    render_review_template,
    render_structured_payload,
    structured_prompt_for,
    validate_structured_payload,
)
from eduflow_cli.runtime.model_registry import default_model_name
from eduflow_cli.runtime.ollama_client import OllamaClient
from eduflow_cli.safety.pipeline import evaluate_safety


def load_json_from_stdin() -> Optional[Dict[str, Any]]:
    if sys.stdin.isatty():
        return None
    raw = sys.stdin.read().strip()
    if not raw:
        return None
    return parse_input_json(raw)


def envelope_from_args(args: argparse.Namespace, stdin_payload: Optional[Dict[str, Any]] = None) -> Any:
    source = stdin_payload or {}
    if getattr(args, "input_json", None):
        source = parse_input_json(args.input_json)

    input_overrides: Dict[str, Any] = {}
    for field in ("topic", "question", "submission", "focus", "tone"):
        value = getattr(args, field, None)
        if value:
            input_overrides[field] = value

    audience_overrides: Dict[str, Any] = {}
    if getattr(args, "learner_level", None):
        audience_overrides["learner_level"] = args.learner_level

    safety_overrides: Dict[str, Any] = {}
    if getattr(args, "safety_mode", None):
        safety_overrides["mode"] = args.safety_mode
    if getattr(args, "allow_unsafe", False):
        safety_overrides["block_on_unsafe"] = False

    session_overrides: Dict[str, Any] = {}
    if getattr(args, "session_id", None):
        session_overrides["id"] = args.session_id
    if getattr(args, "no_save", False):
        session_overrides["save"] = False

    overrides = {
        "input": input_overrides,
        "audience": audience_overrides,
        "safety": safety_overrides,
        "session": session_overrides,
    }
    return build_request_envelope(source=source, overrides=overrides)


def _structured_attempt_count() -> int:
    return 2


def _render_command_fallback(command: str, user_input: Dict[str, Any], raw_output: str) -> str:
    if command == "explain":
        topic = user_input.get("topic") or user_input.get("submission") or user_input.get("question") or "설명"
        return render_explain_fallback(topic, raw_output)
    if command == "quiz":
        fallback = render_quiz_fallback(raw_output)
        if fallback.strip():
            return fallback
        return render_quiz_template(user_input.get("topic") or user_input.get("question") or "학습 주제")
    if command == "review":
        fallback = render_review_fallback(raw_output)
        if fallback.strip():
            return fallback
        return render_review_template(user_input.get("submission") or user_input.get("topic") or "학습자 작업")
    return raw_output


def _generate_structured_first(
    command: str,
    user_input: Dict[str, Any],
    learner_level: str,
    prompt: str,
    client: OllamaClient,
) -> tuple[str, str, Optional[Dict[str, Any]]]:
    topic = user_input.get("topic") or user_input.get("submission") or user_input.get("question") or ""
    structured_prompt = structured_prompt_for(
        command,
        topic,
        guidance_for_level(learner_level),
    )

    last_error: Optional[Exception] = None
    for _ in range(_structured_attempt_count()):
        try:
            structured_payload = validate_structured_payload(
                command,
                client.generate_json(prompt=structured_prompt, model=default_model_name()),
                topic=topic,
            )
            return render_structured_payload(command, structured_payload), structured_prompt, structured_payload
        except Exception as exc:
            last_error = exc

    try:
        raw_output = client.generate(prompt=prompt, model=default_model_name())
    except Exception:
        if last_error is not None:
            raise last_error
        raise
    return _render_command_fallback(command, user_input, raw_output), prompt, None


def execute_generation(command: str, envelope: Any) -> Dict[str, Any]:
    user_input = envelope.input
    if not user_input:
        raise InputValidationError("input payload is required", {"command": command})

    learner_level = envelope.audience.learner_level
    prompt = build_prompt(command, learner_level, user_input)
    start = time.perf_counter()
    client = OllamaClient()
    structured_payload = None
    if command in {"explain", "quiz", "review"}:
        raw_output, prompt, structured_payload = _generate_structured_first(
            command=command,
            user_input=user_input,
            learner_level=learner_level,
            prompt=prompt,
            client=client,
        )
    else:
        raw_output = client.generate(prompt=prompt, model=default_model_name())
    safety_result, safe_output = evaluate_safety(
        command=command,
        text_in=json.dumps(user_input, ensure_ascii=False),
        text_out=raw_output,
        learner_level=learner_level,
        block_on_unsafe=envelope.safety.block_on_unsafe,
    )
    cleaned_output = clean_generated_text(safe_output)
    latency_ms = int((time.perf_counter() - start) * 1000)
    result = {
        "content": cleaned_output,
        "input": user_input,
        "prompt": prompt,
        "learner_level": learner_level,
        "safety": safety_result,
    }
    if structured_payload is not None:
        result["structured"] = structured_payload
    session_id = None
    if envelope.session.save:
        session_id = save_session(command, envelope.to_dict(), result, safety_result, envelope.session.id)
    return {
        "schema_version": get_settings().schema_version,
        "ok": True,
        "command": command,
        "result": result,
        "meta": ResponseMeta(model=default_model_name(), latency_ms=latency_ms, session_id=session_id).__dict__,
        "error": None,
    }


def build_success(command: str, result: Dict[str, Any], latency_ms: int = 0, session_id: Optional[str] = None) -> Dict[str, Any]:
    envelope = ResponseEnvelope(
        schema_version=get_settings().schema_version,
        ok=True,
        command=command,
        result=result,
        meta=ResponseMeta(model=default_model_name(), latency_ms=latency_ms, session_id=session_id),
        error=None,
    )
    return envelope.to_dict()
