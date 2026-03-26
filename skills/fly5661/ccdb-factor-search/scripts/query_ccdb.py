#!/usr/bin/env python3
"""CCDB factor query helper for Carbonstop website API.

Search strategy: prefer the smallest core term first, then use bilingual equivalents,
then expand only if recall is weak.
"""

import argparse
import hashlib
import json
import os
import re
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

BUSINESS_LABEL = os.environ.get("CCDB_SIGN_PREFIX", "openclaw_ccdb")
DEFAULT_BASE_URL = os.environ.get(
    "CCDB_API_BASE_URL",
    "https://gateway.carbonstop.com/management/system/website/queryFactorListClaw",
)

CN_TO_EN = {
    "电力": ["electricity", "power"],
    "蒸汽": ["steam", "steam supply", "process steam", "industrial steam", "heat"],
    "天然气": ["natural gas", "gas"],
    "原铝": ["primary aluminium", "primary aluminum", "aluminium"],
    "铝": ["aluminium", "aluminum"],
    "聚酯切片": ["polyester chip", "PET resin", "PET chip"],
    "聚酯": ["polyester", "PET"],
    "PET": ["PET resin", "PET chip", "polyester resin"],
}

TERM_SIMPLIFY = {
    "外购电": "电力",
    "电网电力": "电力",
    "外购蒸汽": "蒸汽",
    "外购天然气": "天然气",
    "管道天然气": "天然气",
    "城市燃气": "天然气",
    "燃气": "天然气",
    "电解铝": "原铝",
    "铝锭": "原铝",
    "PET切片": "聚酯切片",
    "PET树脂": "聚酯切片",
    "聚酯树脂": "聚酯切片",
}

REGION_HINTS = [
    "中国", "全国", "华东", "华北", "华南", "华中", "东北", "西北", "西南",
    "北京", "上海", "广东", "江苏", "浙江", "山东", "欧洲", "美国", "英国", "日本", "非洲",
]

UNIT_PATTERNS = [
    r"kgCO₂e/[A-Za-z%\u4e00-\u9fa5]+",
    r"tCO₂e/[A-Za-z%\u4e00-\u9fa5]+",
    r"kgCO2e/[A-Za-z%\u4e00-\u9fa5]+",
    r"tCO2e/[A-Za-z%\u4e00-\u9fa5]+",
]

YEAR_RE = re.compile(r"(20\d{2})")


