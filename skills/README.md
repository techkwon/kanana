# Eduflow Skills

This directory contains ready-to-use skill files for:

- Codex CLI
- Claude Code
- OpenCode
- OpenClaw

Each skill is a thin adapter over the `eduflow` CLI.

The rule is simple:

- collect user intent
- convert it to the Eduflow JSON request envelope
- invoke `eduflow`
- consume the JSON response

Business logic, safety policy, fallback handling, and QA stay inside Eduflow itself.
