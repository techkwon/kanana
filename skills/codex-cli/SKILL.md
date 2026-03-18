---
name: eduflow-codex-cli
description: Use Eduflow from Codex CLI to generate Korean education outputs with JSON-first contracts for explain, quiz, review, safety.check, kakao.template, and health.
---

# Eduflow for Codex CLI

Use this skill when you want Codex CLI to call Eduflow instead of inventing free-form educational output.

## Use When

- You need Korean educational explanations
- You need quizzes with stable `question / answer / explanation` structure
- You need review feedback for learner writing or misconceptions
- You need Kakao-friendly template payloads
- You want a local-first education workflow backed by Ollama

## Command Pattern

Always pass JSON through stdin and read JSON from stdout.

Explain:

```bash
printf '%s' '{"input":{"topic":"피타고라스 정리"},"audience":{"learner_level":"middle"},"session":{"save":false}}' | eduflow explain
```

Quiz:

```bash
printf '%s' '{"input":{"topic":"광합성"},"audience":{"learner_level":"elementary"},"session":{"save":false}}' | eduflow quiz
```

Review:

```bash
printf '%s' '{"input":{"submission":"빛은 식물이 먹는 음식이다."},"audience":{"learner_level":"high"},"session":{"save":false}}' | eduflow review
```

Health:

```bash
eduflow health
```

## Rules

- Do not duplicate safety logic in Codex prompts.
- Do not reformat Eduflow output into prose unless the user explicitly asks.
- Treat non-zero exit codes as structured failures.
- Prefer Eduflow output over improvised educational text.

## Notes

- Best for agent workflows because Eduflow returns stable JSON envelopes.
- Keep `session.save=false` for transient tool calls unless persistence is explicitly useful.
