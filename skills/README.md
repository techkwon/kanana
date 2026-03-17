# Kanana Skills

This directory contains ready-to-use skill files for:

- Codex CLI
- Claude Code
- OpenCode
- OpenClaw

Each skill is a thin adapter over the `kanana` CLI.

The rule is simple:

- collect user intent
- convert it to the Kanana JSON request envelope
- invoke `kanana`
- consume the JSON response

Business logic, safety policy, fallback handling, and QA stay inside Kanana itself.
