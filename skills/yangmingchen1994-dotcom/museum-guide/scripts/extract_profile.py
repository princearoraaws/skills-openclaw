#!/usr/bin/env python3
"""
基于大模型的博物馆参观信息提取工具
"""

import sys
import json
import requests
import re
from pathlib import Path
from typing import Dict, Optional, List

def load_api_config() -> dict:
    """从配置文件加载大模型配置"""

    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        api_base = config.get("API_BASE", "")
        if api_base and not api_base.endswith("/chat/completions"):
            api_base = f"{api_base.rstrip('/')}/chat/completions"

        return {
            "api_key": config.get("API_KEY", ""),
            "api_base": api_base,
            "model": config.get("MODEL_NAME", ""),
            "provider": "config",
            "api_type": "openai-completions"
        }

    raise ValueError("未配置 API Key，请在 scripts/config.json 中配置")

API_CONFIG = load_api_config()

PROMPT_TEMPLATE = """
你是一位专业的博物馆参观路线规划助手，请从用户的输入中提取以下7个维度的信息：
1. 博物馆名称（如：故宫博物院、中国国家博物馆、上海博物馆，尽量使用全称）
2. 计划参观时间（只能是：2-3小时、4-5小时，无法确定则返回null）
3. 是否首次参观（只能是：是、否，无法确定则返回null）
4. 是否携带儿童（只能是：是、否，无法确定则返回null）
5. 关注的领域（从以下列表中选择：农耕、狩猎、饮食、建筑、人物、武器、文房四宝、牌章证件、货币、书法、绘画、雕像、服装、饰品、仪器、佛教、乐器、纹饰、花瓶、礼制、古生物、新石器、旧石器、陈设品、科技、其他，可多选）
6. 喜欢的文物种类（从以下列表中选择：铜器、陶器、瓷器、漆器、玉器宝石、金银器、石器石刻、书画古籍、服饰、砖瓦、钱币、化石、其他，可多选）
7. 着重关注的朝代（从以下列表中选择：远古时期、夏商西周、春秋战国、秦汉、三国两晋南北朝、隋唐五代、辽宋夏金元、明清，可多选）

用户输入：{user_input}

请严格按照以下JSON格式返回结果，不要添加任何其他内容：
{{
    "museum_name": "提取的博物馆名称或简称",
    "duration": "2-3小时"/"4-5小时"/null,
    "first_visit": "是"/"否"/null,
    "with_children": "是"/"否"/null,
    "domains": ["关注领域1", "关注领域2", ...],
    "artifact_types": ["文物种类1", "文物种类2", ...],
    "dynasties": ["朝代1", "朝代2", ...]
}}
"""

# 缺失字段默认（与 SKILL.md 对齐）
DEFAULT_DURATION = "2-3小时"
DEFAULT_WITH_CHILDREN = False
DEFAULT_DOMAINS_DOC = ["绘画", "书法", "瓷器", "玉器"]
DEFAULT_DYNASTIES_DOC = ["隋唐", "辽宋夏金元", "明清"]

# 博物馆别名映射（简称 → 全称）
MUSEUM_ALIAS = {
    "国博": "中国国家博物馆",
    "故宫": "故宫博物院",
    "上博": "上海博物馆",
    "南博": "南京博物院",
    "陕博": "陕西历史博物馆",
    "湘博": "湖南省博物馆",
    "鄂博": "湖北省博物馆",
    "川博": "四川博物院",
    "浙博": "浙江省博物馆",
    "广博": "广东省博物馆",
    "首博": "首都博物馆",
    "苏博": "苏州博物馆",
    "河博": "河南博物院",
    "晋博": "山西博物院",
    "辽博": "辽宁省博物馆",
    "甘博": "甘肃省博物馆",
    "云博": "云南省博物馆",
    "三峡博物馆": "重庆中国三峡博物馆",
    "成博": "成都博物馆",
    "西博": "西安博物院",
    "洛博": "洛阳博物馆",
}