def md5_hex(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def make_sign(name: str) -> str:
    return md5_hex(f"{BUSINESS_LABEL}{name}")


def normalize_text(*parts) -> str:
    return " ".join(str(p or "").strip() for p in parts if str(p or "").strip()).lower()


def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def extract_region(text: str) -> str:
    for hint in REGION_HINTS:
        if hint in (text or ""):
            return hint
    return ""


def extract_unit(text: str) -> str:
    for pattern in UNIT_PATTERNS:
        m = re.search(pattern, text or "")
        if m:
            return m.group(0)
    return ""


def extract_year(text: str) -> str:
    m = YEAR_RE.search(text or "")
    return m.group(1) if m else ""


def infer_raw_term(text: str) -> str:
    text = text or ""
    candidates = sorted(set(list(TERM_SIMPLIFY.keys()) + list(CN_TO_EN.keys())), key=len, reverse=True)
    for term in candidates:
        if term in text or term.lower() in text.lower():
            return term
    cleaned = re.sub(r"我要找|请帮我找|请查询|查询|检索|因子|排放因子|碳因子|全国|中国|单位|适合|是否|给我|一个|最合适|有效的|输出|分析", " ", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:20] if cleaned else text[:20]


def simplify_term(term: str) -> str:
    term = (term or "").strip()
    return TERM_SIMPLIFY.get(term, term)


def english_variants(cn_term: str):
    return CN_TO_EN.get(cn_term, []) + CN_TO_EN.get(cn_term.lower(), [])


def build_terms(user_request: str, explicit_query: str = ""):
    raw = explicit_query.strip() if explicit_query else infer_raw_term(user_request)
    core = simplify_term(raw)
    terms = []

    def add(term: str, lang: str, source: str):
        term = (term or "").strip()
        if not term:
            return
        item = {"term": term, "lang": lang, "source": source}
        if item not in terms:
            terms.append(item)

    # smallest core term first
    if contains_chinese(core):
        add(core, "zh", "core_cn")
        for en in english_variants(core):
            add(en, "en", "core_en")
    else:
        add(core, "en", "core_en")

    # then the original raw phrase if different
    if raw != core:
        add(raw, "zh" if contains_chinese(raw) else "en", "raw_term")

    # then only a small number of secondary expansions
    if core == "蒸汽":
        for t in ["steam", "steam supply", "process steam", "industrial steam", "purchased steam", "heat"]:
            add(t, "en", "secondary")
    elif core == "天然气":
        for t in ["natural gas", "pipeline natural gas", "city gas"]:
            add(t, "en", "secondary")
    elif core == "电力":
        for t in ["electricity", "power", "grid electricity"]:
            add(t, "en", "secondary")
    elif core == "原铝":
        for t in ["primary aluminium", "aluminium ingot", "aluminium"]:
            add(t, "en", "secondary")
    elif core == "聚酯切片":
        for t in ["PET resin", "PET chip", "polyester resin"]:
            add(t, "en", "secondary")

    return core, raw, terms


def query_semantic_penalty(core_term: str, row: dict):
    core = normalize_text(core_term)
    text = normalize_text(row.get("name"), row.get("nameEn"), row.get("description"), row.get("specification"))
    penalties = []
    score = 0

    if core in ["聚酯切片", "聚酯", "pet"]:
        if not any(k in text for k in ["polyester", "pet", "resin", "切片", "聚酯"]):
            score -= 18
            penalties.append("material semantics weak for polyester/PET query")
    if core in ["原铝", "铝"]:
        if not any(k in text for k in ["铝", "aluminium", "aluminum"]):
            score -= 15
            penalties.append("material semantics weak for aluminium query")
    if core == "蒸汽":
        if not any(k in text for k in ["steam", "heat", "蒸汽", "thermal"]):
            score -= 12
            penalties.append("steam/heat semantics weak")
        if any(k in text for k in ["steam", "蒸汽"]):
            score += 10
        elif "heat" in text and not any(k in text for k in ["steam", "蒸汽"]):
            score -= 10
            penalties.append("heat may be broader than steam")
    if core == "天然气":
        if not any(k in text for k in ["natural gas", "天然气", "燃气", "gas", "lng"]):
            score -= 15
            penalties.append("natural gas semantics weak")
    if core == "电力":
        if not any(k in text for k in ["electricity", "power", "电力"]):
            score -= 12
            penalties.append("electricity semantics weak")
    return score, penalties


def classify_match(score: int, row: dict, region: str, unit: str, risks: list):
    region_text = normalize_text(row.get("area"), row.get("countries"))
    unit_value = str(row.get("unit") or "")
    region_ok = (not region) or (region.lower() in region_text)
    unit_ok = (not unit) or (unit.lower() == unit_value.lower()) or (unit.lower() in unit_value.lower())
    if 'region mismatch' in risks and region:
        return 'not_suitable'
    if 'unit mismatch' in risks and unit:
        return 'not_suitable'
    if 'monetary unit may be unsuitable for physical activity factor matching' in risks:
        return 'not_suitable'
    if score >= 80 and region_ok and unit_ok:
        return 'direct_match'
    if score >= 60 and not any(r in risks for r in ['region mismatch', 'unit mismatch']):
        return 'close_match'
    if score >= 45 and len(risks) <= 2:
        return 'fallback_generic'
    return 'not_suitable'


def score_row(row: dict, query: str, core_term: str, region: str = '', unit: str = '', year: str = ''):
    score = 0
    reasons = []
    risks = []
    q = (query or '').strip().lower()
    q_tokens = [t for t in re.split(r"[\s/,_\-]+", q) if t]

    name = str(row.get('name') or '')
    name_en = str(row.get('nameEn') or '')
    description = str(row.get('description') or '')
    specification = str(row.get('specification') or '')
    area = str(row.get('area') or '')
    countries = str(row.get('countries') or '')
    unit_value = str(row.get('unit') or '')
    institution = str(row.get('institution') or '')
    source_level = str(row.get('sourceLevel') or '')
    document_type = str(row.get('documentType') or '')
    apply_year = str(row.get('applyYear') or '')
    c_value = str(row.get('cValue') or '')
    factor_classify = str(row.get('factorClassify') or '')

    combined = normalize_text(name, name_en, description, specification)

    if q and (q == name.lower() or q == name_en.lower()):
        score += 50
        reasons.append('exact name match')
    elif q and q in combined:
        score += 30
        reasons.append('query appears in candidate text')

    token_hits = 0
    for token in q_tokens:
        if token in combined:
            token_hits += 1
    if token_hits:
        score += min(20, token_hits * 5)
        reasons.append(f'{token_hits} token(s) matched')

    semantic_penalty, semantic_penalty_reasons = query_semantic_penalty(core_term, row)
    score += semantic_penalty
    risks.extend(semantic_penalty_reasons)

    if region:
        region_text = normalize_text(area, countries)
        if region.lower() in region_text:
            score += 15
            reasons.append('region matched')
        else:
            score -= 18
            reasons.append('region not matched')
            risks.append('region mismatch')

    if unit:
        if unit.lower() == unit_value.lower():
            score += 18
            reasons.append('unit matched exactly')
        elif unit.lower() in unit_value.lower() or unit_value.lower() in unit.lower():
            score += 8
            reasons.append('unit partially matched')
        else:
            score -= 18
            reasons.append('unit not matched')
            risks.append('unit mismatch')

    if year:
        if year == apply_year:
            score += 8
            reasons.append('year matched')
        elif apply_year:
            risks.append('year differs')

    if institution:
        score += 3
    if source_level:
        score += 3
    if document_type:
        score += 1
    if factor_classify:
        score += 1

    if '加密数据' in c_value:
        risks.append('value encrypted')
    if area in {'0', 'null', 'None'}:
        score -= 3
        risks.append('weak area field')
    if any(x in normalize_text(description, specification) for x in ['范畴3', '生产资料', '支出']):
        score -= 8
        risks.append('may be spend-based or scope-3 category factor')
    if any(x in unit_value.lower() for x in ['日元', 'usd', 'eur', '元', 'rmb']) and not any(x in core_term for x in ['金额', '支出', '花费']):
        score -= 18
        risks.append('monetary unit may be unsuitable for physical activity factor matching')

    risks = list(dict.fromkeys(risks))
    return score, reasons, risks


def query_api(base_url: str, name: str, lang: str) -> dict:
    payload = {'sign': make_sign(name), 'name': name, 'lang': lang}
    body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'OpenClaw-CCDB-Skill/1.0',
    }
    req = Request(base_url, data=body, headers=headers, method='POST')
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode('utf-8', errors='replace')
        data = json.loads(raw)
        return {'request': payload, 'response': data, 'ok': True}
    except HTTPError as e:
        detail = e.read().decode('utf-8', errors='replace') if hasattr(e, 'read') else str(e)
        return {
            'request': payload,
            'response': None,
            'ok': False,
            'error': {
                'type': 'http_error',
                'status': getattr(e, 'code', None),
                'message': str(e),
                'detail': detail,
            },
        }
    except URLError as e:
        return {
            'request': payload,
            'response': None,
            'ok': False,
            'error': {
                'type': 'network_error',
                'message': str(e),
            },
        }
    except json.JSONDecodeError as e:
        return {
            'request': payload,
            'response': None,
            'ok': False,
            'error': {
                'type': 'invalid_json',
                'message': str(e),
            },
        }


