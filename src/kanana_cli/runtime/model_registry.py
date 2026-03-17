import os

from kanana_cli.config import get_settings


def default_model_name() -> str:
    return os.getenv("KANANA_MODEL", get_settings().default_model)
