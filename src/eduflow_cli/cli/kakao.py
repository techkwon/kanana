from eduflow_cli.cli.common import build_success
from eduflow_cli.contracts.errors import InputValidationError


def run_kakao_template(envelope: object) -> dict:
    topic = envelope.input.get("topic") or envelope.input.get("question")
    if not topic:
        raise InputValidationError("kakao.template requires input.topic or input.question")
    result = {
        "template": {
            "type": "feed",
            "title": f"학습 안내: {topic}",
            "description": "학생 안전을 고려한 수업/과제 안내 템플릿",
            "buttons": [
                {"label": "학습 목표 보기", "action": "share"},
                {"label": "안전 가이드", "action": "share"},
            ],
        },
        "delivery": {
            "mode": "template_only",
            "send_supported": False,
        },
    }
    return build_success("kakao.template", result)