def run_single_query(base_url: str, query: str, lang: str, core_term: str, region: str, unit: str, year: str, top: int):
    result = query_api(base_url, query, lang)
    if not result.get('ok'):
        return {
            'query': query,
            'lang': lang,
            'request': result['request'],
            'code': None,
            'msg': 'api_error',
            'total': 0,
            'ranked_candidates': [],
            'error': result.get('error'),
        }

    response = result.get('response') or {}
    rows = response.get('rows') or []
    ranked = []
    for row in rows:
        score, reasons, risks = score_row(row, query, core_term, region, unit, year)
        ranked.append({
            'score': score,
            'classification': classify_match(score, row, region, unit, risks),
            'reasons': reasons,
            'risks': risks,
            'candidate': row,
        })
    ranked.sort(key=lambda x: x['score'], reverse=True)
    return {
        'query': query,
        'lang': lang,
        'request': result['request'],
        'code': response.get('code'),
        'msg': response.get('msg'),
        'total': response.get('total'),
        'ranked_candidates': ranked[:top],
        'error': None,
    }


def dedupe_candidates(search_runs):
    merged = {}
    for run in search_runs:
        if run.get('error'):
            continue
        for cand in run.get('ranked_candidates', []):
            row = cand['candidate']
            key = row.get('id') or f"{row.get('name')}|{row.get('unit')}|{row.get('institution')}"
            enriched = {'from_query': run.get('query'), 'from_lang': run.get('lang'), **cand}
            existing = merged.get(key)
            if existing is None or enriched['score'] > existing['score']:
                merged[key] = enriched
    return sorted(merged.values(), key=lambda x: x['score'], reverse=True)


