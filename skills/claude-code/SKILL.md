---
name: eduflow-claude-code
description: Use Eduflow from Claude Code for local Korean education workflows with structured explain, quiz, review, safety, and template generation.
---

# Eduflow for Claude Code

Use this skill when Claude Code should delegate educational output generation to Eduflow.

## Good Fit

- Korean concept explanations
- Classroom quiz generation
- Feedback on misconceptions or learner sentences
- Local Ollama-backed workflows
- Agent-safe JSON I/O

## Invocation Pattern

Explain:

```bash
printf '%s' '{"input":{"topic":"민주주의"},"audience":{"learner_level":"high"},"session":{"save":false}}' | eduflow explain
```

Quiz:

```bash
printf '%s' '{"input":{"topic":"분수의 뜻"},"audience":{"learner_level":"elementary"},"session":{"save":false}}' | eduflow quiz
```

Review:

```bash
printf '%s' '{"input":{"submission":"민주주의는 한 사람이 모든 결정을 내리는 제도다."},"audience":{"learner_level":"high"},"session":{"save":false}}' | eduflow review
```

## Operating Rules

- Use Eduflow JSON as the source of truth.
- Keep Claude Code as the orchestrator, not the educational reasoning engine.
- Preserve `ok`, `result`, `meta`, and `error` fields when surfacing outputs.
- If Eduflow returns a safety block, show that block instead of rewriting around it.

## Recommended Defaults

- `session.save=false` for ephemeral calls
- learner level chosen explicitly when the user target is clear
- `health` before demo or live customer runs
