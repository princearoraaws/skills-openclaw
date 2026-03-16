---
name: ocmemog-installer
description: Install, update, and configure the ocmemog OpenClaw memory plugin and sidecar from the simbimbo/ocmemog repository. Use when setting up ocmemog for local durable memory, transcript-backed continuity, sidecar launch, plugin enablement, or troubleshooting an existing ocmemog install.
---

# ocmemog Installer

Install `ocmemog` from the canonical GitHub repo and configure OpenClaw to use it as the memory plugin.

## Canonical source

- Repo: `https://github.com/simbimbo/ocmemog.git`
- Plugin id: `memory-ocmemog`
- Default sidecar endpoint: `http://127.0.0.1:17890`

## Install / update workflow

1. Clone or update the repo into a local working directory.
2. Create a Python virtualenv in the repo and install `requirements.txt`.
3. Start the sidecar with `./scripts/ocmemog-sidecar.sh` or install the macOS LaunchAgents with `./scripts/ocmemog-install.sh`.
4. Install the plugin into OpenClaw with:
   - `openclaw plugins install -l /path/to/ocmemog`
   - `openclaw plugins enable memory-ocmemog`
5. Configure OpenClaw to use the plugin in the `memory` slot and point the entry config at the sidecar endpoint.
6. Validate with the sidecar health endpoint and a memory search/get smoke test.

## Minimal config shape

Use this OpenClaw plugin config shape:

```yaml
plugins:
  load:
    paths:
      - /path/to/ocmemog
  slots:
    memory: memory-ocmemog
  entries:
    memory-ocmemog:
      enabled: true
      config:
        endpoint: http://127.0.0.1:17890
        timeoutMs: 10000
```

## Validation checklist

- Sidecar responds on `/healthz`
- `openclaw plugins` shows `memory-ocmemog` installed/enabled
- Memory search/get calls return data instead of connection errors
- If packaging/publish questions arise, remember this skill is a ClawHub wrapper for the plugin repo, not the plugin package itself

## Notes

- Keep the sidecar bound to `127.0.0.1` unless explicit auth/network hardening is added.
- Prefer publishing the plugin itself through GitHub/npm/plugin-install flows; use this skill as the ClawHub-distributed installer/config guide.
