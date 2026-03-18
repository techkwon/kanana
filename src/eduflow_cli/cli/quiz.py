from eduflow_cli.cli.common import execute_generation


def run_quiz(envelope: object) -> dict:
    return execute_generation("quiz", envelope)
