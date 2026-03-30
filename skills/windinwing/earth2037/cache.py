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


def _auth_401_hint(token):
    t = (token or "").strip()
    if t.upper().startswith("SK-"):
        return "「SK-」开头的是注册/绑定用 key，不能当 Bearer。请执行 2037.py login 用户名 密码，或 curl POST /auth/token，使用返回的 token。"
    return "请检查 EARTH2037_TOKEN：应用 2037.py login 或 POST /auth/token、/auth/apply 返回的长 token（32 位十六进制），不是 SK- key。"


def _post_bootstrap(api_base, token):
    import urllib.request
    import urllib.error
    url = f"{api_base}/game/bootstrap"
    body = json.dumps({}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise RuntimeError("HTTP 401 Unauthorized。 " + _auth_401_hint(token)) from e
        raise
    with resp:
        r = json.loads(resp.read().decode("utf-8"))
    if not r.get("ok"):
        raise RuntimeError(r.get("err", "bootstrap failed"))
    return r.get("data")


def _game_command(api_base, token, cmd, args=""):
    import urllib.request
    import urllib.error
    url = f"{api_base}/game/command"
    body = json.dumps({"cmd": cmd, "args": args or ""}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/json")
    try:
        resp = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise RuntimeError("HTTP 401 Unauthorized。 " + _auth_401_hint(token)) from e
        raise
    with resp:
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


def bootstrap(api_base=None, token=None):
    api_base = api_base or _load_config()
    token = token or _get_token()
    if not token:
        raise ValueError("Token required: set EARTH2037_TOKEN or token/apiKey in config.json")

    data = _post_bootstrap(api_base, token)
    cache_dir = _cache_dir()
    path = os.path.join(cache_dir, "session_cache.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if isinstance(data, dict):
        ui = data.get("userinfo")
        if isinstance(ui, str):
            try:
                ui = json.loads(ui)
            except (json.JSONDecodeError, TypeError):
                ui = None
        if isinstance(ui, dict):
            with open(os.path.join(cache_dir, "userinfo.json"), "w", encoding="utf-8") as f:
                json.dump(ui, f, ensure_ascii=False, indent=2)
        cl = data.get("citylist")
        if isinstance(cl, str):
            try:
                cl = json.loads(cl)
            except (json.JSONDecodeError, TypeError):
                cl = None
        if isinstance(cl, list):
            with open(os.path.join(cache_dir, "citys.json"), "w", encoding="utf-8") as f:
                json.dump(cl, f, ensure_ascii=False, indent=2)

    return data


def load_session_cache():
    path = os.path.join(_cache_dir(), "session_cache.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


_CACHE_SECTIONS = [
    ("userinfo", "[account]"),
    ("citylist", "[cities]"),
    ("citybuildlist", "[city buildings]"),
    ("buildlist", "[building types]"),
    ("getbuildcosts2", "[build costs]"),
    ("getuserbuildqueue", "[build queue]"),
    ("getcitytroops", "[garrison]"),
    ("gettasklist", "[tasks]"),
    ("getconscriptionqueue", "[conscription]"),
    ("usertroopssciencequeue", "[troop science queue]"),
    ("armies", "[army types]"),
    ("usercitymilitarysciences", "[city military tech]"),
    ("getoutput", "[output]"),
    ("userheros", "[heroes]"),
    ("goodslist", "[goods catalog]"),
    ("usergoodslist", "[inventory]"),
    ("combatqueue", "[march queue]"),
    ("nm", "[nm]"),
    ("airinfo", "[air]"),
]

_CACHE_FOCUS = {
    "city": {"citylist"},
    "cities": {"citylist"},
    "build": {"citybuildlist", "buildlist", "getbuildcosts2", "getuserbuildqueue"},
    "troops": {"armies", "getcitytroops", "usercitymilitarysciences"},
    "military": {"armies", "getcitytroops", "usercitymilitarysciences"},
    "task": {"gettasklist"},
    "queue": {"getuserbuildqueue", "getconscriptionqueue", "combatqueue", "usertroopssciencequeue"},
    "hero": {"userheros"},
    "goods": {"goodslist", "usergoodslist"},
}


def show_cache(focus=None):
    data = load_session_cache()
    if not data:
        print("No session_cache.json. Run: python3 2037.py bootstrap", file=sys.stderr)
        return 1

    fkey = (focus or "all").strip().lower()
    allowed = None
    if fkey not in ("", "all", "a"):
        allowed = _CACHE_FOCUS.get(fkey)
        if allowed is None:
            print("Unknown focus. Use: all city build troops task queue hero goods", file=sys.stderr)
            return 1

    printed = False
    for key, title in _CACHE_SECTIONS:
        if key not in data:
            continue
        if allowed is not None and key not in allowed:
            continue
        printed = True
        print(title)
        print(json.dumps(data[key], ensure_ascii=False, indent=2))
        print()

    for mk in ("_meta", "_errors"):
        if mk in data and allowed is None:
            print(f"[{mk}]")
            print(json.dumps(data[mk], ensure_ascii=False, indent=2))
            print()

    if "_meta" in data and allowed is not None:
        print("[_meta]")
        print(json.dumps(data["_meta"], ensure_ascii=False, indent=2))
        print()

    if not printed and allowed is not None:
        print("(no data for this focus)", file=sys.stderr)
        return 1
    return 0


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
    elif len(sys.argv) > 1 and sys.argv[1] == "bootstrap":
        try:
            bootstrap()
            print("Wrote session_cache.json")
        except Exception as e:
            print(f"Bootstrap failed: {e}")
            sys.exit(1)
    elif len(sys.argv) > 1 and sys.argv[1] == "show":
        focus = sys.argv[2] if len(sys.argv) > 2 else None
        sys.exit(show_cache(focus))
    else:
        print("Usage: python3 cache.py sync | bootstrap | show [city|build|troops|...]")
        print("  Requires token for sync/bootstrap; show reads session_cache.json only")
