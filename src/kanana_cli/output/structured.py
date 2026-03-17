import re
from typing import Any, Dict, List, Optional

from kanana_cli.domain.knowledge import explain_hint_for_topic
from kanana_cli.output.quality import clean_generated_text


def _normalize_topic(topic: str) -> str:
    normalized = clean_generated_text(topic or "").strip()
    return normalized or "학습 주제"


def _default_explain_title(topic: str) -> str:
    return _normalize_topic(topic)


def structured_prompt_for(command: str, topic: str, guidance: str) -> str:
    if command == "explain":
        hint = explain_hint_for_topic(topic)
        hint_text = ""
        if hint is not None:
            keywords = ", ".join(hint["keywords"])  # type: ignore[index]
            hint_text = f"반드시 포함할 핵심 단어: {keywords}. "
        return (
            f"주제: {topic}\n"
            f"대상 가이드: {guidance}\n"
            "반드시 JSON 객체만 출력하세요.\n"
            '스키마: {"title":"", "summary":["", ""], "example":"", "key_points":["", "", ""]}\n'
            "title은 반드시 주제를 그대로 반영해야 합니다. "
            "summary, example, key_points는 모두 주제와 직접 연결된 내용이어야 합니다. "
            f"{hint_text}"
            "모든 값은 한국어 문자열이어야 합니다. 느낌표, 장식 기호, 불필요한 영어를 쓰지 마세요."
        )
    if command == "quiz":
        return (
            f"주제: {topic}\n"
            f"대상 가이드: {guidance}\n"
            "반드시 JSON 객체만 출력하세요.\n"
            '스키마: {"questions":[{"question":"","answer":"","explanation":""},{"question":"","answer":"","explanation":""},{"question":"","answer":"","explanation":""}]}\n'
            "모든 값은 한국어 문자열이어야 합니다. 문항은 정확히 3개여야 합니다. "
            "question은 한 문장 질문으로 쓰고 물음표로 끝내세요. "
            "answer와 explanation은 완전한 문장으로 쓰고 마침표로 끝내세요. "
            "번호, 따옴표, 불릿, 장식 기호를 넣지 마세요."
        )
    if command == "review":
        return (
            f"학습자 작업: {topic}\n"
            f"대상 가이드: {guidance}\n"
            "반드시 JSON 객체만 출력하세요.\n"
            '스키마: {"strengths":["", ""], "improvements":["", ""], "suggestion":""}\n'
            "모든 값은 한국어 문자열이어야 합니다. 공손하고 차분한 톤을 유지하세요."
        )
    raise ValueError(f"Unsupported structured command: {command}")


