from eduflow_cli.runtime.model_registry import default_model_name
from eduflow_cli.runtime.ollama_client import OllamaClient


def _normalize_model_name(name: str) -> str:
    return name[:-7] if name.endswith(":latest") else name


def run_healthcheck() -> dict:
    client = OllamaClient()
    target_model = default_model_name()
    try:
        models = client.list_models().get("models", [])
        reachable = True
    except Exception as exc:
        return {
            "reachable": False,
            "model_present": False,
            "ready": False,
            "target_model": target_model,
            "details": str(exc),
        }

    names = {
        item.get("name")
        for item in models
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }
    normalized_names = {_normalize_model_name(name) for name in names}
    normalized_target = _normalize_model_name(target_model)
    model_present = target_model in names or normalized_target in normalized_names
    return {
        "reachable": reachable,
        "model_present": model_present,
        "ready": reachable and model_present,
        "target_model": target_model,
    }
