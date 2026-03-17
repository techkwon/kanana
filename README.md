# Kanana CLI v0.1

Kanana is a local-first, JSON-first CLI for educator workflows. Core business logic stays inside the CLI so thin adapters for Claude Code, Codex CLI, OpenCode, and OpenClaw can call the same stable contract.

## Supported commands

- `health`
- `explain`
- `quiz`
- `review`
- `safety.check`
- `kakao.template`

## Request envelope

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

## Response envelope

```json
{
  "schema_version": "1.0",
  "ok": true,
  "command": "health",
  "result": {},
  "meta": {
    "model": "neoali/kanana-1.5-2.1b-instruct-2505:latest",
    "latency_ms": 0,
    "session_id": null
  },
  "error": null
}
```

## Exit codes

- `0` success
- `2` blocked by safety policy
- `3` invalid input / contract error
- `4` runtime dependency error
- `5` unexpected internal failure

## Local development

### Smoke run without install

```bash
cd kanana
PYTHONPATH=src python3 -m kanana_cli.main health
```

### Stub runtime for local testing

If Ollama is not available, set `KANANA_USE_STUB_RUNTIME=1`.

```bash
cd kanana
KANANA_USE_STUB_RUNTIME=1 PYTHONPATH=src python3 -m kanana_cli.main explain --topic fractions --learner-level elementary
```

### Ollama assumptions

- Default host: `http://localhost:11434`
- Default model: `neoali/kanana-1.5-2.1b-instruct-2505:latest`
- `health` checks reachability and model presence.

Pull the default model before live runs:

```bash
/Applications/Ollama.app/Contents/Resources/ollama pull neoali/kanana-1.5-2.1b-instruct-2505
```

## Session storage

Saved sessions default to `.kanana/sessions/` under the current working directory, or `KANANA_SESSION_DIR` when set.

## Quality QA Harness

Kanana includes a repeatable QA harness for `explain`, `quiz`, and `review`.

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

The harness reads the grouped case directory [qa/cases](/Users/techkwon/Documents/MyApps/kanana/qa/cases), scores each case, and writes a JSON report under `.kanana/reports/`.

Current layout:

- `qa/cases/explain/*.json`
- `qa/cases/quiz/*.json`
- `qa/cases/review/*.json`
- `qa/misconception-taxonomy.json`

Reports now include:

- command summary
- group/file summary
- misconception summary
- top recurring issues

## Adapter pattern

Adapters are documentation-thin wrappers only. They should pass JSON into `kanana` and consume JSON out.
