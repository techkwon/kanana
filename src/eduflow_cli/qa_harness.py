import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES_PATH = ROOT / "qa" / "cases"
DEFAULT_TAXONOMY_PATH = ROOT / "qa" / "misconception-taxonomy.json"
DEFAULT_REPORT_DIR = ROOT / ".eduflow" / "reports"

_REPEATED_PUNCT = re.compile(r"([!！?？~])\1+")
_HANGUL = re.compile(r"[가-힣]")
_LATIN = re.compile(r"[A-Za-z]")


@dataclass
class CaseResult:
    case_id: str
    command: str
    domain: str
    group_id: str
    group_label: str
    source_path: Optional[str]
    misconception_ids: List[str]
    score: int
    passed: bool
    latency_ms: Optional[int]
    return_code: int
    issues: List[str]
    content_preview: str


def _string_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    return []


def _dedupe(items: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def _prepare_taxonomy(taxonomy: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if taxonomy is None:
        return {"version": 1, "misconceptions": [], "by_id": {}, "case_index": {}, "path": None}
    if "by_id" in taxonomy and "case_index" in taxonomy:
        return taxonomy

    misconceptions = taxonomy.get("misconceptions", [])
    by_id: Dict[str, Dict[str, Any]] = {}
    case_index: Dict[str, List[str]] = {}
    normalized_items: List[Dict[str, Any]] = []
    for item in misconceptions:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            continue
        normalized = dict(item)
        normalized["case_ids"] = _string_list(normalized.get("case_ids"))
        normalized_items.append(normalized)
        by_id[normalized["id"]] = normalized
        for case_id in normalized["case_ids"]:
            case_index.setdefault(case_id, []).append(normalized["id"])

    prepared = dict(taxonomy)
    prepared["misconceptions"] = normalized_items
    prepared["by_id"] = by_id
    prepared["case_index"] = case_index
    prepared.setdefault("version", 1)
    prepared.setdefault("path", None)
    return prepared


def load_taxonomy(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "version": 1,
            "misconceptions": [],
            "by_id": {},
            "case_index": {},
            "path": str(path),
        }

    data = json.loads(path.read_text(encoding="utf-8"))
    misconceptions = data.get("misconceptions", [])
    if not isinstance(misconceptions, list):
        raise ValueError("Taxonomy file must contain a 'misconceptions' list")

    by_id: Dict[str, Dict[str, Any]] = {}
    case_index: Dict[str, List[str]] = {}
    normalized_items: List[Dict[str, Any]] = []
    for item in misconceptions:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ValueError("Each taxonomy entry must be an object with an id")
        normalized = dict(item)
        normalized["case_ids"] = _string_list(normalized.get("case_ids"))
        normalized_items.append(normalized)
        by_id[normalized["id"]] = normalized
        for case_id in normalized["case_ids"]:
            case_index.setdefault(case_id, []).append(normalized["id"])

    return _prepare_taxonomy({
        "version": data.get("version", 1),
        "misconceptions": normalized_items,
        "by_id": by_id,
        "case_index": case_index,
        "path": str(path),
    })


def _normalize_case(
    case: Dict[str, Any],
    *,
    command: Optional[str] = None,
    domain: Optional[str] = None,
    source_path: Optional[Path] = None,
    taxonomy: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    normalized = dict(case)
    normalized["command"] = normalized.get("command") or command
    normalized["domain"] = normalized.get("domain") or domain or "general"
    normalized["group_id"] = normalized.get("group_id") or f"{normalized['command']}:{normalized['domain']}"
    normalized["group_label"] = normalized.get("group_label") or f"{normalized['command']} / {normalized['domain']}"

    explicit_ids = _string_list(normalized.get("misconception_ids"))
    if not explicit_ids and isinstance(normalized.get("misconception_id"), str):
        explicit_ids = [normalized["misconception_id"]]
    prepared_taxonomy = _prepare_taxonomy(taxonomy)
    taxonomy_ids = prepared_taxonomy["case_index"].get(normalized["id"], [])
    normalized["misconception_ids"] = _dedupe([*explicit_ids, *taxonomy_ids])

    if source_path is not None:
        normalized["source_path"] = source_path.as_posix()
    return normalized


def _load_group_file(
    path: Path,
    taxonomy: Optional[Dict[str, Any]] = None,
    source_root: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"QA group file must contain an object: {path}")

    command = data.get("command")
    domain = data.get("domain") or path.stem
    cases = data.get("cases")
    if not isinstance(cases, list):
        raise ValueError(f"QA group file must contain a cases list: {path}")

    display_path = path if source_root is None else path.relative_to(source_root)
    return [
        _normalize_case(case, command=command, domain=domain, source_path=display_path, taxonomy=taxonomy)
        for case in cases
    ]


def load_cases(path: Path, taxonomy: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    if path.is_dir():
        cases: List[Dict[str, Any]] = []
        for group_file in sorted(path.rglob("*.json")):
            cases.extend(_load_group_file(group_file, taxonomy=taxonomy, source_root=path))
        if not cases:
            raise ValueError("QA cases directory does not contain any JSON group files")
        return cases

    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [_normalize_case(case, taxonomy=taxonomy) for case in data]
    if isinstance(data, dict) and isinstance(data.get("cases"), list):
        return [
            _normalize_case(
                case,
                command=data.get("command"),
                domain=data.get("domain"),
                source_path=path,
                taxonomy=taxonomy,
            )
            for case in data["cases"]
        ]
    raise ValueError("QA cases file must contain a list or a grouped object with a cases list")


def build_case_input(case: Dict[str, Any]) -> Dict[str, Any]:
    input_payload: Dict[str, Any] = {}
    if "topic" in case:
        input_payload["topic"] = case["topic"]
    if "submission" in case:
        input_payload["submission"] = case["submission"]
    if "question" in case:
        input_payload["question"] = case["question"]
    return {
        "input": input_payload,
        "audience": {"learner_level": case.get("learner_level", "elementary")},
        "session": {"save": False},
    }


def _count(pattern: re.Pattern[str], text: str) -> int:
    return len(pattern.findall(text))


def _language_score(text: str) -> tuple[int, List[str]]:
    hangul_count = _count(_HANGUL, text)
    latin_count = _count(_LATIN, text)
    if hangul_count == 0:
        return 0, ["한글 비율이 너무 낮습니다."]
    if latin_count == 0:
        return 10, []
    ratio = hangul_count / (hangul_count + latin_count)
    if ratio >= 0.8:
        return 10, []
    if ratio >= 0.6:
        return 6, ["영문 비율이 다소 높습니다."]
    return 0, ["영문 비율이 너무 높습니다."]


def _structure_score(command: str, content: str) -> tuple[int, List[str]]:
    issues: List[str] = []
    if command == "explain":
        required = ["개념 설명", "예시", "핵심 정리"]
        missing = [label for label in required if label not in content]
        if missing:
            issues.append(f"설명 구조 누락: {', '.join(missing)}")
            return 0, issues
        if "1." not in content or "2." not in content or "3." not in content:
            issues.append("핵심 정리 번호 형식이 부족합니다.")
            return 6, issues
        return 20, []

    if command == "quiz":
        q_count = content.count("문제 ")
        a_count = content.count("정답:")
        e_count = content.count("해설:")
        if min(q_count, a_count, e_count) < 3:
            issues.append("퀴즈의 문제/정답/해설 구조가 3개씩 갖춰지지 않았습니다.")
            return 0, issues
        return 20, []

    if command == "review":
        required = ["잘한 점", "고칠 점", "바로 적용할 문장"]
        missing = [label for label in required if label not in content]
        if missing:
            issues.append(f"리뷰 구조 누락: {', '.join(missing)}")
            return 0, issues
        return 20, []

    return 10, []


def _keyword_score(case: Dict[str, Any], content: str) -> tuple[int, List[str]]:
    issues: List[str] = []
    expected = case.get("expected_keywords", [])
    forbidden = case.get("forbidden_keywords", [])

    score = 0
    if expected:
        matched = [keyword for keyword in expected if keyword in content]
        score += int(20 * (len(matched) / len(expected)))
        missing = [keyword for keyword in expected if keyword not in matched]
        if missing:
            issues.append(f"기대 키워드 일부 누락: {', '.join(missing)}")
    else:
        score += 20

    forbidden_hits = [keyword for keyword in forbidden if keyword in content]
    if forbidden_hits:
        issues.append(f"금지 키워드 발견: {', '.join(forbidden_hits)}")
        score = max(0, score - 10)

    return score, issues


def score_output(case: Dict[str, Any], payload: Dict[str, Any], return_code: int) -> tuple[int, List[str]]:
    issues: List[str] = []
    if return_code != 0 or not payload.get("ok"):
        issues.append("명령 실행 실패 또는 ok=false 입니다.")
        return 0, issues

    result = payload.get("result") or {}
    content = result.get("content", "")
    if not isinstance(content, str) or not content.strip():
        issues.append("출력 내용이 비어 있습니다.")
        return 0, issues

    score = 20
    if _REPEATED_PUNCT.search(content):
        issues.append("반복 구두점이 남아 있습니다.")
    else:
        score += 10

    language_score, language_issues = _language_score(content)
    score += language_score
    issues.extend(language_issues)

    structure_score, structure_issues = _structure_score(case["command"], content)
    score += structure_score
    issues.extend(structure_issues)

    keyword_score, keyword_issues = _keyword_score(case, content)
    score += keyword_score
    issues.extend(keyword_issues)

    if len(content) >= 80:
        score += 10
    else:
        issues.append("출력 길이가 짧습니다.")

    return min(score, 100), issues


def run_case(case: Dict[str, Any], use_stub: bool) -> CaseResult:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    env["EDUFLOW_USE_STUB_RUNTIME"] = "1" if use_stub else "0"

    input_json = json.dumps(build_case_input(case), ensure_ascii=False)
    command = [
        sys.executable,
        "-m",
        "eduflow_cli.main",
        case["command"],
        "--no-save",
    ]

    proc = subprocess.run(
        command,
        cwd=ROOT,
        env=env,
        input=input_json,
        capture_output=True,
        text=True,
        timeout=180,
    )
    payload = json.loads(proc.stdout or "{}")
    score, issues = score_output(case, payload, proc.returncode)
    meta = payload.get("meta") or {}
    content = ((payload.get("result") or {}).get("content") or "").strip()
    return CaseResult(
        case_id=case["id"],
        command=case["command"],
        domain=case.get("domain", "general"),
        group_id=case.get("group_id", f"{case['command']}:{case.get('domain', 'general')}"),
        group_label=case.get("group_label", f"{case['command']} / {case.get('domain', 'general')}"),
        source_path=case.get("source_path"),
        misconception_ids=_string_list(case.get("misconception_ids")),
        score=score,
        passed=score >= 85 and proc.returncode == 0 and bool(payload.get("ok")),
        latency_ms=meta.get("latency_ms"),
        return_code=proc.returncode,
        issues=issues,
        content_preview=content[:200],
    )


def _bucket() -> Dict[str, Any]:
    return {"count": 0, "passed": 0, "scores": []}


def _finalize_bucket(bucket: Dict[str, Any]) -> Dict[str, Any]:
    bucket["failed"] = bucket["count"] - bucket["passed"]
    bucket["avg_score"] = round(sum(bucket["scores"]) / len(bucket["scores"]), 2) if bucket["scores"] else 0
    del bucket["scores"]
    return bucket


def summarize(results: List[CaseResult], taxonomy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    total = len(results)
    passed = sum(1 for item in results if item.passed)
    avg_score = round(sum(item.score for item in results) / total, 2) if total else 0

    by_command: Dict[str, Dict[str, Any]] = {}
    by_group: Dict[str, Dict[str, Any]] = {}
    by_misconception: Dict[str, Dict[str, Any]] = {}
    issue_counts: Dict[str, int] = {}
    tagged_cases = 0

    prepared_taxonomy = _prepare_taxonomy(taxonomy)
    taxonomy_by_id = prepared_taxonomy.get("by_id", {})

    for item in results:
        command_bucket = by_command.setdefault(item.command, _bucket())
        command_bucket["count"] += 1
        command_bucket["passed"] += int(item.passed)
        command_bucket["scores"].append(item.score)

        group_bucket = by_group.setdefault(
            item.group_id,
            {
                "group_label": item.group_label,
                "command": item.command,
                "domain": item.domain,
                **_bucket(),
            },
        )
        group_bucket["count"] += 1
        group_bucket["passed"] += int(item.passed)
        group_bucket["scores"].append(item.score)

        if item.misconception_ids:
            tagged_cases += 1
        for issue in item.issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        for misconception_id in item.misconception_ids:
            meta = taxonomy_by_id.get(misconception_id, {})
            misconception_bucket = by_misconception.setdefault(
                misconception_id,
                {
                    "label": meta.get("label", misconception_id),
                    "domain": meta.get("domain", item.domain),
                    "count": 0,
                    "passed": 0,
                    "scores": [],
                    "case_ids": [],
                },
            )
            misconception_bucket["count"] += 1
            misconception_bucket["passed"] += int(item.passed)
            misconception_bucket["scores"].append(item.score)
            misconception_bucket["case_ids"].append(item.case_id)

    for bucket in by_command.values():
        _finalize_bucket(bucket)
    for bucket in by_group.values():
        _finalize_bucket(bucket)
    for bucket in by_misconception.values():
        bucket["case_ids"] = sorted(bucket["case_ids"])
        _finalize_bucket(bucket)

    top_issues = [
        {"issue": issue, "count": count}
        for issue, count in sorted(issue_counts.items(), key=lambda item: (-item[1], item[0]))
    ]

    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": total - passed,
        "average_score": avg_score,
        "tagged_cases": tagged_cases,
        "untagged_cases": total - tagged_cases,
        "by_command": by_command,
        "by_group": by_group,
        "by_misconception": by_misconception,
        "top_issues": top_issues,
    }


def _group_results(results: List[CaseResult]) -> List[Dict[str, Any]]:
    grouped: Dict[str, Dict[str, Any]] = {}
    for result in results:
        entry = grouped.setdefault(
            result.group_id,
            {
                "group_id": result.group_id,
                "group_label": result.group_label,
                "command": result.command,
                "domain": result.domain,
                "results": [],
            },
        )
        entry["results"].append(asdict(result))

    ordered_groups: List[Dict[str, Any]] = []
    for group_id in sorted(grouped):
        entry = grouped[group_id]
        group_results = [CaseResult(**item) for item in entry["results"]]
        entry["summary"] = summarize(group_results)
        ordered_groups.append(entry)
    return ordered_groups


def write_report(mode: str, results: List[CaseResult], taxonomy: Optional[Dict[str, Any]] = None) -> Path:
    DEFAULT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = DEFAULT_REPORT_DIR / f"quality-{mode}-{timestamp}.json"
    payload = {
        "generated_at": timestamp,
        "mode": mode,
        "summary": summarize(results, taxonomy=taxonomy),
        "taxonomy": {
            "path": None if taxonomy is None else _prepare_taxonomy(taxonomy).get("path"),
            "version": None if taxonomy is None else _prepare_taxonomy(taxonomy).get("version"),
            "count": 0 if taxonomy is None else len(_prepare_taxonomy(taxonomy).get("misconceptions", [])),
            "misconceptions": [] if taxonomy is None else _prepare_taxonomy(taxonomy).get("misconceptions", []),
        },
        "groups": _group_results(results),
        "results": [asdict(result) for result in results],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="eduflow-qa")
    parser.add_argument("--cases", default=str(DEFAULT_CASES_PATH))
    parser.add_argument("--taxonomy", default=str(DEFAULT_TAXONOMY_PATH))
    parser.add_argument("--mode", choices=("stub", "live"), default="stub")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--min-score", type=int, default=85)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    taxonomy = _prepare_taxonomy(load_taxonomy(Path(args.taxonomy)))
    cases = load_cases(Path(args.cases), taxonomy=taxonomy)
    if args.limit:
        cases = cases[: args.limit]

    results = [run_case(case, use_stub=args.mode == "stub") for case in cases]
    summary = summarize(results, taxonomy=taxonomy)
    report_path = write_report(args.mode, results, taxonomy=taxonomy)

    output = {
        "ok": summary["failed_cases"] == 0,
        "mode": args.mode,
        "summary": summary,
        "taxonomy": {
            "path": taxonomy.get("path"),
            "version": taxonomy.get("version"),
            "count": len(taxonomy.get("misconceptions", [])),
        },
        "report_path": str(report_path),
        "failed_cases": [asdict(result) for result in results if result.score < args.min_score or not result.passed],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