def explain_best(best, alternatives, constraints, core_term):
    if not best or best.get('classification') == 'not_suitable':
        suggestions = []
        if core_term == '蒸汽':
            suggestions = ['蒸汽', 'steam', 'steam supply', 'process steam', 'industrial steam', 'purchased steam']
        elif core_term == '天然气':
            suggestions = ['天然气', 'natural gas', 'pipeline natural gas', 'city gas', 'natural gas combustion']
        elif core_term == '聚酯切片':
            suggestions = ['聚酯切片', 'PET resin', 'PET chip', 'polyester resin']
        top_alts = []
        for alt in alternatives[:3]:
            r = alt['candidate']
            top_alts.append({
                'name': r.get('name'),
                'nameEn': r.get('nameEn'),
                'unit': r.get('unit'),
                'countries': r.get('countries'),
                'score': alt.get('score'),
                'classification': alt.get('classification'),
                'risks': alt.get('risks'),
            })
        return {
            'selected': None,
            'classification': 'not_suitable',
            'why': 'No reliable direct/close/fallback candidate met the current constraints after searching from the smallest core term outward.',
            'mismatch_risks': ['no suitable candidate found'],
            'constraints_used': constraints,
            'alternatives_considered': top_alts,
            'query_refinement_suggestions': suggestions,
            'next_action': 'Retry with a nearby core noun or provide more precise stage/region/unit constraints.'
        }

    row = best['candidate']
    why_parts = [
        f"Selected because score={best['score']} and classification={best['classification']}",
        f"matched via query '{best['from_query']}' ({best['from_lang']}) from core term '{core_term}'",
    ]
    if best.get('reasons'):
        why_parts.append('; '.join(best['reasons']))

    alt_summary = []
    for alt in alternatives[:3]:
        r = alt['candidate']
        alt_summary.append({
            'name': r.get('name'), 'nameEn': r.get('nameEn'), 'unit': r.get('unit'),
            'countries': r.get('countries'), 'score': alt.get('score'),
            'classification': alt.get('classification'), 'risks': alt.get('risks'),
        })

    return {
        'selected': row,
        'classification': best['classification'],
        'why': ' | '.join(why_parts),
        'mismatch_risks': best.get('risks', []),
        'constraints_used': constraints,
        'alternatives_considered': alt_summary,
        'recommended_result': {
            '匹配等级': best['classification'],
            '因子名称': row.get('name'),
            '英文名称': row.get('nameEn'),
            '因子值': row.get('cValue'),
            '单位': row.get('unit'),
            '适用地区': row.get('area') or row.get('countries'),
            '适用年份': row.get('applyYear'),
            '来源机构': row.get('institution'),
            '来源说明': row.get('source'),
            '选择原因': ' | '.join(why_parts),
            '风险与注意事项': best.get('risks', []),
        },
        'next_action': 'Use as direct/close match if acceptable, otherwise refine with a nearby synonym or more precise stage/region details.'
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', default='')
    parser.add_argument('--user-request', default='')
    parser.add_argument('--lang', default='zh', choices=['zh', 'en'])
    parser.add_argument('--base-url', default=DEFAULT_BASE_URL)
    parser.add_argument('--region', default='')
    parser.add_argument('--unit', default='')
    parser.add_argument('--year', default='')
    parser.add_argument('--top', type=int, default=5)
    parser.add_argument('--auto', action='store_true')
    args = parser.parse_args()

    if args.auto or args.user_request:
        user_request = args.user_request or args.query
        region = args.region or extract_region(user_request)
        unit = args.unit or extract_unit(user_request)
        year = args.year or extract_year(user_request)
        constraints = {'region': region, 'unit': unit, 'year': year}
        core_term, raw_term, terms = build_terms(user_request, args.query)
        runs = []
        for item in terms[:8]:
            runs.append(run_single_query(args.base_url, item['term'], item['lang'], core_term, region, unit, year, args.top))
        api_errors = [r for r in runs if r.get('error')]
        if api_errors and not any(r.get('ranked_candidates') for r in runs):
            print(json.dumps({
                'ok': False,
                'mode': 'auto',
                'user_request': user_request,
                'core_term': core_term,
                'raw_term': raw_term,
                'derived_constraints': constraints,
                'terms': terms,
                'search_runs': runs,
                'analysis': {
                    'selected': None,
                    'classification': 'api_unavailable',
                    'why': 'CCDB API request failed across all attempted search terms; returning no recommendation to avoid a misleading factor match.',
                    'mismatch_risks': ['api unavailable'],
                    'constraints_used': constraints,
                    'alternatives_considered': [],
                    'next_action': 'Retry later or verify API endpoint / network / signing configuration.',
                },
            }, ensure_ascii=False, indent=2))
            return 1
        merged = dedupe_candidates(runs)
        best = merged[0] if merged else None
        explanation = explain_best(best, merged[1:], constraints, core_term)
        print(json.dumps({
            'ok': True,
            'mode': 'auto',
            'user_request': user_request,
            'core_term': core_term,
            'raw_term': raw_term,
            'derived_constraints': constraints,
            'terms': terms,
            'search_runs': runs,
            'merged_candidates': merged[:10],
            'best_match': best,
            'analysis': explanation,
        }, ensure_ascii=False, indent=2))
        return 0

    core_term = simplify_term(args.query)
    result = run_single_query(args.base_url, args.query, args.lang, core_term, args.region, args.unit, args.year, args.top)
    print(json.dumps({'ok': True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
