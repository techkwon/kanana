import argparse
import traceback

from kanana_cli.cli.common import envelope_from_args, load_json_from_stdin
from kanana_cli.cli.explain import run_explain
from kanana_cli.cli.health import run_health
from kanana_cli.cli.kakao import run_kakao_template
from kanana_cli.cli.quiz import run_quiz
from kanana_cli.cli.review import run_review
from kanana_cli.cli.safety import run_safety_check
from kanana_cli.contracts.errors import KananaError
from kanana_cli.output.serializer import emit_json


def _add_common_generation_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input-json")
    parser.add_argument("--topic")
    parser.add_argument("--question")
    parser.add_argument("--submission")
    parser.add_argument("--focus")
    parser.add_argument("--tone")
    parser.add_argument("--learner-level")
    parser.add_argument("--safety-mode")
    parser.add_argument("--allow-unsafe", action="store_true")
    parser.add_argument("--session-id")
    parser.add_argument("--no-save", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="kanana")
    subparsers = parser.add_subparsers(dest="command", required=True)

    health_parser = subparsers.add_parser("health")
    health_parser.add_argument("--input-json")

    for name in ("explain", "quiz", "review", "safety.check", "kakao.template"):
        subparser = subparsers.add_parser(name)
        _add_common_generation_args(subparser)

    return parser


def _dispatch(args: argparse.Namespace) -> dict:
    stdin_payload = load_json_from_stdin()
    if args.command == "health":
        return run_health(None)

    envelope = envelope_from_args(args, stdin_payload=stdin_payload)
    if args.command == "explain":
        return run_explain(envelope)
    if args.command == "quiz":
        return run_quiz(envelope)
    if args.command == "review":
        return run_review(envelope)
    if args.command == "safety.check":
        return run_safety_check(envelope)
    if args.command == "kakao.template":
        return run_kakao_template(envelope)
    raise RuntimeError(f"Unsupported command: {args.command}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = _dispatch(args)
        emit_json(payload)
        return 0
    except KananaError as exc:
        emit_json({
            "schema_version": "1.0",
            "ok": False,
            "command": getattr(args, "command", "unknown"),
            "result": {},
            "meta": {"model": "kanana-nano", "latency_ms": 0, "session_id": None},
            "error": exc.to_error_detail().to_dict(),
        })
        return exc.exit_code
    except Exception as exc:  # pragma: no cover
        emit_json({
            "schema_version": "1.0",
            "ok": False,
            "command": getattr(args, "command", "unknown"),
            "result": {},
            "meta": {"model": "kanana-nano", "latency_ms": 0, "session_id": None},
            "error": {"code": "internal_error", "message": str(exc), "details": {"traceback": traceback.format_exc()}},
        })
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
