# Kanana

한국어 교육 현장에서 바로 쓸 수 있게 만든 로컬 교육 AI CLI.

Kanana는 “그럴듯한 데모”가 아니라, 교육자와 에이전트가 실제로 호출해도 무너지지 않게 설계한 JSON-first AI CLI입니다. Ollama 위에서 동작하고, `explain`, `quiz`, `review`를 중심으로 구조화 출력, 안전 게이트, 오개념 분류, QA harness까지 갖추고 있습니다.

## 아주 쉽게 말하면

Kanana는 이런 도구입니다.

- 어려운 내용을 쉽게 설명해 주고
- 퀴즈를 만들어 주고
- 학생이 쓴 문장을 보고 뭐가 맞고 뭐가 틀렸는지 알려주고
- 그 결과를 컴퓨터 프로그램이나 AI 에이전트가 다시 쓰기 좋게 JSON으로 내보내는 도구

한 줄로 말하면:

`교육용으로 다듬은 로컬 AI 선생님 CLI`

## 한눈에 보기

- 한국어 교육용 출력에 맞춘 로컬-first CLI
- `explain / quiz / review` 구조화 생성
- Codex CLI, Claude Code, OpenCode, OpenClaw 같은 에이전트 도구와 연결하기 쉬운 JSON 계약
- 안전 필터 + deterministic fallback
- grouped QA 케이스 + misconception taxonomy
- live 샘플 검증까지 포함한 품질 관리 구조

## 왜 이 프로젝트를 주목해야 하나

대부분의 로컬 LLM 프로젝트는 여기서 멈춥니다.

- 한두 번 잘 나온 출력
- 예쁜 스크린샷
- 하지만 반복 실행하면 품질 흔들림

Kanana는 그 반대로 갑니다.

- 출력 형식을 모델에만 맡기지 않음
- 구조화 JSON 생성 우선
- 실패하면 로컬 fallback으로 회수
- 오개념 리뷰는 taxonomy로 분류
- 품질은 harness로 점수화

즉, “보여주기 좋은 AI”가 아니라 “계속 돌려도 버티는 교육 AI”를 목표로 합니다.

## 지금 어디까지 왔나

fresh evidence:

- `PYTHONPATH=src python3 -m unittest discover -s tests`
  `28 tests OK`
- `PYTHONPATH=src python3 -m kanana_cli.qa_harness --mode stub`
  `100/100 pass`
- `PYTHONPATH=src python3 -m kanana_cli.qa_harness --mode live --limit 12`
  `12/12 pass`

현재 포지션:

- 데모: 가능
- 파일럿 판매: 가능
- 초기 유료 테스트: 가능
- 대규모 상용 배포: QA를 더 쌓아야 함

## 누구를 위한가

- 교사, 강사, 튜터, 교육 콘텐츠 제작자
- 한국어 교육형 AI를 붙이고 싶은 개발자
- 에이전트 워크플로에 교육용 도구를 넣고 싶은 팀
- “로컬에서 돌아가면서도 품질 관리가 되는” 교육 AI가 필요한 사람

## 핵심 명령

- `health`
  Ollama 연결과 모델 준비 상태 확인
- `explain`
  개념 설명을 제목, 설명, 예시, 핵심 정리 구조로 생성
- `quiz`
  문제, 정답, 해설 구조의 한국어 퀴즈 생성
- `review`
  학생 문장이나 오개념에 대해 교육자용 피드백 생성
- `safety.check`
  안전 레이어 직접 실행
- `kakao.template`
  카카오 공유용 템플릿 payload 생성

## 빠르게 써보기

### 1. 모델 준비

```bash
/Applications/Ollama.app/Contents/Resources/ollama pull neoali/kanana-1.5-2.1b-instruct-2505
```

### 2. 상태 확인

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main health
```

### 3. 개념 설명

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main explain --topic "피타고라스 정리" --learner-level middle --no-save
```

### 4. 퀴즈 생성

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main quiz --topic "광합성" --learner-level elementary --no-save
```

### 5. 오개념 리뷰

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main review --submission "빛은 식물이 먹는 음식이다." --learner-level high --no-save
```

## 에이전트 친화 설계

Kanana는 사람용 CLI처럼 보이지만, 실제로는 에이전트 호출에 맞춰져 있습니다.

Request envelope:

```json
{
  "input": {},
  "audience": {
    "role": "educator",
    "learner_level": "elementary"
  },
  "safety": {
    "mode": "strict",
    "block_on_unsafe": true
  },
  "session": {
    "id": null,
    "save": true
  },
  "output": {
    "format": "json",
    "verbosity": "standard"
  }
}
```

Response envelope:

```json
{
  "schema_version": "1.0",
  "ok": true,
  "command": "explain",
  "result": {},
  "meta": {
    "model": "neoali/kanana-1.5-2.1b-instruct-2505:latest",
    "latency_ms": 0,
    "session_id": null
  },
  "error": null
}
```

Exit codes:

- `0` success
- `2` blocked by safety policy
- `3` invalid input
- `4` runtime dependency error
- `5` internal error

## QA 시스템

Kanana의 차별점은 QA를 구조로 들고 간다는 점입니다.

구성:

- `qa/cases/explain/*.json`
- `qa/cases/quiz/*.json`
- `qa/cases/review/*.json`
- `qa/misconception-taxonomy.json`

리포트는 아래 기준으로 집계됩니다.

- command별
- group별
- misconception별
- 반복 이슈별

Stub QA:

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.qa_harness --mode stub
```

Live QA:

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.qa_harness --mode live
```

리포트는 `.kanana/reports/`에 JSON으로 쌓입니다.

## 저장소 구조

```text
src/kanana_cli/
  cli/
  contracts/
  domain/
  output/
  runtime/
  safety/
qa/
  cases/
  misconception-taxonomy.json
tests/
```

## 어댑터

Kanana는 로직을 바깥으로 흩뿌리지 않습니다.

- Claude Code
- Codex CLI
- OpenCode
- OpenClaw

이 어댑터들은 모두 얇게 유지하고, 실제 판단은 Kanana CLI 안에서 하도록 설계했습니다.

## 현재 포지셔닝

가장 정확한 한 줄은 이겁니다.

`QA-backed local Korean education AI CLI for educators, copilots, and agent workflows.`

한국어로 풀면:

`교육자와 에이전트 워크플로를 위해 만든, 품질 검증 가능한 로컬 한국어 교육 AI CLI`

## 다음으로 커질 방향

지금 중요한 건 기능을 더 붙이는 게 아닙니다.

- live QA 100 전체 완주
- 과목별 케이스 확대
- 오개념 taxonomy 세분화
- 판매 페이지용 시연 캡처와 social preview 제작

그 단계까지 가면 “좋아 보이는 프로젝트”에서 “사고 싶은 프로젝트”로 넘어갑니다.
