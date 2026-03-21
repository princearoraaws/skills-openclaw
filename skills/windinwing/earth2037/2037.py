#!/usr/bin/env python3
"""
Earth2037 Game Skill - CLI entry (English)
Calls GameSkillAPI for key, register, login, apply. Uses stdlib urllib, no pip install.
"""

import json
import os
import sys
import urllib.error
import urllib.request


def load_config(api_base_override=None):
    """Read apiBase from env, config.json. Priority: api_base_override > EARTH2037_API_BASE > apiBase"""
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

    if api_base_override:
        return api_base_override.rstrip("/")
    env_base = os.environ.get("EARTH2037_API_BASE", "").strip()
    if env_base:
        return env_base.rstrip("/")
    return api_base.rstrip("/")


def http_get(url):
    req = urllib.request.Request(url, method="GET")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_post(url, data):
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def cmd_key(api_base):
    url = f"{api_base}/auth/key?skill_id=2037"
    try:
        r = http_get(url)
        if r.get("ok") and r.get("key"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print("\nKey obtained. Long-term valid. Save for register/bind.")
        else:
            print(json.dumps(r, ensure_ascii=False))
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def _parse_tribe_id(t):
    if t is None or t == "":
        return 1
    m = {"1": 1, "2": 2, "3": 3, "human": 1, "empire": 2, "eagle": 3}
    return m.get(str(t).strip().lower(), int(t) if str(t).isdigit() else 1)


def cmd_register(api_base, username, password, tribe_id=None):
    url = f"{api_base}/auth/register"
    tid = _parse_tribe_id(tribe_id)
    try:
        r = http_post(url, {"username": username, "password": password, "tribe_id": tid})
        if r.get("ok") and r.get("token"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print("\nRegistered. Put token in OpenClaw 2037 API Key config.")
        else:
            print(json.dumps(r, ensure_ascii=False))
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def cmd_login(api_base, username, password):
    url = f"{api_base}/auth/token"
    try:
        r = http_post(url, {"username": username, "password": password})
        if r.get("ok") and r.get("token"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print("\nLogged in. Put token in OpenClaw 2037 API Key config.")
        else:
            print(json.dumps(r, ensure_ascii=False))
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def cmd_apply(api_base, username, password, key, action="register", tribe_id=None):
    url = f"{api_base}/auth/apply"
    tid = _parse_tribe_id(tribe_id)
    try:
        r = http_post(
            url,
            {
                "username": username,
                "password": password,
                "action": action,
                "key": key,
                "skill_id": "2037",
                "tribe_id": tid,
            },
        )
        if r.get("ok") and r.get("token"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print("\nDone. Put token in OpenClaw 2037 API Key config.")
        else:
            print(json.dumps(r, ensure_ascii=False))
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)


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


def cmd_newkey(api_base):
    token = _get_token()
    if not token:
        print("No token. Set EARTH2037_TOKEN or token/apiKey in config.json")
        sys.exit(1)
    url = f"{api_base}/auth/newkey"
    body = json.dumps({"skill_id": "2037"}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            r = json.loads(resp.read().decode("utf-8"))
        if r.get("ok") and r.get("token"):
            print(json.dumps(r, ensure_ascii=False, indent=2))
            print("\nNew key generated. Old key invalid. Update OpenClaw 2037 API Key config.")
        else:
            print(json.dumps(r, ensure_ascii=False))
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)


def cmd_sync(api_base):
    try:
        from cache import sync as cache_sync
        ui, cs = cache_sync(api_base=api_base)
        print("Cache updated")
        print(f"  userinfo.json: userID={ui.get('UserID')}, CapitalID={ui.get('CapitalID')}")
        print(f"  citys.json: {len(cs)} cities")
    except Exception as e:
        print(f"Sync failed: {e}")
        sys.exit(1)


def main():
    args = sys.argv[1:]
    api_base_override = None
    while args and args[0].startswith("--"):
        if args[0] == "--api-base" and len(args) > 1:
            api_base_override = args[1]
            args = args[2:]
        else:
            args = args[1:]

    if len(args) < 1:
        print("Usage: 2037.py [--api-base URL] key | newkey | register <user> <pwd> [tribe_id] | login <user> <pwd> | apply <user> <pwd> <key> [tribe_id] | sync")
        print("  tribe_id: 1=Human 2=Empire 3=Eagle, default 1")
        sys.exit(1)

    api_base = load_config(api_base_override=api_base_override)
    cmd = args[0].lower()

    if cmd == "sync":
        cmd_sync(api_base)
    elif cmd == "newkey":
        cmd_newkey(api_base)
    elif cmd == "key":
        cmd_key(api_base)
    elif cmd == "register":
        if len(args) < 4:
            print("Usage: 2037.py register <username> <password> [tribe_id]")
            sys.exit(1)
        tribe_id = args[4] if len(args) > 4 else None
        cmd_register(api_base, args[2], args[3], tribe_id)
    elif cmd == "login":
        if len(args) < 4:
            print("Usage: 2037.py login <username> <password>")
            sys.exit(1)
        cmd_login(api_base, args[2], args[3])
    elif cmd == "apply":
        if len(args) < 5:
            print("Usage: 2037.py apply <username> <password> <key> [tribe_id]")
            sys.exit(1)
        tribe_id = args[5] if len(args) > 5 else None
        cmd_apply(api_base, args[2], args[3], args[4], tribe_id=tribe_id)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
