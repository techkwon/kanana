import unittest
from unittest.mock import patch

from kanana_cli.cli.common import execute_generation
from kanana_cli.contracts.requests import build_request_envelope
from kanana_cli.output.quality import clean_generated_text
from kanana_cli.output.structured import render_explain_fallback


class OutputQualityTests(unittest.TestCase):
    def test_removes_repeated_decorative_punctuation(self):
        raw = "!! 피타!!! 고!! 라!!! 스! 정리!!"
        cleaned = clean_generated_text(raw)
        self.assertNotIn("!!!", cleaned)
        self.assertNotIn("!!", cleaned)
        self.assertIn("피타고라스", cleaned)

    def test_preserves_line_breaks_between_question_and_answer(self):
        raw = "무엇인가요?\n정답: 식물이 만듭니다."
        cleaned = clean_generated_text(raw)
        self.assertIn("?\n정답:", cleaned)

    def test_explain_fallback_uses_topic_template_for_stub_like_output(self):
        rendered = render_explain_fallback("photosynthesis", "STUB: prompt echo")
        self.assertTrue(rendered.startswith("photosynthesis\n\n개념 설명"))
        self.assertIn("photosynthesis", rendered)


if __name__ == "__main__":
    unittest.main()


class StructuredFallbackRoutingTests(unittest.TestCase):
    def test_explain_retries_structured_generation_before_fallback(self):
        envelope = build_request_envelope(source={"input": {"topic": "fractions"}, "session": {"save": False}})
        with patch("kanana_cli.cli.common.OllamaClient.generate_json") as generate_json, patch(
            "kanana_cli.cli.common.OllamaClient.generate"
        ) as generate:
            generate_json.side_effect = [
                ValueError("bad json"),
                {
                    "title": "분수",
                    "summary": ["전체를 같은 크기로 나눈 것의 일부입니다.", "분자와 분모로 나타냅니다."],
                    "example": "피자를 4조각으로 나누고 1조각을 먹으면 1/4입니다.",
                    "key_points": ["분자는 위에 씁니다.", "분모는 아래에 씁니다.", "같은 크기로 나눈다는 점이 중요합니다."],
                },
            ]

            payload = execute_generation("explain", envelope)

        self.assertTrue(payload["ok"])
        self.assertEqual(generate_json.call_count, 2)
        generate.assert_not_called()
        self.assertEqual(payload["result"]["structured"]["title"], "fractions")

    def test_quiz_uses_cleaned_model_text_before_static_template(self):
        envelope = build_request_envelope(source={"input": {"topic": "광합성"}, "session": {"save": False}})
        with patch("kanana_cli.cli.common.OllamaClient.generate_json", side_effect=ValueError("bad json")), patch(
            "kanana_cli.cli.common.OllamaClient.generate",
            return_value="문제 1: 광합성은 무엇인가요??!!\n\n정답: 식물이 양분을 만듭니다.!!",
        ):
            payload = execute_generation("quiz", envelope)

        self.assertEqual(
            payload["result"]["content"],
            "문제 1: 광합성은 무엇인가요?\n\n정답: 식물이 양분을 만듭니다.",
        )
        self.assertNotIn("기본 뜻을 설명하는 내용입니다", payload["result"]["content"])

    def test_review_falls_back_to_static_template_when_model_text_is_blank(self):
        envelope = build_request_envelope(source={"input": {"submission": "빛은 식물의 음식"}, "session": {"save": False}})
        with patch("kanana_cli.cli.common.OllamaClient.generate_json", side_effect=ValueError("bad json")), patch(
            "kanana_cli.cli.common.OllamaClient.generate", return_value="   \n\n  "
        ):
            payload = execute_generation("review", envelope)

        self.assertIn("바로 적용할 문장", payload["result"]["content"])
        self.assertIn("광합성에 필요한 에너지", payload["result"]["content"])
