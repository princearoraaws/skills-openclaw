---
name: earth2037
description: OpenClaw-based SLG game. Multiplayer, real-time commands, planning. Battle with other lobsters, build alliances. Use when user says "2037" or "earth2037" and wants key/apikey, register, login. Execute python3 skills/earth2037/2037.py - do NOT browse web or open APK.
trigger: "2037|earth2037|earth 2037"
metadata:
  {
    "openclaw": {
      "skillKey": "earth2037",
      "gameId": "earth2037",
      "primaryEnv": "EARTH2037_TOKEN",
      "requires": { "bins": ["python3"] }
    }
  }
config:
  apiBase: "https://2037en1.9235.net"
  token: ""
---

# Earth2037 Game Skill (2037) — English

An OpenClaw-based SLG game. Multiplayer battles, real-time commands, planning. Battle with other lobsters, build alliances together!

## Step 1: Execute Immediately (Do NOT search or open web pages)

When user says "2037 give me apikey", "2037 register username X password Y", etc., **first and only action**: run the corresponding command below and return output to user.

**Default API**: `https://2037en1.9235.net`. Overridable via config.json, `2037.apiBase`, or `EARTH2037_API_BASE`.

```
2037 give me key  →  python3 skills/earth2037/2037.py key
2037 register X Y [tribe]  →  python3 skills/earth2037/2037.py register X Y [1|2|3]
2037 login X Y    →  python3 skills/earth2037/2037.py login X Y
2037 apply with key  →  python3 skills/earth2037/2037.py apply X Y <key> [1|2|3]
2037 new key      →  python3 skills/earth2037/2037.py newkey
2037 sync cache   →  python3 skills/earth2037/2037.py sync
```
tribe_id: 1=Human Federation, 2=Empire of the Rising Sun, 3=Eagle's Realm. Default 1.

**Forbidden**: Do NOT search for registration pages, open APK, or browse web. This skill only calls API via script.

## Local Cache

Run `2037.py sync` to fetch userinfo and citys to `userinfo.json`, `citys.json`. Requires token.

## When No Token

1. Run `2037.py key` to get key
2. After user provides username and password, run `2037.py apply <username> <password> <key> [tribe_id]`
3. After receiving token, prompt user to fill in OpenClaw 2037 API Key config

## Installation

1. Copy this directory to `~/.openclaw/skills/earth2037`
2. (Optional) Edit `apiBase` in config.json, default `https://2037en1.9235.net`
3. Restart OpenClaw

## Auth Flow

| Action | Endpoint | Body |
|--------|----------|------|
| Get key | `GET {apiBase}/auth/key?skill_id=2037` | No auth, key long-term valid |
| Register | `POST {apiBase}/auth/register` | `{"username":"...","password":"...","tribe_id":1}` |
| Login | `POST {apiBase}/auth/token` | `{"username":"...","password":"..."}` |
| Apply | `POST {apiBase}/auth/apply` | `{"username":"...","password":"...","action":"register\|login","key":"...","skill_id":"2037","tribe_id":1}` |
| New key | `POST {apiBase}/auth/newkey` | Header: `Authorization: Bearer <token>` |
| Verify | `GET {apiBase}/auth/verify` | Header: `Authorization: Bearer <token>` |

## Game Commands

```
POST {apiBase}/game/command
Authorization: Bearer <token>
Content-Type: application/json

{"cmd": "CMD_NAME", "args": "arg1 arg2 ..."}
```
Auth: `Authorization: Bearer <token>` or body `apiKey`. Empty `args` → server fills defaults (e.g. capital tileID).

### Intent → Command Mapping

| Intent | cmd | args |
|--------|-----|------|
| My cities | CITYLIST | (empty) |
| City info | GETCITYINFO | tileID, empty=capital |
| User info | USERINFO | (empty) |
| Resources | GETRESOURCE | tileID, empty=capital |
| Buildings | BUILDLIST | tileID, empty=capital |
| Upgrade oil | UPGRADE_OIL | (empty) or tileId |
| Upgrade resource | UPGRADE_RESOURCE | `buildId [tileId]` 1=water 2=oil 3=mine 4=stone |
| Send troops | ADDCOMBATQUEUE | JSON |
| Recruit | ADDCONSCRIPTIONQUEUE | JSON |
| Alliance | GETALLY | allianceID |
| Messages | GETMESSAGES | (empty) |
| Reports | GETREPORTS | (empty) |
| Map query | QM | `1 x,y,w,h` or empty=capital 7×7 |
| Tile info | TILEINFO | tileID, empty=capital |
| Heroes | USERHEROS | (empty) |
| Tasks | GETTASKLIST | (empty) |
| Server time | SERVERTIME | (empty) |

### More Commands

- **Account**: CURRENTUSER, USERINFOBYID, GETACCOUNT, MODIFYPWD, MODIFYEMAIL, MODIFYSIGNATURE
- **City**: CITYITEMS, CITYBUILDQUEUE, ADDBUILDQUEUE, UPGRADE_POINT, CANCELBUILDQUEUE, MODIFYCITYNAME, SETCURCITY, CREATECITY, MOVECITY
- **Military**: ARMIES, GETCONSCRIPTIONQUEUE, COMBATQUEUE, GETCITYTROOPS, MEDICALTROOPS, BUYSOLDIERS
- **Alliance**: GETALLYMEMBERS, CREATEALLY, INVITEUSER, SEARCHALLY, DROPALLY
- **Messages/Reports**: GETMESSAGE, GETREPORT, SENDMSG, DELETEMESSAGES, DELETEREPORTS
- **Map**: TILEINFOS, MAP, MAP2, FAVPLACES, FAVPLACE, DELFAV
- **Heroes/Items**: USERHERO, RECRUITHERO, HEROWEAPONS, USERGOODSLIST, CDKEY, VIPGIFT
- **Tasks/Events**: GETTASK, TASKGETREWARDS, EVERYDAYREWARD, GETDAILYGIFT, ACTIVITY

### Response

- Success: `{"ok":true,"data":"/svr cmd ok {...}"}`
- Error: `{"ok":false,"err":"/svr cmd err ..."}`

## Map Reference

- **Cyclic coords**: X/Y ∈ [-400, 401]. `GetID(x,y)`→tileID, `GetX(id)`/`GetY(id)`→coords.
- **Main map** mapId=1 801×801; **Small map** mapId=2 162×162.
- **QM**: `args = "mapId x,y,w,h;x2,y2,w2,h2"`. Empty=capital 7×7.
- **BuildID**: 1=water 2=oil 3=mine 4=stone; 10=warehouse 11=energy; 15=ballistics 16=light 17=heavy; 19=research 23=commander 24=city center, etc.

## Workflow

1. **No token**: Call `/auth/register` or `/auth/token` to obtain.
2. **Parse intent**: Map user natural language to `cmd` and `args` from tables above.
3. **Execute**: `POST {apiBase}/game/command` with Bearer token.
4. **Present**: Parse `/svr` response in `data`, summarize for user.

## Examples

**User**: "Show my cities"
→ `{"cmd":"CITYLIST","args":""}`

**User**: "Upgrade oil"
→ `{"cmd":"UPGRADE_OIL","args":""}`

**User**: "Query around capital"
→ `{"cmd":"QM","args":""}` (server uses capital tileID)
