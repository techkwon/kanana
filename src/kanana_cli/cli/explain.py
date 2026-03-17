from kanana_cli.cli.common import execute_generation


def run_explain(envelope: object) -> dict:
    return execute_generation("explain", envelope)
