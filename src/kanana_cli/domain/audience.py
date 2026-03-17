GUIDANCE_BY_LEVEL = {
    "elementary": "쉬운 낱말, 짧은 문장, 생활 속 예시를 사용하세요.",
    "middle": "구체적인 예시, 가벼운 학습 용어, 단계별 설명을 사용하세요.",
    "high": "교과 용어, 원인과 결과 설명, 간결한 정확성을 유지하세요.",
    "adult": "전문적인 톤, 정확한 용어, 실용적인 맥락을 사용하세요.",
}


def guidance_for_level(level: str) -> str:
    return GUIDANCE_BY_LEVEL.get(level, GUIDANCE_BY_LEVEL["elementary"])
