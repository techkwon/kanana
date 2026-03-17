import json
import tempfile
import unittest
from pathlib import Path

from kanana_cli.qa_harness import (
    CaseResult,
    load_cases,
    load_taxonomy,
    score_output,
    summarize,
    write_report,
)


class QaHarnessTests(unittest.TestCase):
    def test_scores_explain_output_high_when_structure_and_keywords_match(self):
        case = {
            "id": "explain-test",
            "command": "explain",
            "expected_keywords": ["개념 설명", "예시", "핵심 정리"],
            "forbidden_keywords": ["!!"],
        }
        payload = {
            "ok": True,
            "result": {
                "content": (
                    "피타고라스 정리\n\n"
                    "개념 설명\n- 직각삼각형에서 빗변을 구합니다.\n- 제곱의 합으로 설명합니다.\n\n"
                    "예시\n- 변의 길이가 3, 4이면 빗변은 5입니다.\n\n"
                    "핵심 정리\n1. 직각삼각형에 적용됩니다.\n2. 빗변을 구할 수 있습니다.\n3. 도형 문제에 씁니다."
                )
            },
        }
        score, issues = score_output(case, payload, 0)
        self.assertGreaterEqual(score, 85)
        self.assertEqual(issues, [])

    def test_load_taxonomy_reads_misconception_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "taxonomy.json"
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "misconceptions": [
                            {
                                "id": "science.photosynthesis.light-as-food",
                                "domain": "science",
                                "label": "빛을 식물의 음식으로 오해",
                                "case_ids": ["review-001"],
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            taxonomy = load_taxonomy(path)

        self.assertEqual(taxonomy["version"], 1)
        self.assertEqual(taxonomy["misconceptions"][0]["id"], "science.photosynthesis.light-as-food")
        self.assertIn("science.photosynthesis.light-as-food", taxonomy["by_id"])

    def test_load_cases_reads_grouped_directory_and_applies_metadata(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "review").mkdir(parents=True)
            (root / "review" / "science.json").write_text(
                json.dumps(
                    {
                        "domain": "science",
                        "command": "review",
                        "cases": [
                            {
                                "id": "review-001",
                                "submission": "빛은 식물이 먹는 음식이다.",
                                "learner_level": "high",
                                "misconception_id": "concept-reversal",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            taxonomy = {
                "misconceptions": [
                    {
                        "id": "science.photosynthesis.light-as-food",
                        "case_ids": ["review-001"],
                    }
                ],
                "case_index": {"review-001": ["science.photosynthesis.light-as-food"]},
            }
            cases = load_cases(root, taxonomy=taxonomy)

        self.assertEqual(len(cases), 1)
        self.assertEqual(cases[0]["command"], "review")
        self.assertEqual(cases[0]["domain"], "science")
        self.assertEqual(cases[0]["group_id"], "review:science")
        self.assertTrue(cases[0]["source_path"].endswith("review/science.json"))
        self.assertEqual(
            cases[0]["misconception_ids"],
            ["concept-reversal", "science.photosynthesis.light-as-food"],
        )

    def test_summary_aggregates_group_and_misconception_breakdowns(self):
        results = [
            CaseResult(
                case_id="review-001",
                command="review",
                domain="science",
                group_id="review:science",
                group_label="review / science",
                source_path="review/science.json",
                misconception_ids=["concept-reversal"],
                score=90,
                passed=True,
                latency_ms=10,
                return_code=0,
                issues=[],
                content_preview="ok",
            ),
            CaseResult(
                case_id="review-002",
                command="review",
                domain="science",
                group_id="review:science",
                group_label="review / science",
                source_path="review/science.json",
                misconception_ids=[],
                score=70,
                passed=False,
                latency_ms=20,
                return_code=0,
                issues=["low"],
                content_preview="bad",
            ),
        ]
        summary = summarize(results)
        self.assertEqual(summary["total_cases"], 2)
        self.assertEqual(summary["passed_cases"], 1)
        self.assertEqual(summary["tagged_cases"], 1)
        self.assertIn("review", summary["by_command"])
        self.assertIn("review:science", summary["by_group"])
        self.assertIn("concept-reversal", summary["by_misconception"])
        self.assertEqual(summary["by_group"]["review:science"]["count"], 2)
        self.assertEqual(summary["by_group"]["review:science"]["failed"], 1)

    def test_write_report_includes_cases_path_taxonomy_and_group_summary(self):
        results = [
            CaseResult(
                case_id="review-001",
                command="review",
                domain="science",
                group_id="review:science",
                group_label="review / science",
                source_path="review/science.json",
                misconception_ids=["concept-reversal"],
                score=92,
                passed=True,
                latency_ms=10,
                return_code=0,
                issues=[],
                content_preview="ok",
            )
        ]
        taxonomy = {
            "version": 1,
            "misconceptions": [
                {
                    "id": "concept-reversal",
                    "domain": "science",
                    "label": "개념 반전",
                    "case_ids": ["review-001"],
                }
            ],
            "by_id": {
                "concept-reversal": {
                    "id": "concept-reversal",
                    "domain": "science",
                    "label": "개념 반전",
                    "case_ids": ["review-001"],
                }
            },
        }

        report_path = write_report("stub", results, taxonomy)
        payload = json.loads(Path(report_path).read_text(encoding="utf-8"))

        self.assertEqual(payload["taxonomy"]["count"], 1)
        self.assertEqual(payload["summary"]["by_group"]["review:science"]["passed"], 1)
        self.assertEqual(payload["groups"][0]["group_id"], "review:science")

        Path(report_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
