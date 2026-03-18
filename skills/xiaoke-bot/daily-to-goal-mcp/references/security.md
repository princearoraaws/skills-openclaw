# Security & API Key Management

## Getting Your API Key

1. Sign up or log in at [https://h5.dd-up.com/](https://h5.dd-up.com/)
2. Go to Settings → API Keys
3. Generate a new key — save it immediately, it is shown only once

## API Key Format

Keys follow the pattern: `dtg_{environment}_{random}`

- `dtg_live_...` — Production keys
- `dtg_test_...` — Test/development keys

## Key Scopes

| Scope | Permission |
|-------|-----------|
| `goals:read` | Read goal data |
| `goals:write` | Create/update/delete goals |
| `tasks:read` | Read task data |
| `tasks:write` | Create/update/delete tasks |
| `entities:read` | Read entity data |
| `entities:write` | Create/update/delete entities |
| `team:read` | Read team data |
| `datasets:read` | Read dataset data |

## Multi-Tenant Isolation

All operations are scoped to your tenant. Data from other tenants is never accessible.

## Best Practices

1. Never commit API keys to version control
2. Rotate keys periodically
3. Use minimum required scopes
4. Set expiration times on keys
5. Revoke unused keys promptly
