# ClawHub Publish Command

## 1. Login first

```bash
clawhub login
clawhub whoami
```

## 2. Publish command

```bash
clawhub publish /root/.openclaw/workspace/skills/ccdb-carbon-factor-search \
  --slug ccdb-factor-search \
  --name "CCDB Factor Search" \
  --version 0.1.0 \
  --tags carbon,emission-factor,ccdb,sustainability,lca,search \
  --changelog "Initial beta release for CCDB factor matching. Supports bilingual search, smallest-core-term query strategy, iterative candidate comparison, suitability filtering, and structured factor selection output."
```

## 3. Suggested follow-up checks

After publishing, check:

```bash
clawhub whoami
clawhub inspect ccdb-factor-search
```

If later you update the skill, bump the version and publish again.