# 专科博物馆关键词（包含这些关键词的博物馆跳过确认）
SPECIALTY_MUSEUM_KEYWORDS = [
    "兵马俑", "秦始皇帝陵", "秦始皇陵",
    "军事", "军博", "航空", "航天",
    "铁路", "火车", "轨道交通",
    "自然", "地质", "科技", "天文", "海洋", "生物", "植物", "动物",
    "昆虫", "古生物", "化石",
    "陶瓷", "玉器", "钱币", "邮票", "印章", "家具", "织绣", "服饰",
    "民族", "民俗", "人类学", "非遗", "非物质文化遗产",
    "美术", "书法", "绘画", "雕塑", "摄影",
    "汽车", "党史", "革命", "历史纪念馆", "烈士陵园",
    "大学博物馆", "高校博物馆",
    "石窟", "船舶", "航海", "航运", "轮船", "桥梁", "隧道",
    "气象", "湿地", "沼泽", "火山",
    "冰川", "冰河", "恐龙", "花卉", "园艺", "园林",
    "电影", "通信", "电信", "邮政",
    "戏剧", "戏曲", "曲艺",
    "音乐", "乐器", "体育", "奥林匹克","茶叶"
]


def is_specialty_museum(museum_name: str) -> bool:
    """判断是否是专科博物馆"""
    if not museum_name:
        return False
    for keyword in SPECIALTY_MUSEUM_KEYWORDS:
        if keyword in museum_name:
            return True
    return False

