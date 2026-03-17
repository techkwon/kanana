import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from kanana_cli.output.structured import validate_structured_payload

ROOT = Path(__file__).resolve().parents[2]


class QuizCliTests(unittest.TestCase):
    def test_quiz_command_uses_level_guidance(self):
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        env["KANANA_USE_STUB_RUNTIME"] = "1"
        proc = subprocess.run(
            [sys.executable, "-m", "kanana_cli.main", "quiz", "--topic", "photosynthesis", "--learner-level", "middle", "--no-save"],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertIn("반드시 JSON 객체만 출력하세요", payload["result"]["prompt"])
        self.assertIn('"questions"', payload["result"]["prompt"])
        self.assertIn("question은 한 문장 질문으로 쓰고 물음표로 끝내세요", payload["result"]["prompt"])
        self.assertEqual(len(payload["result"]["structured"]["questions"]), 3)

    def test_quiz_structured_payload_normalizes_labels_and_punctuation(self):
        payload = validate_structured_payload(
            "quiz",
            {
                "questions": [
                    {
                        "question": "문제 1: 광합성은 무엇인가요!!!",
                        "answer": "정답: 식물이 빛으로 양분을 만드는 과정입니다!!!",
                        "explanation": "해설: 햇빛, 물, 이산화탄소를 사용해 스스로 양분을 만듭니다!!!",
                    },
                    {
                        "question": "질문 2 - 광합성은 어디에서 일어나나요",
                        "answer": "답: 잎에서 일어납니다",
                        "explanation": "설명: 잎이 햇빛을 잘 받기 때문입니다",
                    },
                    {
                        "question": "question 3: 광합성이 왜 중요한가요",
                        "answer": "answer: 식물이 자라고 산소를 만드는 데 필요합니다",
                        "explanation": "explanation: 생물의 삶과 연결되기 때문입니다",
                    },
                ]
            },
        )

        self.assertEqual(payload["questions"][0]["question"], "광합성은 무엇인가요?")
        self.assertEqual(payload["questions"][0]["answer"], "식물이 빛으로 양분을 만드는 과정입니다.")
        self.assertEqual(payload["questions"][0]["explanation"], "햇빛, 물, 이산화탄소를 사용해 스스로 양분을 만듭니다.")
        self.assertEqual(payload["questions"][1]["question"], "광합성은 어디에서 일어나나요?")
        self.assertEqual(payload["questions"][2]["question"], "광합성이 왜 중요한가요?")


if __name__ == "__main__":
    unittest.main()
