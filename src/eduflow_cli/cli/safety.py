import json

from eduflow_cli.cli.common import build_success
from eduflow_cli.safety.classifier import classify_text


def run_safety_check(envelope: object) -> dict:
    text = json.dumps(envelope.input, ensure_ascii=False)
    result = classify_text(text)
    return build_success("safety.check", {
        "decision": "blocked" if result["unsafe"] else "allowed",
        "checked_input": result,
        "checked_output": None,
    })
