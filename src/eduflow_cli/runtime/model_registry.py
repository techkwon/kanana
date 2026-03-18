import os

from eduflow_cli.config import get_settings


def default_model_name() -> str:
    return os.getenv("EDUFLOW_MODEL", get_settings().default_model)
