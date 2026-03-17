from kanana_cli.cli.common import execute_generation


def run_review(envelope: object) -> dict:
    return execute_generation("review", envelope)