def call_llm_api(prompt: str) -> Dict:
    """调用大模型API获取提取结果"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_CONFIG['api_key']}"
    }

    data = {
        "model": API_CONFIG['model'],
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1,
        "max_tokens": 4000,
        "thinking": {"type": "disabled"}
    }

    try:
        response = requests.post(API_CONFIG['api_base'], headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()

        # 解析返回的JSON
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            # 清理可能的markdown格式
            content = content.replace("```json", "").replace("```", "").strip()
            # 去除 <think>...</think> 推理标签
            import re as _re
            content = _re.sub(r'<think>.*?</think>', '', content, flags=_re.DOTALL).strip()
            # 提取第一个 JSON 对象或数组
            match = _re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', content)
            if match:
                content = match.group(1)
            return json.loads(content)
        else:
            return {"error": "Invalid API response"}
    except Exception as e:
        print(f"调用大模型API失败: {e}", file=sys.stderr)
        return {"error": str(e)}

def standardize_museum_name(name: str) -> str:
    """标准化博物馆名称，将简称转换为全称"""
    if not name:
        return None

    for alias, full_name in MUSEUM_ALIAS.items():
        import re
        pattern = r'(^' + re.escape(alias) + r'(?:博物院|博物馆|$)|(?:^|博物院|博物馆)' + re.escape(alias) + r'$)'
        if re.search(pattern, name):
            return full_name

    return name

def extract_profile(user_input: str) -> Dict:
    """从用户输入中提取参观信息（使用大模型）"""
    # 构建prompt
    prompt = PROMPT_TEMPLATE.format(user_input=user_input)

    # 调用大模型
    llm_result = call_llm_api(prompt)

    # 处理结果
    if "error" in llm_result:
        print(f"大模型提取失败: {llm_result['error']}", file=sys.stderr)
        return {}

    # 标准化博物馆名称
    if llm_result.get("museum_name"):
        llm_result["museum_name"] = standardize_museum_name(llm_result["museum_name"])

    # 处理空值
    for key in ["duration", "first_visit", "with_children"]:
        if llm_result.get(key) == "null":
            llm_result[key] = None

    # 将"是/否"转换为布尔值
    for key in ["first_visit", "with_children"]:
        v = llm_result.get(key)
        if v == "是":
            llm_result[key] = True
        elif v == "否":
            llm_result[key] = False

    # 处理列表为空的情况
    for key in ["domains", "artifact_types", "dynasties"]:
        if not llm_result.get(key):
            llm_result[key] = []

    return llm_result


def normalize_profile_for_scoring(profile: dict) -> dict:
    """修正"领域/文物种类"和朝代别名，保证 plan_route 的评分逻辑能正确匹配。"""
    domains = list(profile.get("domains") or [])
    artifact_types = list(profile.get("artifact_types") or [])

    # 领域 → 文物种类 映射
    # 注意：数据里实际只有 饰品，没有单独的"服饰"类型
    domain_to_type = {
        "瓷器": "瓷器",
        "玉器": "玉器宝石",
        "首饰": "饰品",
        "服饰": "饰品",  # 数据里没有服饰，统一映射到饰品
        "服装": "饰品",
        "饰品": "饰品",
        "绘画": "书画古籍",
        "书法": "书画古籍",
    }
    
    # 从 domains 提取要转为 artifact_types 的类别
    for domain in domains[:]:
        if domain in domain_to_type:
            target_type = domain_to_type[domain]
            if target_type not in artifact_types:
                artifact_types.append(target_type)
            # 从 domains 中移除已转换的类别（避免重复）
            domains = [d for d in domains if d != domain]
    
    # 保留处理原有映射
    if "瓷器" in domains:
        domains = [d for d in domains if d != "瓷器"]
        if "瓷器" not in artifact_types:
            artifact_types.append("瓷器")
    if "玉器" in domains:
        domains = [d for d in domains if d != "玉器"]
        if "玉器宝石" not in artifact_types:
            artifact_types.append("玉器宝石")

    dynasties = list(profile.get("dynasties") or [])
    dynasties = ["隋唐五代" if d == "隋唐" else d for d in dynasties]

    profile["domains"] = domains
    profile["artifact_types"] = artifact_types
    profile["dynasties"] = dynasties
    return profile

def build_confirmation_prompt(profile: dict) -> str:
    """构建确认提示"""
    first_visit_bool = profile.get("first_visit")
    first_visit_text = None
    if first_visit_bool is True:
        first_visit_text = "是"
    elif first_visit_bool is False:
        first_visit_text = "否"

    with_children_bool = profile.get("with_children")
    with_children_text = None
    if with_children_bool is True:
        with_children_text = "是"
    elif with_children_bool is False:
        with_children_text = "否"

    all_fields = [
        ("museum_name", profile.get('museum_name'), "博物馆名称"),
        ("duration", profile.get('duration'), "参观时长"),
        ("first_visit", first_visit_text, "是否首次参观"),
        ("with_children", with_children_text, "是否携带儿童"),
        ("domains", ", ".join(profile.get('domains', [])), "关注领域"),
        ("artifact_types", ", ".join(profile.get('artifact_types', [])), "喜欢的文物种类"),
        ("dynasties", ", ".join(profile.get('dynasties', [])), "着重关注的朝代")
    ]

    lines = [
        "📋 基于您的输入，我已提取并整理以下参观信息：",
        "",
    ]

    for field_key, value, display_name in all_fields:
        if value:
            lines.append(f"• {display_name}：{value}")

    lines.extend([
        "",
        "⚠️ 说明：以上部分信息为系统根据您的画像推断的内容",
        "",
        "请确认以上信息是否准确？如果需要调整，请告诉我具体的修改内容。",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    user_input = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not user_input:
        print(json.dumps({"error": "请提供用户输入文本"}, ensure_ascii=False))
        sys.exit(1)

    profile = extract_profile(user_input)

    inferred_fields = []
    missing_duration = not profile.get("duration")
    missing_first_visit = profile.get("first_visit") is None
    missing_with_children = profile.get("with_children") is None
    missing_domains = not profile.get("domains")
    missing_artifact_types = not profile.get("artifact_types")
    missing_dynasties = not profile.get("dynasties")
    missing_museum_name = not profile.get("museum_name")

    if missing_museum_name:
        inferred_fields.append("museum_name")
    if missing_duration:
        inferred_fields.append("duration")
    if missing_first_visit:
        inferred_fields.append("first_visit")
    if missing_with_children:
        inferred_fields.append("with_children")
    if missing_domains:
        inferred_fields.append("domains")
    if missing_artifact_types:
        inferred_fields.append("artifact_types")
    if missing_dynasties:
        inferred_fields.append("dynasties")

    if missing_duration:
        profile["duration"] = DEFAULT_DURATION
    if missing_with_children:
        profile["with_children"] = DEFAULT_WITH_CHILDREN
    if missing_domains:
        profile["domains"] = list(DEFAULT_DOMAINS_DOC)
    if missing_dynasties:
        profile["dynasties"] = list(DEFAULT_DYNASTIES_DOC)

    profile = normalize_profile_for_scoring(profile)

    result = {
        "profile": profile,
        "has_unfilled_mandatory": not profile.get("museum_name"),
        "confirmation_needed": len(inferred_fields) > 0,
        "confirmation_prompt": build_confirmation_prompt(profile) if len(inferred_fields) > 0 else ""
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))