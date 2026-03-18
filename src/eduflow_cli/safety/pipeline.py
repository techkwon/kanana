from typing import Dict, Tuple

from eduflow_cli.contracts.errors import SafetyViolationError
from eduflow_cli.safety.classifier import classify_text
from eduflow_cli.safety.fallbacks import safe_fallback


def evaluate_safety(command: str, text_in: str, text_out: str, learner_level: str, block_on_unsafe: bool = True) -> Tuple[Dict[str, object], str]:
    input_check = classify_text(text_in)
    if input_check["unsafe"] and block_on_unsafe:
        decision = {
            "decision": "blocked_input",
            "checked_input": input_check,
            "checked_output": None,
        }
        raise SafetyViolationError("request blocked by educator safety policy", decision)

    output_check = classify_text(text_out)
    if output_check["unsafe"]:
        safe_text = safe_fallback(command, learner_level)
        return {
            "decision": "replaced_output",
            "checked_input": input_check,
            "checked_output": output_check,
        }, safe_text

    return {
        "decision": "allowed",
        "checked_input": input_check,
        "checked_output": output_check,
    }, text_out
