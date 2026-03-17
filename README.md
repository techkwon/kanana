# Kanana

Local-first Korean education AI CLI for real educator workflows.

Kanana is built for people who need AI outputs they can actually use in class, in tutoring, or in education products. It runs on top of Ollama, exposes a JSON-first contract for agents and tools, and adds structured output, safety gates, and QA-backed quality checks on top of local generation.

## Why Kanana

- Built for educators, not generic chat
- Local-first by default with Ollama
- Stable JSON contract for Codex CLI, Claude Code, OpenCode, and OpenClaw
- Structured generation for `explain`, `quiz`, and `review`
- Safety-aware pipeline with deterministic fallbacks
- QA harness with grouped case packs and misconception taxonomy

## What It Does

- `explain`
  Turn a topic into a clean Korean explanation with title, concept summary, example, and key takeaways
- `quiz`
  Generate readable Korean quizzes with fixed `question / answer / explanation` structure
- `review`
  Turn learner writing or misconceptions into feedback with strengths, improvements, and a concrete correction sentence
- `safety.check`
  Run the safety layer directly
- `kakao.template`
  Produce Kakao-friendly template payloads without direct sending
- `health`
  Check Ollama reachability and target model readiness

## Why It Feels Different

Most local LLM demos look impressive for one prompt and fall apart when you try to operationalize them.

Kanana is opinionated in the places that matter:

- structured-first generation before free-form fallback
- Korean-first prompt shaping
- output cleanup for punctuation and formatting drift
- misconception-aware review handling
- repeatable QA instead of one-off screenshots

## Current Quality Bar

Fresh local evidence:

- `PYTHONPATH=src python3 -m unittest discover -s tests`
  `28 tests OK`
- `PYTHONPATH=src python3 -m kanana_cli.qa_harness --mode stub`
  `100/100 pass`
- `PYTHONPATH=src python3 -m kanana_cli.qa_harness --mode live --limit 12`
  `12/12 pass`

This is strong enough for:

- demos
- pilot customers
- early paid trials
- internal education tooling

This is not yet a promise of broad commercial correctness across every curriculum edge case. The QA system is in place so that bar can be raised deliberately.

## Quick Start

### 1. Pull the model

```bash
/Applications/Ollama.app/Contents/Resources/ollama pull neoali/kanana-1.5-2.1b-instruct-2505
```

### 2. Health check

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main health
```

### 3. Try explain

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main explain --topic "피타고라스 정리" --learner-level middle --no-save
```

### 4. Try quiz

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main quiz --topic "광합성" --learner-level elementary --no-save
```

### 5. Try review

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main review --submission "빛은 식물이 먹는 음식이다." --learner-level high --no-save
```

## Agent-Ready Contract

Kanana is designed for tool use, not just manual shell use.

Request shape:

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

Response shape:

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

## QA System

Kanana now includes a structured QA system instead of a single flat case file.

Layout:

- `qa/cases/explain/*.json`
- `qa/cases/quiz/*.json`
- `qa/cases/review/*.json`
- `qa/misconception-taxonomy.json`

The harness reports:

- by command
- by group
- by misconception category
- recurring issue summaries

Stub run:

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.qa_harness --mode stub
```

Live run:

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.qa_harness --mode live
```

Reports are written to `.kanana/reports/`.

## Repository Structure

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

## Adapters

Adapters stay thin by design.

- Claude Code
- Codex CLI
- OpenCode
- OpenClaw

They should pass JSON in, read JSON out, and keep business logic inside Kanana itself.

## Current Positioning

Kanana is best positioned as:

`A QA-backed local Korean education AI CLI for pilot sales and early production workflows.`

## Next Milestone

The next serious step is not “more features.”

It is:

- expanding live QA beyond sampled runs
- broadening misconception coverage
- tightening subject-specific correctness thresholds

That is the path from strong demo software to real commercial trust.
