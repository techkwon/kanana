import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from eduflow_cli.output.structured import validate_structured_payload

ROOT = Path(__file__).resolve().parents[2]


class ReviewCliTests(unittest.TestCase):
    def test_review_command_accepts_stdin_json(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["EDUFLOW_USE_STUB_RUNTIME"] = "1"
        proc = subprocess.run(
            [sys.executable, "-m", "eduflow_cli.main", "review", "--learner-level", "high", "--no-save"],
            cwd=ROOT,
            env=env,
            input='{"input":{"submission":"Essay draft"}}',
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["result"]["input"]["submission"], "Essay draft")
        self.assertIn("structured", payload["result"])
        self.assertEqual(len(payload["result"]["structured"]["strengths"]), 2)

    def test_review_structured_payload_rejects_non_feedback_content(self):
        with self.assertRaises(ValueError):
            validate_structured_payload(
                "review",
                {
                    "strengths": [
                        "빛은 식물의 광합성에 필요한 에너지원입니다.",
                        "식물이 빛을 이용해 유기물을 생성합니다.",
                    ],
                    "improvements": [
                        "빛의 양과 파장을 조절하여 식물 성장 촉진",
                        "인공조명 활용으로 빛 부족 문제 해결",
                    ],
                    "suggestion": "식물에게 적절한 빛 환경을 제공하는 것이 중요합니다.",
                },
            )


if __name__ == "__main__":
    unittest.main()
