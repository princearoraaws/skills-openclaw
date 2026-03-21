# WebDAV Sync Operations

## Environment

Read credentials from an env file. Expected keys:

- `WEBDAV_SITE`
- `WEBDAV_USERID`
- `WEBDAV_PWD`

Do not print these values in logs or chat replies.

## Interpreter Policy

Prefer a pinned Python 3.10+ interpreter for this skill.

Do not rely on bare `python3` for this skill unless the host version has been verified.

## Wrapper Pattern

Use a thin wrapper around `scripts/webdav_sync.py` for host-specific scheduling or one-command execution.

Example:

```bash
python3.10 /path/to/skills/webdav-sync/scripts/webdav_sync.py --source /path/to/folder ...
```

## Example Nightly Job

```cron
0 0 * * * /path/to/project/scripts/webdav_sync_wrapper.sh >> /var/log/webdav_sync.log 2>&1
```

## Example Exclude Set

- `folder/.trash`
- `folder/.trash/*`
- `folder/tmp`
- `folder/tmp/*`
- `folder/__pycache__`
- `folder/__pycache__/*`

## Upload Semantics

- Create missing remote directories with `MKCOL`.
- Accept `201`, `301`, `405` for directory-ready responses.
- Upload archive with `PUT`.
- Accept `200`, `201`, `204` as upload success.
