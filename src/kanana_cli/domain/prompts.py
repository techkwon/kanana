from .audience import guidance_for_level


def build_prompt(command: str, learner_level: str, user_input: dict) -> str:
    topic = user_input.get("topic") or user_input.get("submission") or user_input.get("question") or "the provided topic"
    guidance = guidance_for_level(learner_level)

    if command == "explain":
        return (
            f"다음 주제를 교육자가 바로 설명에 사용할 수 있게 한국어로 설명하세요: {topic}. "
            f"{guidance} "
            "출력 규칙: 제목 한 줄, 핵심 설명 2~4문장, 쉬운 예시 1개, 핵심 정리 3개. "
            "느낌표, 반복 기호, 과장된 장식 표현을 쓰지 마세요. "
            "불필요한 영어를 쓰지 마세요."
        )

    if command == "quiz":
        return (
            f"다음 주제로 한국어 퀴즈를 만드세요: {topic}. "
            f"{guidance} "
            "출력 규칙: 문제 3개, 각 문제 뒤에 정답 1개와 짧은 해설 1개. "
            "문제는 한 문장 질문으로 쓰고, 정답과 해설은 완전한 문장으로 쓰세요. "
            "초등 수준이면 문장을 짧게 쓰세요. "
            "형식 예시: 문제 1: ... 줄바꿈 정답: ... 줄바꿈 해설: ... "
            "느낌표, 반복 기호, 따옴표, 불필요한 영어를 쓰지 마세요."
        )

    if command == "review":
        return (
            f"다음 학습자 작업을 한국어로 검토하세요: {topic}. "
            f"{guidance} "
            "출력 규칙: 잘한 점 2개, 고칠 점 2개, 바로 적용할 한 문장 제안 1개. "
            "공손하고 차분한 톤을 유지하고, 장식성 기호를 쓰지 마세요."
        )

    return (
        f"다음 교육자 요청을 한국어로 지원하세요: {topic}. "
        f"{guidance} "
        "장식성 기호와 불필요한 영어를 쓰지 마세요."
    )
