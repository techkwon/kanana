from kanana_cli.cli.common import build_success
from kanana_cli.runtime.healthcheck import run_healthcheck


def run_health(_: object) -> dict:
    return build_success("health", run_healthcheck())
