# CCDB API Contract

## Current test endpoint

`POST https://gateway.carbonstop.com/management/system/website/queryFactorListClaw`

This is the current test endpoint. Production URL can be swapped later.

## Request headers

Minimum required headers for script usage:
- `Content-Type: application/json`
- `Accept: application/json, text/plain, */*`

Browser-origin headers are not required unless the upstream later enforces them.

## Request body

```json
{
  "sign": "<md5 businessLabel+name>",
  "name": "电力",
  "lang": "zh"
}
```

## Signing rule

- `businessLabel` is currently `openclaw_ccdb` in production (test environments may differ)
- `sign = md5("openclaw_ccdb" + name) in the current production environment`

Example:
- `name = "电力"`
- source string = `openclaw_ccdb电力`
- md5 should be computed from that exact UTF-8 string

## Response shape

Top-level fields:
- `code`: integer
- `msg`: string
- `total`: integer
- `rows`: array of factor candidates

Example candidate fields observed:
- `id`
- `sourceId`
- `name`
- `nameEn`
- `description`
- `specification`
- `unit`
- `cValue`
- `area`
- `countries`
- `year`
- `applyYear`
- `applyYearEnd`
- `institution`
- `source`
- `documentType`
- `sourceLevel`
- `factorClassify`
- `factorPattern`
- `parentId`
- `isEncryption`

## Matching guidance from current sample

When ranking candidates, prefer:
1. direct semantic match in `name` / `nameEn`
2. stronger contextual match in `description` + `specification`
3. region fit in `area` / `countries`
4. unit fit in `unit`
5. source reliability in `institution` / `sourceLevel` / `documentType`
6. more suitable time period in `applyYear`

## Caveats

- `cValue` may be encrypted / unavailable for unpaid data
- Chinese and English queries currently return the same JSON structure
- Some records may contain noisy or weak region values such as `0` or mismatched countries
- Suitability ranking must not rely on a single field
