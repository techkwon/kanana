# Claude Code adapter

Thin pattern:

```bash
echo '{"input":{"topic":"fractions"},"audience":{"learner_level":"elementary"}}' | eduflow explain
```

Claude Code should only prepare JSON input and consume Eduflow JSON output.
