# Telegram Footer Patch

![Footer Preview](./assets/footer-preview.jpg)

Patch OpenClaw's Telegram reply pipeline to append a one-line footer in private chats (`🧠 Model + 💭 Think + 📊 Context`).

## What it does
- Adds a one-line footer for Telegram private-chat replies
- Shows model, think level, and context usage in one line
- Supports dry-run preview
- Creates a backup before any file change
- Supports rollback and verification after restart
- Handles Telegram streaming replies in current OpenClaw builds

## Recommended flow
1. Dry-run
2. Apply
3. Restart the gateway (**required** to take effect)
4. Send a test message and verify the footer

## Before you run
- This updates OpenClaw frontend bundle files under `.../openclaw/dist/`.
- Run `python3 scripts/patch_reply_footer.py --dry-run` first.
- Confirm backups exist (`*.bak.telegram-footer.*`) and test rollback (`python3 scripts/revert_reply_footer.py --dry-run`).
- Use only on systems you control.

## Key files
- `SKILL.md` — usage guidance
- `scripts/patch_reply_footer.py` — patch script
- `scripts/revert_reply_footer.py` — rollback script
- `CHANGELOG.md` — release notes
- `LICENSE` — MIT license
