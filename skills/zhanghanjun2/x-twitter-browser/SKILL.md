---
name: x-twitter-browser
description: Use a real browser session's cookie header to verify login and perform browser actions on X/Twitter via headless Playwright. Currently supports posting tweets.
version: 1.0.0
user-invocable: true
metadata:
  openclaw:
    emoji: "🐦"
    skillKey: "x-twitter-browser"
    requires:
      bins:
        - python3
allowed-tools: Bash(python3:*), browser
---

# x-twitter-browser

Execute browser actions on X using your real browser login state, without the official X API.

Users only need to provide a single `cookie header` string.

After installing into OpenClaw, the skill lives at:

```bash
~/.openclaw/workspace/skills/x-twitter-browser/
```

Commands below assume you run from the skill root directory:

```bash
cd ~/.openclaw/workspace/skills/x-twitter-browser
```

## Use cases

- You want to reuse browser login state instead of the official API
- Running headless on a VM or Linux server
- Building a long-term extensible browser skill for X automation
- You can provide a single `cookie header` string

## Architecture

This skill has two layers:

### 1. Session layer

Persists the user-provided cookie locally:

- `scripts/save_cookie_header.py`
- `runtime/cookie-header.txt`

### 2. Action layer

Performs actions using the verified browser session. Currently implemented:

- Post tweet: `scripts/post_tweet.py`

## Implemented features

- Save user-provided cookie header
- Verify that the session is still logged in
- Post plain-text tweets via the browser session

## Dependencies

**Note:** First-time setup can take several minutes (Chromium is ~150MB). Each step may take 1–5 minutes depending on your network. If a package or browser is already installed, that step will finish quickly.

**OpenClaw:** When running `setup.sh` via OpenClaw, it executes in the background and the user cannot see the `echo` output. Forward each progress message (e.g. "Installing playwright...", "✓ Playwright package installed.", "Installing Chromium...") to the user as it appears so they know the setup is progressing.

First-time setup (recommended):

```bash
./scripts/setup.sh
```

## Authentication input

Paste the full browser `Cookie` request header, e.g.:

```text
guest_id=...; auth_token=...; ct0=...; twid=...; ...
```

Important cookies:

- `auth_token`
- `ct0`
- `twid`
- `kdt`
- `att`
- `_twitter_sess`

## Runtime files

Scripts write sensitive runtime files to:

```bash
runtime/
```

Files used:

- `cookie-header.txt`

These files contain account credentials. Do not commit them or share them.

## Workflow

### 1. Save the user-provided cookie

If the user pastes a cookie header, save it to the runtime directory:

```bash
mkdir -p runtime

python3 scripts/save_cookie_header.py \
  --cookie-header 'guest_id=...; auth_token=...; ct0=...; twid=...'
```

Or save the cookie to a file first, then import:

```bash
cat > runtime/cookie-header.txt <<'EOF'
guest_id=...; auth_token=...; ct0=...; twid=...; ...
EOF

python3 scripts/save_cookie_header.py \
  --cookie-file runtime/cookie-header.txt
```

### 2. Verify login state

Before any browser action, run:

```bash
python3 scripts/post_tweet.py \
  --verify-only
```

Success looks like:

```text
Session looks valid: https://x.com/home
```

If verification fails, the cookie may be expired. Ask the user to provide a fresh cookie.

### 3. Post a tweet

After verification succeeds:

```bash
python3 scripts/post_tweet.py \
  --text "hello"
```

## Rules

- `--verify-only` success means the session is likely usable
- If the page behaves oddly, buttons are disabled, or extra dialogs appear, re-run verification first
- If Chromium fails to start, install Playwright browsers or system deps before blaming the cookie

## Operational requirements

- Run `--verify-only` before any write operation
- Confirm the action and content before executing
- Do not commit cookies or headers to the repo
- Prefer the full cookie header over partial cookies
- Keep all runtime files under `runtime/`
- Call `scripts/*.py` directly


### `Imported session is not authenticated`

- Cookie expired
- Incomplete header from user
- Account triggered extra verification

Ask the user to provide a fresh, complete cookie header.
