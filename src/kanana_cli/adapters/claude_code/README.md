# Claude Code adapter

Thin pattern:

```bash
echo '{"input":{"topic":"fractions"},"audience":{"learner_level":"elementary"}}' | kanana explain
```

Claude Code should only prepare JSON input and consume Kanana JSON output.
