#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote


DEFAULT_COOKIE_DOMAIN = ".x.com"
DEFAULT_RUNTIME_DIR = Path.home() / ".openclaw" / "workspace" / "skills" / "x-twitter-browser" / "runtime"
FALLBACK_RUNTIME_DIR = Path(__file__).resolve().parent.parent / "runtime"


def resolve_runtime_dir(explicit: str | None = None) -> Path:
    if explicit:
        path = Path(explicit).expanduser()
    elif DEFAULT_RUNTIME_DIR.parent.exists():
        path = DEFAULT_RUNTIME_DIR
    else:
        path = FALLBACK_RUNTIME_DIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def runtime_cookie_file(runtime_dir: Path) -> Path:
    return runtime_dir / "cookie-header.txt"


def runtime_state_file(runtime_dir: Path) -> Path:
    return runtime_dir / "storage-state.json"


def parse_cookie_header(cookie_header: str) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for item in cookie_header.split(";"):
        part = item.strip()
        if not part or "=" not in part:
            continue
        name, value = part.split("=", 1)
        name = name.strip()
        value = value.strip()
        if not name:
            continue
        cookies[name] = value
    return cookies


def cookie_header_to_storage_state(
    cookie_header: str,
    domain: str = DEFAULT_COOKIE_DOMAIN,
) -> dict[str, Any]:
    parsed = parse_cookie_header(cookie_header)
    cookies = []
    for name, value in parsed.items():
        secure = name not in {"lang", "g_state", "__cuid"}
        cookies.append(
            {
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/",
                "expires": -1,
                "httpOnly": False,
                "secure": secure,
                "sameSite": "Lax",
            }
        )

    origins = []
    if "g_state" in parsed:
        origins.append(
            {
                "origin": "https://x.com",
                "localStorage": [
                    {
                        "name": "g_state",
                        "value": unquote(parsed["g_state"]),
                    }
                ],
            }
        )

    return {
        "cookies": cookies,
        "origins": origins,
    }


def load_cookie_header(cookie_header: str | None, cookie_file: str | None, runtime_dir: Path) -> str:
    if cookie_header:
        return cookie_header.strip()
    if cookie_file:
        return Path(cookie_file).expanduser().read_text(encoding="utf-8").strip()
    runtime_path = runtime_cookie_file(runtime_dir)
    if runtime_path.exists():
        return runtime_path.read_text(encoding="utf-8").strip()
    raise FileNotFoundError("No cookie header provided and no runtime cookie-header.txt found")


def load_storage_state(storage_state: str | None, runtime_dir: Path) -> str:
    if storage_state:
        return str(Path(storage_state).expanduser())
    runtime_path = runtime_state_file(runtime_dir)
    if runtime_path.exists():
        return str(runtime_path)
    raise FileNotFoundError("No storage state provided and no runtime storage-state.json found")


def write_cookie_header(runtime_dir: Path, cookie_header: str) -> Path:
    path = runtime_cookie_file(runtime_dir)
    path.write_text(cookie_header.strip() + "\n", encoding="utf-8")
    return path


def write_storage_state(runtime_dir: Path, storage_state: dict[str, Any]) -> Path:
    path = runtime_state_file(runtime_dir)
    path.write_text(json.dumps(storage_state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def require_playwright() -> Any:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "Missing dependency: playwright. Install it first, then run this skill again."
        ) from exc
    return sync_playwright


def _default_playwright_browsers_path() -> Path:
    home = Path.home()
    if sys.platform == "darwin":
        return home / "Library" / "Caches" / "ms-playwright"
    if sys.platform == "win32":
        return home / "AppData" / "Local" / "ms-playwright"
    return home / ".cache" / "ms-playwright"


def ensure_playwright_browser_hint() -> None:
    env_path = os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    browsers_path = Path(env_path) if env_path else _default_playwright_browsers_path()
    if not browsers_path.exists():
        raise SystemExit(
            "Playwright browser binaries are not installed. Run `python3 -m playwright install chromium` first."
        )
