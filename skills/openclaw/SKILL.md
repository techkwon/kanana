---
name: kanana-openclaw
description: Use Kanana from OpenClaw for local Korean education generation with structured explain, quiz, review, and Kakao template outputs.
---

# Kanana for OpenClaw

Use this skill when OpenClaw should call a local education-focused generator instead of producing ad hoc text.

## Best Uses

- Educational concept explanation
- Structured quiz generation
- Misconception or sentence review
- Kakao-friendly classroom notice templates

## Thin Adapter Contract

- stdin: Kanana request JSON
- stdout: Kanana response JSON
- non-zero exit: structured failure

## Example Commands

Explain:

```bash
printf '%s' '{"input":{"topic":"생태계"},"audience":{"learner_level":"high"},"session":{"save":false}}' | kanana explain
```

Quiz:

```bash
printf '%s' '{"input":{"topic":"소수와 합성수"},"audience":{"learner_level":"middle"},"session":{"save":false}}' | kanana quiz
```

Review:

```bash
printf '%s' '{"input":{"submission":"분모는 분수에서 위에 쓰는 숫자다."},"audience":{"learner_level":"middle"},"session":{"save":false}}' | kanana review
```

Kakao template:

```bash
printf '%s' '{"input":{"topic":"수업 자료 안내"},"audience":{"learner_level":"adult"},"session":{"save":false}}' | kanana kakao.template
```

## Notes

- Keep OpenClaw focused on routing, not rewriting.
- Kanana is the quality and safety boundary.
- For demos, run `kanana health` first.
