---
name: wise-readonly
description: Read-only Wise API operations for account inspection and FX lookups. Use when asked to list profiles, inspect balances, fetch profile details, or check rates without creating transfers, recipients, quotes, or any other mutable resources.
---

Read-only Wise API skill for OpenClaw.

## Requirements
- `WISE_API_TOKEN` environment variable.
- Network access from the runtime host to `https://api.wise.com`.

## Supported Commands
- `list_profiles` (PII-redacted by default)
- `get_profile --profile-id <id>` (PII-redacted by default)
- `list_balances --profile-id <id>`
- `get_exchange_rate --source <CUR> --target <CUR>`

Command runner:
- `scripts/wise_readonly.mjs`

## Privacy and Safety
- Profile responses redact common PII fields by default.
- Add `--raw` only when strictly necessary.
- This skill performs no write operations.
- Disallowed operations include quote creation, transfers, recipient create/update/delete, funding, and cancellation.

## Quick Test
```bash
export WISE_API_TOKEN=...
node scripts/wise_readonly.mjs list_profiles
node scripts/wise_readonly.mjs list_balances --profile-id <id>
node scripts/wise_readonly.mjs get_exchange_rate --source GBP --target EUR
```

## Troubleshooting
- `403 unauthorized`: check token validity, scopes, and Wise IP allowlist.
- Empty/missing token: ensure `WISE_API_TOKEN` is set in the same shell.

## Acknowledgements
This skill is inspired by wise-mcp by Szotasz:
https://github.com/Szotasz/wise-mcp
