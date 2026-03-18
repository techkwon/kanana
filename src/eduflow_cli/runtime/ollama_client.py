import json
import os
import socket
from typing import Any, Dict, Optional
from urllib import error, request

from eduflow_cli.config import get_settings
from eduflow_cli.contracts.errors import RuntimeDependencyError


class OllamaClient:
    def __init__(self, host: Optional[str] = None, timeout: Optional[float] = None):
        settings = get_settings()
        resolved_host = host or os.getenv("EDUFLOW_OLLAMA_HOST", settings.ollama_host)
        resolved_timeout = timeout or float(
            os.getenv("EDUFLOW_TIMEOUT_SECONDS", str(settings.request_timeout_seconds))
        )
        self.host = resolved_host.rstrip("/")
        self.timeout = resolved_timeout
        self.use_stub_runtime = os.getenv(
            "EDUFLOW_USE_STUB_RUNTIME",
            "1" if settings.use_stub_runtime else "0",
        ) == "1"

    def _request_json(self, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if self.use_stub_runtime:
            return self._stub_response(path, payload)
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.host}{path}",
            method="POST" if payload is not None else "GET",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
        except (error.URLError, TimeoutError, socket.timeout) as exc:
            raise RuntimeDependencyError("ollama is unreachable", {"host": self.host, "reason": str(exc)})
        try:
            return json.loads(body or "{}")
        except json.JSONDecodeError as exc:
            raise RuntimeDependencyError("ollama returned invalid JSON", {"position": exc.pos})

    def _stub_response(self, path: str, payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if path == "/api/tags":
            return {"models": [{"name": get_settings().default_model}]}
        if path == "/api/generate":
            prompt = (payload or {}).get("prompt", "")
            if (payload or {}).get("format") == "json":
                if '"questions"' in prompt:
                    return {
                        "response": json.dumps(
                            {
                                "questions": [
                                    {
                                        "question": "광합성은 무엇인가요?",
                                        "answer": "식물이 빛으로 양분을 만드는 과정입니다.",
                                        "explanation": "햇빛, 물, 이산화탄소를 사용해 스스로 양분을 만듭니다.",
                                    },
                                    {
                                        "question": "광합성은 주로 어디에서 일어나나요?",
                                        "answer": "잎에서 일어납니다.",
                                        "explanation": "식물의 잎이 햇빛을 가장 잘 받기 때문입니다.",
                                    },
                                    {
                                        "question": "광합성이 중요한 이유는 무엇인가요?",
                                        "answer": "식물이 자라고 산소를 만드는 데 필요합니다.",
                                        "explanation": "광합성 덕분에 식물은 자라고 사람과 동물도 산소를 얻습니다.",
                                    },
                                ]
                            },
                            ensure_ascii=False,
                        )
                    }
                if '"strengths"' in prompt:
                    return {
                        "response": json.dumps(
                            {
                                "strengths": ["핵심 내용이 분명합니다.", "문장이 비교적 자연스럽습니다."],
                                "improvements": ["예시를 하나 더 추가하면 좋습니다.", "마침표와 띄어쓰기를 조금 더 다듬으면 좋습니다."],
                                "suggestion": "핵심 내용을 유지하면서 예시를 한 문장만 더 덧붙여 보세요.",
                            },
                            ensure_ascii=False,
                        )
                    }
                topic = self._extract_prompt_value(prompt, "주제:")
                return {
                    "response": json.dumps(
                        {
                            "title": topic or "학습 주제",
                            "summary": [
                                f"{topic or '이 주제'}의 뜻과 핵심 원리를 먼저 이해하면 다음 설명을 따라가기 쉽습니다.",
                                f"{topic or '이 주제'}은(는) 주요 특징과 쓰임을 함께 보면 더 잘 기억됩니다.",
                            ],
                            "example": f"예를 들어, {topic or '이 주제'}와(과) 관련된 쉬운 사례를 하나 떠올리면 개념이 더 선명해집니다.",
                            "key_points": [
                                f"{topic or '이 주제'}의 기본 뜻을 한 문장으로 정리합니다.",
                                f"{topic or '이 주제'}의 중요한 특징을 두세 가지로 나눠 봅니다.",
                                f"{topic or '이 주제'}을(를) 실제 예와 연결해 이해합니다.",
                            ],
                        },
                        ensure_ascii=False,
                    )
                }
            return {"response": f"STUB: {prompt}"}
        return {}

    @staticmethod
    def _extract_prompt_value(prompt: str, label: str) -> str:
        for line in prompt.splitlines():
            if line.startswith(label):
                return line.split(":", 1)[1].strip()
        return ""

    def list_models(self) -> Dict[str, Any]:
        return self._request_json("/api/tags")

    def generate(self, prompt: str, model: str) -> str:
        response = self._request_json(
            "/api/generate",
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "repeat_penalty": 1.15,
                    "num_predict": 256,
                },
            },
        )
        text = response.get("response")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeDependencyError("ollama generate returned empty response", {"model": model})
        return text.strip()

    def generate_json(self, prompt: str, model: str) -> Dict[str, Any]:
        response = self._request_json(
            "/api/generate",
            {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.2,
                    "repeat_penalty": 1.15,
                    "num_predict": 256,
                },
            },
        )
        text = response.get("response")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeDependencyError("ollama generate returned empty JSON response", {"model": model})
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeDependencyError("ollama generate returned invalid JSON", {"model": model, "position": exc.pos})
