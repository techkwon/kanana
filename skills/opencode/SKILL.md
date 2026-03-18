---
name: eduflow-opencode
description: Use Eduflow from OpenCode as a thin local education adapter with JSON-first input/output and QA-backed Korean explain, quiz, and review flows.
---

# Eduflow for OpenCode

OpenCode should stay a thin wrapper over Eduflow.

## Workflow

1. Collect user intent
2. Convert it to the Eduflow request envelope
3. Invoke `eduflow <command>`
4. Read JSON output
5. Render or route the result inside OpenCode

## Commands

Explain:

```bash
printf '%s' '{"input":{"topic":"훈민정음"},"audience":{"learner_level":"middle"},"session":{"id":"lesson-001","save":true}}' | eduflow explain
```

Quiz:

```bash
printf '%s' '{"input":{"topic":"태양계"},"audience":{"learner_level":"elementary"},"session":{"save":false}}' | eduflow quiz
```

Review:

```bash
printf '%s' '{"input":{"submission":"광합성은 밤에만 일어난다."},"audience":{"learner_level":"elementary"},"session":{"save":false}}' | eduflow review
```

Kakao template:

```bash
printf '%s' '{"input":{"topic":"과학 경시대회 안내"},"audience":{"learner_level":"adult"},"session":{"save":false}}' | eduflow kakao.template
```

## Rules

- Do not add OpenCode-only business logic.
- Do not bypass Eduflow safety or fallback layers.
- Prefer exact JSON pass-through over lossy reshaping.
- Use Eduflow session IDs only when the workflow needs persistent artifacts.
