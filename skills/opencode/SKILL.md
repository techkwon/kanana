---
name: kanana-opencode
description: Use Kanana from OpenCode as a thin local education adapter with JSON-first input/output and QA-backed Korean explain, quiz, and review flows.
---

# Kanana for OpenCode

OpenCode should stay a thin wrapper over Kanana.

## Workflow

1. Collect user intent
2. Convert it to the Kanana request envelope
3. Invoke `kanana <command>`
4. Read JSON output
5. Render or route the result inside OpenCode

## Commands

Explain:

```bash
printf '%s' '{"input":{"topic":"훈민정음"},"audience":{"learner_level":"middle"},"session":{"id":"lesson-001","save":true}}' | kanana explain
```

Quiz:

```bash
printf '%s' '{"input":{"topic":"태양계"},"audience":{"learner_level":"elementary"},"session":{"save":false}}' | kanana quiz
```

Review:

```bash
printf '%s' '{"input":{"submission":"광합성은 밤에만 일어난다."},"audience":{"learner_level":"elementary"},"session":{"save":false}}' | kanana review
```

Kakao template:

```bash
printf '%s' '{"input":{"topic":"과학 경시대회 안내"},"audience":{"learner_level":"adult"},"session":{"save":false}}' | kanana kakao.template
```

## Rules

- Do not add OpenCode-only business logic.
- Do not bypass Kanana safety or fallback layers.
- Prefer exact JSON pass-through over lossy reshaping.
- Use Kanana session IDs only when the workflow needs persistent artifacts.
