---
name: aiheal-cli-operator
description: Operate and troubleshoot the AIHealingMe frontend CLI through the npm package (`aihealingme-cli`). Use when tasks involve auth/user/audio/plan/chat/emotion/subscription workflows, payload shaping, command diagnostics, and API failure handling without backend secret access.
---

# Aiheal Cli Operator

## Quick Start

- Use npm package runtime by default.
- Global runtime: `npm install -g aihealingme-cli` then `aiheal ...`.
- No-global runtime: `npx -y -p aihealingme-cli aiheal ...`.
- Keep all operations in package runtime.

## Workflow

1. Confirm runtime baseline.
- Run `aiheal --help`.
- Run `aiheal config get` to verify `apiBaseUrl`, locale, region, and token state.

2. Choose command family by task.
- Use `auth`/`config` for login and token setup.
- Use `audio`, `plan`, `single-job`, `plan-stage-job` for healing generation workflows.
- Use `chat` and `emotion` for conversation and emotion-space workflows.
- Use `subscription`, `notification`, `feedback`, `memory`, `behavior` for account-side operations.
- Use `api request` as fallback for unwrapped endpoints.

3. Prefer structured payload input for complex operations.
- Use `--payload-file path/to/file.json` by default.
- Use `--body '{...}'` only for short payloads.
- Merge behavior: `--body` overrides same keys from `--payload-file`.

4. Validate outputs and state transitions.
- Expect JSON output with top-level `ok`.
- Use `error.code` and `error.status` as primary diagnostics.
- For async jobs, use `single-job wait` and `plan-stage-job wait` with explicit timeout values.

## Execution Rules

- Keep operations frontend-only; never use backend secret files.
- Keep default API on public endpoint `https://aihealing.me/api` unless task explicitly requires override.
- Require explicit `--output` for download/export commands.
- Use global overrides (`--api-base`, `--locale`, `--region`, `--token`) only in the current command context.

## Troubleshooting

- `AUTH_ERROR`: login again and verify with `whoami`.
- `API_ERROR` with `status: 0`: verify network and `apiBaseUrl`.
- `npx` cache `EPERM`: set `NPM_CONFIG_CACHE=/tmp/aiheal-npm-cache` or use global install.
- Async wait timeout: query status endpoints (`get`/`by-request`) and inspect progress fields.

## Resources

- Read [references/command-map.md](references/command-map.md) for full command syntax and parameter meanings.
- Read [references/error-playbook.md](references/error-playbook.md) for failure signatures and fix flow.
- Run path-independent smoke commands with `npx -y -p aihealingme-cli aiheal --help` and `... config get`.