def _ensure_string_list(value: Any, expected_length: Optional[int] = None) -> List[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError("Expected a non-empty string list")
    if expected_length is not None and len(value) != expected_length:
        raise ValueError(f"Expected {expected_length} items")
    return [clean_generated_text(item).strip() for item in value]


def _normalize_quiz_field(value: str, prefix: str, ending: str) -> str:
    normalized = clean_generated_text(value).strip()
    normalized = re.sub(rf"^{prefix}\s*\d*\s*[:：.\-]?\s*", "", normalized, flags=re.IGNORECASE)
    normalized = re.sub(r"\s+", " ", normalized).strip(" -•·\t")
    normalized = normalized.rstrip(".?!~…")
    if not normalized:
        raise ValueError("Quiz field became empty after normalization")
    return f"{normalized}{ending}"


def _normalize_quiz_question(value: str) -> str:
    return _normalize_quiz_field(value, prefix=r"(?:문제|질문|question)", ending="?")


def _normalize_quiz_answer(value: str) -> str:
    return _normalize_quiz_field(value, prefix=r"(?:정답|답|answer)", ending=".")


def _normalize_quiz_explanation(value: str) -> str:
    return _normalize_quiz_field(value, prefix=r"(?:해설|설명|explanation)", ending=".")


_REVIEW_FEEDBACK_KEYWORDS = (
    "문장",
    "표현",
    "설명",
    "근거",
    "예시",
    "구성",
    "흐름",
    "명확",
    "정확",
    "용어",
    "핵심",
    "논리",
    "수정",
    "보완",
    "추가",
    "다듬",
    "고치",
    "바꾸",
)


def _looks_like_review_feedback(text: str) -> bool:
    normalized = clean_generated_text(text).strip()
    return any(keyword in normalized for keyword in _REVIEW_FEEDBACK_KEYWORDS)


def validate_structured_payload(command: str, payload: Dict[str, Any], topic: Optional[str] = None) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Structured payload must be an object")

    if command == "explain":
        title = payload.get("title")
        example = payload.get("example")
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Explain payload requires title")
        if not isinstance(example, str) or not example.strip():
            raise ValueError("Explain payload requires example")
        normalized_topic = topic or clean_generated_text(title).strip()
        hint = explain_hint_for_topic(normalized_topic)
        if hint is not None:
            joined = " ".join(
                [
                    clean_generated_text(title),
                    clean_generated_text(example),
                    *payload.get("summary", []),
                    *payload.get("key_points", []),
                ]
            )
            if not all(keyword in joined for keyword in hint["keywords"]):  # type: ignore[index]
                return {
                    "title": _default_explain_title(normalized_topic),
                    "summary": list(hint["summary"]),  # type: ignore[arg-type]
                    "example": str(hint["example"]),
                    "key_points": list(hint["key_points"]),  # type: ignore[arg-type]
                }
        return {
            "title": _default_explain_title(normalized_topic),
            "summary": _ensure_string_list(payload.get("summary"), expected_length=2),
            "example": clean_generated_text(example).strip(),
            "key_points": _ensure_string_list(payload.get("key_points"), expected_length=3),
        }

    if command == "quiz":
        questions = payload.get("questions")
        if not isinstance(questions, list) or len(questions) != 3:
            raise ValueError("Quiz payload requires exactly 3 questions")
        normalized_questions = []
        for item in questions:
            if not isinstance(item, dict):
                raise ValueError("Quiz question must be an object")
            question = item.get("question")
            answer = item.get("answer")
            explanation = item.get("explanation")
            if not all(isinstance(v, str) and v.strip() for v in (question, answer, explanation)):
                raise ValueError("Quiz question fields must be non-empty strings")
            normalized_questions.append(
                {
                    "question": _normalize_quiz_question(question),
                    "answer": _normalize_quiz_answer(answer),
                    "explanation": _normalize_quiz_explanation(explanation),
                }
            )
        return {"questions": normalized_questions}

    if command == "review":
        suggestion = payload.get("suggestion")
        if not isinstance(suggestion, str) or not suggestion.strip():
            raise ValueError("Review payload requires suggestion")
        strengths = _ensure_string_list(payload.get("strengths"), expected_length=2)
        improvements = _ensure_string_list(payload.get("improvements"), expected_length=2)
        normalized_suggestion = clean_generated_text(suggestion).strip()
        if not all(_looks_like_review_feedback(item) for item in strengths + improvements):
            raise ValueError("Review payload must contain feedback-oriented sentences")
        if not any(keyword in normalized_suggestion for keyword in ("쓰면", "고치", "바꾸", "수정", "정확", "보세요")):
            raise ValueError("Review suggestion must contain actionable revision guidance")
        return {
            "strengths": strengths,
            "improvements": improvements,
            "suggestion": normalized_suggestion,
        }

    raise ValueError(f"Unsupported structured command: {command}")


def render_structured_payload(command: str, payload: Dict[str, Any]) -> str:
    if command == "explain":
        lines = [
            payload["title"],
            "",
            "개념 설명",
            f"- {payload['summary'][0]}",
            f"- {payload['summary'][1]}",
            "",
            "예시",
            f"- {payload['example']}",
            "",
            "핵심 정리",
            f"1. {payload['key_points'][0]}",
            f"2. {payload['key_points'][1]}",
            f"3. {payload['key_points'][2]}",
        ]
        return "\n".join(lines)

    if command == "quiz":
        lines: List[str] = []
        for idx, item in enumerate(payload["questions"], start=1):
            lines.extend(
                [
                    f"문제 {idx}: {item['question']}",
                    f"정답: {item['answer']}",
                    f"해설: {item['explanation']}",
                    "",
                ]
            )
        return "\n".join(lines).strip()

    if command == "review":
        lines = [
            "잘한 점",
            f"1. {payload['strengths'][0]}",
            f"2. {payload['strengths'][1]}",
            "",
            "고칠 점",
            f"1. {payload['improvements'][0]}",
            f"2. {payload['improvements'][1]}",
            "",
            "바로 적용할 문장",
            payload["suggestion"],
        ]
        return "\n".join(lines)

    raise ValueError(f"Unsupported structured command: {command}")


def render_explain_fallback(topic: str, raw_text: str) -> str:
    if explain_hint_for_topic(topic) is not None:
        return render_explain_template(topic)
    compact = raw_text.replace("\r\n", "\n").strip()
    if not compact or compact.startswith("STUB:") or "출력 규칙:" in compact or compact.startswith("주제:"):
        return render_explain_template(topic)
    candidates = [
        clean_generated_text(segment).strip(" -")
        for segment in re.split(r"(?<=[.!?다요])\s+|\n+", compact)
        if segment.strip()
    ]
    sentences = []
    for segment in candidates:
        if len(segment) < 12:
            continue
        if segment in {"!", "?", "개념 설명", "핵심 정리"}:
            continue
        if segment.endswith("란?"):
            continue
        sentences.append(segment)

    if len(sentences) < 2:
        return render_explain_template(topic)

    summary = sentences[:2] if len(sentences) >= 2 else sentences
    example = next(
        (sentence for sentence in sentences if "예시" in sentence or "예를 들어" in sentence or any(ch.isdigit() for ch in sentence)),
        summary[-1] if summary else compact,
    )
    key_points = []
    for sentence in sentences:
        if sentence not in key_points:
            key_points.append(sentence)
        if len(key_points) == 3:
            break

    while len(summary) < 2:
        summary.append("핵심 개념을 짧게 다시 설명하세요.")
    while len(key_points) < 3:
        key_points.append(key_points[-1] if key_points else "핵심 개념을 다시 정리하세요.")

    return "\n".join(
        [
            topic,
            "",
            "개념 설명",
            f"- {summary[0]}",
            f"- {summary[1]}",
            "",
            "예시",
            f"- {example}",
            "",
            "핵심 정리",
            f"1. {key_points[0]}",
            f"2. {key_points[1]}",
            f"3. {key_points[2]}",
        ]
    )


def render_explain_template(topic: str) -> str:
    title = _default_explain_title(topic)
    hint = explain_hint_for_topic(title)
    if hint is not None:
        return "\n".join(
            [
                title,
                "",
                "개념 설명",
                f"- {hint['summary'][0]}",
                f"- {hint['summary'][1]}",
                "",
                "예시",
                f"- {hint['example']}",
                "",
                "핵심 정리",
                f"1. {hint['key_points'][0]}",
                f"2. {hint['key_points'][1]}",
                f"3. {hint['key_points'][2]}",
            ]
        )
    return "\n".join(
        [
            title,
            "",
            "개념 설명",
            f"- {title}의 뜻을 먼저 짧게 이해하면 다음 내용을 배우기 쉽습니다.",
            f"- {title}은(는) 핵심 특징과 쓰임을 함께 보면 더 잘 기억됩니다.",
            "",
            "예시",
            f"- 수업에서는 {title}과(와) 관련된 쉬운 사례 하나를 먼저 떠올리면 이해가 빨라집니다.",
            "",
            "핵심 정리",
            f"1. {title}의 기본 뜻을 한 문장으로 말할 수 있어야 합니다.",
            f"2. {title}의 중요한 특징을 두세 가지로 정리하면 좋습니다.",
            f"3. {title}을(를) 실제 예와 연결하면 오래 기억할 수 있습니다.",
        ]
    )


def render_quiz_fallback(raw_text: str) -> str:
    compact = clean_generated_text(raw_text)
    return compact


def render_quiz_template(topic: str) -> str:
    return "\n".join(
        [
            f"문제 1: {topic}은 무엇인가요?",
            f"정답: {topic}의 뜻을 한 문장으로 설명한 내용입니다.",
            f"해설: 먼저 {topic}의 기본 뜻을 이해하면 다음 내용을 더 쉽게 배울 수 있습니다.",
            "",
            f"문제 2: {topic}이 왜 중요한가요?",
            f"정답: {topic}은 관련 개념을 이해하는 바탕이 됩니다.",
            f"해설: 핵심 이유를 함께 떠올리면 내용을 더 오래 기억할 수 있습니다.",
            "",
            f"문제 3: {topic}은 어디에서 볼 수 있나요?",
            f"정답: 수업 활동이나 일상 사례에서 찾아볼 수 있습니다.",
            f"해설: 배운 내용을 실제 장면과 연결하면 개념이 더 또렷해집니다.",
        ]
    )


def render_review_fallback(raw_text: str) -> str:
    compact = clean_generated_text(raw_text)
    required = ("잘한 점", "고칠 점", "바로 적용할 문장")
    if not all(label in compact for label in required):
        return ""
    return compact


def render_review_template(submission: str) -> str:
    suggestion = "핵심 개념을 더 정확하게 설명하고, 이유를 한 문장 덧붙여 보세요."
    if "빛" in submission and "음식" in submission:
        suggestion = "빛은 식물이 먹는 음식이 아니라, 광합성에 필요한 에너지라고 쓰면 더 정확합니다."

    return "\n".join(
        [
            "잘한 점",
            "1. 한 문장으로 핵심 생각을 분명하게 드러냈습니다.",
            "2. 짧고 간단한 문장으로 표현해 읽기 쉽습니다.",
            "",
            "고칠 점",
            "1. 개념의 정확성을 다시 확인해 보세요.",
            "2. 이유나 근거를 한 문장 더 덧붙이면 설명이 더 좋아집니다.",
            "",
            "바로 적용할 문장",
            suggestion,
        ]
    )
