from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    schema_version: str
    default_model: str
    ollama_host: str
    request_timeout_seconds: float
    use_stub_runtime: bool
    session_dir: Path


def get_settings() -> Settings:
    return Settings(
        schema_version="1.0",
        default_model=os.getenv("EDUFLOW_MODEL", "neoali/kanana-1.5-2.1b-instruct-2505:latest"),
        ollama_host=os.getenv("EDUFLOW_OLLAMA_HOST", "http://localhost:11434"),
        request_timeout_seconds=float(os.getenv("EDUFLOW_TIMEOUT_SECONDS", "90")),
        use_stub_runtime=os.getenv("EDUFLOW_USE_STUB_RUNTIME", "0") == "1",
        session_dir=Path(os.getenv("EDUFLOW_SESSION_DIR", ".eduflow/sessions")),
    )
