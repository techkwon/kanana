# OpenCode adapter

OpenCode should stay a thin wrapper around the `eduflow` CLI. Business logic, safety policy, session logging, and prompt construction remain in `eduflow` itself.

## Stable invocation pattern

```bash
echo '{
  "input": {
    "topic": "fractions"
  },
  "audience": {
    "learner_level": "elementary"
  },
  "session": {
    "id": "lesson-001",
    "save": true
  }
}' | eduflow explain
```

## Wrapper expectations

- Pass JSON through stdin.
- Read JSON from stdout.
- Treat non-zero exit codes as structured failures.
- Do not duplicate safety logic in OpenCode.
- Preserve `session_id` and `save_session` fields so the CLI can persist artifacts.

## Suggested OpenCode wrapper flow

1. Collect the user intent in OpenCode.
2. Convert it to the `eduflow` request JSON contract.
3. Invoke `eduflow <command>`.
4. Render the returned JSON to the OpenCode surface.
5. If `ok=false` or exit code is non-zero, show the structured `error`/safety metadata.

## Example shell wrapper

```bash
payload='{"input":{"topic":"photosynthesis"},"audience":{"learner_level":"middle"},"session":{"id":"science-001","save":true}}'
printf '%s' "$payload" | eduflow explain
```
