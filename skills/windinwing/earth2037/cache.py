#!/usr/bin/env python3
"""
Earth2037 local cache: fetch userinfo, citys to local JSON for mapping (capital tileID, city names).
Requires token. Run 2037.py sync to trigger.
"""

import json
import os
import re
import sys


def _load_config():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    api_base = "https://2037en1.9235.net"
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                api_base = cfg.get("apiBase", api_base)
        except (json.JSONDecodeError, IOError):
            pass
    return api_base.rstrip("/")


def _get_token():
    token = os.environ.get("EARTH2037_TOKEN", "").strip()
    if token:
        return token
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return (cfg.get("token") or cfg.get("apiKey") or "").strip()
        except (json.JSONDecodeError, IOError):
            pass
    return ""


def _game_command(api_base, token, cmd, args=""):
    import urllib.request
    import urllib.error
    url = f"{api_base}/game/command"
    body = json.dumps({"cmd": cmd, "args": args or ""}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        r = json.loads(resp.read().decode("utf-8"))
    if not r.get("ok"):
        raise RuntimeError(r.get("err", "unknown error"))
    return r.get("data") or ""


def _parse_svr_json(data, prefix):
    if not data or not isinstance(data, str):
        return None
    pat = re.compile(r"^/svr\s+" + re.escape(prefix) + r"\s+(.+)$", re.IGNORECASE)
    m = pat.match(data.strip())
    if not m:
        return None
    raw = m.group(1).strip()
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _cache_dir():
    return os.path.dirname(os.path.abspath(__file__))


def sync(api_base=None, token=None):
    api_base = api_base or _load_config()
    token = token or _get_token()
    if not token:
        raise ValueError("Token required: set EARTH2037_TOKEN or token/apiKey in config.json")

    raw_user = _game_command(api_base, token, "USERINFO", "")
    userinfo = _parse_svr_json(raw_user, "userinfo")
    if userinfo is None:
        raise RuntimeError("USERINFO parse failed: " + (raw_user[:200] if raw_user else "no data"))

    raw_city = _game_command(api_base, token, "CITYLIST", "")
    citys = _parse_svr_json(raw_city, "citylist")
    if citys is None:
        citys = []
    if not isinstance(citys, list):
        citys = [citys] if citys else []

    cache_dir = _cache_dir()
    userinfo_path = os.path.join(cache_dir, "userinfo.json")
    citys_path = os.path.join(cache_dir, "citys.json")

    with open(userinfo_path, "w", encoding="utf-8") as f:
        json.dump(userinfo, f, ensure_ascii=False, indent=2)

    with open(citys_path, "w", encoding="utf-8") as f:
        json.dump(citys, f, ensure_ascii=False, indent=2)

    return userinfo, citys


def load_userinfo():
    path = os.path.join(_cache_dir(), "userinfo.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_citys():
    path = os.path.join(_cache_dir(), "citys.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data if isinstance(data, list) else []


def get_capital_id():
    u = load_userinfo()
    if not u:
        return None
    return u.get("CapitalID") or u.get("capitalID")


def get_tile_by_name(name):
    citys = load_citys()
    if not citys:
        return get_capital_id() if name in ("capital", "main") else None
    name = (name or "").strip().lower()
    if name in ("capital", "main"):
        for c in citys:
            if c.get("IsCapital") or c.get("isCapital"):
                return c.get("TileID") or c.get("tileID")
        return get_capital_id() or (citys[0].get("TileID") if citys else None)
    for c in citys:
        if (c.get("Name") or c.get("name") or "").lower() == name:
            return c.get("TileID") or c.get("tileID")
    return None


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        try:
            ui, cs = sync()
            print("Cache updated")
            print(f"  userinfo.json: userID={ui.get('UserID')}, CapitalID={ui.get('CapitalID')}")
            print(f"  citys.json: {len(cs)} cities")
        except Exception as e:
            print(f"Sync failed: {e}")
            sys.exit(1)
    else:
        print("Usage: python3 cache.py sync")
        print("  Requires token (EARTH2037_TOKEN or config.json)")
