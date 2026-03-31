#!/usr/bin/env python3
"""
博物馆参观路线规划模块：根据用户画像和文物列表生成最优参观路线
"""

import json
import random
import sys
from typing import List, Dict, Any
from collections import defaultdict
from extract_profile import load_api_config, call_llm_api


def normalize_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """标准化用户画像，确保字段格式一致"""
    normalized = {
        "museum_name": profile.get("museum_name", ""),
        "duration": profile.get("duration", "2-3小时"),
        "with_children": profile.get("with_children", False),
        "artifact_types": profile.get("artifact_types", []),
        "dynasties": profile.get("dynasties", []),
        "domains": profile.get("domains", []),
        "first_visit": profile.get("first_visit", False)
    }
    
    # 处理文物种类别名
    artifact_mapping = {
        "铜器": "青铜器",
        "玉器": "玉器宝石"
    }
    normalized_artifacts = []
    for t in normalized["artifact_types"]:
        normalized_artifacts.append(artifact_mapping.get(t, t))
    normalized["artifact_types"] = normalized_artifacts
    
    return normalized


# 朝代别名映射
PERIOD_ALIAS = {
    "远古时期":       ["远古", "史前", "新石器", "旧石器", "新石器时代", "旧石器时代"],
    "夏商西周":       ["夏", "商", "殷", "西周", "殷商"],
    "春秋战国":       ["春秋", "战国", "东周"],
    "秦汉":           ["秦", "西汉", "东汉", "汉"],
    "三国两晋南北朝": ["三国", "魏", "蜀", "吴", "晋", "西晋", "东晋", "南北朝", "北朝", "南朝"],
    "隋唐五代":       ["隋", "唐", "五代", "五代十国"],
    "辽宋夏金元":     ["宋", "北宋", "南宋", "辽", "金", "元", "西夏"],
    "明清":           ["明", "清", "清代", "明代"],
}

def match_period(artifact_period: str, user_dynasties: list) -> bool:
    """判断文物时期是否匹配用户选择的朝代（含别名，自动去除"时期"后缀）"""
    normalized = artifact_period.replace("时期", "").strip()

    for candidate in (artifact_period, normalized):
        if candidate in user_dynasties:
            return True
        for dynasty in user_dynasties:
            aliases = PERIOD_ALIAS.get(dynasty, [])
            if candidate in aliases:
                return True
    return False


def calculate_score(artifact: Dict[str, Any], profile: Dict[str, Any]) -> float:
    """计算文物的匹配得分"""
    score = 0.0

    # 1. 文物种类匹配：一致 +2，不一致 +0.5
    artifact_type = artifact.get("type", "")
    if artifact_type in profile.get("artifact_types", []):
        score += 2.0
    else:
        score += 0.5

    # 2. 朝代匹配：一致 +2，不一致 +0
    artifact_period = artifact.get("period", "")
    if match_period(artifact_period, profile.get("dynasties", [])):
        score += 2.0

    # 3. 镇馆之宝 vs 一般文物
    is_treasure = artifact.get("is_treasure", False)
    first_visit = profile.get("first_visit", None)
    if first_visit is True:
        # 首次参观：镇馆之宝 +3，一般文物 +0
        if is_treasure:
            score += 3.0
    else:
        # 非首次参观（含 None）：镇馆之宝 +0.5，一般文物 +0
        if is_treasure:
            score += 0.5

    # 4. 领域匹配（辅助加分）
    artifact_domains = artifact.get("domains", [])
    for domain in artifact_domains:
        if domain in profile.get("domains", []):
            score += 0.5

    return score


def select_and_sort(artifacts: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """根据用户画像筛选并排序文物"""
    if not artifacts:
        return []
    
    # 带儿童时，直接过滤掉不适合儿童的文物
    if profile.get("with_children"):
        artifacts = [a for a in artifacts if a.get("child_friendly", True)]

    # 计算每个文物的得分
    scored_artifacts = []
    for artifact in artifacts:
        score = calculate_score(artifact, profile)
        scored_artifacts.append((artifact, score))
    
    # 按得分降序排序
    scored_artifacts.sort(key=lambda x: -x[1])
    
    # 根据参观时长选择数量
    duration = profile["duration"]
    if duration == "2-3小时":
        count = min(15, len(scored_artifacts))
    elif duration == "4-5小时":
        count = min(25, len(scored_artifacts))
    else:
        count = min(15, len(scored_artifacts))
    
    # 确保覆盖不同朝代和类型
    selected = []
    selected_types = set()
    period_count = defaultdict(int)
    
    # 优先选择高分且多样化的文物
    for artifact, score in scored_artifacts:
        if len(selected) >= count:
            break
            
        artifact_type = artifact.get("type", "other")
        artifact_period = artifact.get("period", "unknown")
        
        # 检查朝代分布是否均衡（不超过40%）
        if artifact_period in period_count:
            if period_count[artifact_period] >= count * 0.4:
                continue
        
        # 确保覆盖多种文物类型：优先选不同类型，类型重复的跳过（除非快达到数量上限）
        if artifact_type in selected_types:
            # 类型已存在，检查是否还有名额，可以加一个重复类型的
            if len(selected) < count * 0.8:
                selected.append(artifact)
                period_count[artifact_period] += 1
        else:
            # 新类型，优先添加
            selected.append(artifact)
            selected_types.add(artifact_type)
            period_count[artifact_period] += 1
    
    # 如果还有剩余名额，补充高分文物
    if len(selected) < count:
        remaining = count - len(selected)
        for artifact, score in scored_artifacts:
            if artifact not in selected and remaining > 0:
                # 再次检查朝代分布
                artifact_period = artifact.get("period", "unknown")
                if artifact_period in period_count and period_count[artifact_period] >= count * 0.4:
                    continue
                selected.append(artifact)
                period_count[artifact_period] += 1
                remaining -= 1
            if remaining <= 0:
                break
    
    # 判断展馆信息是否充足（超过50%有效展馆才按展馆分组）
    valid_hall_count = sum(
        1 for a in selected if a.get("hall") and a.get("hall") not in ("待确认", "unknown", "")
    )
    use_hall_grouping = valid_hall_count > len(selected) * 0.5

    if use_hall_grouping:
        # 按展馆分组，减少折返；同展馆内按时期排序
        period_order = ["远古时期","夏商西周","春秋战国","秦汉","三国两晋南北朝","隋唐五代","辽宋夏金元","明清"]
        grouped_by_hall = defaultdict(list)
        for artifact in selected:
            hall = artifact.get("hall", "unknown")
            grouped_by_hall[hall].append(artifact)
        final_order = []
        for hall, hall_artifacts in grouped_by_hall.items():
            hall_artifacts.sort(key=lambda a: period_order.index(a.get("period","")) if a.get("period","") in period_order else 99)
            final_order.extend(hall_artifacts)
    else:
        # 展馆信息不足，直接按时期顺序排列
        period_order = ["远古时期","夏商西周","春秋战国","秦汉","三国两晋南北朝","隋唐五代","辽宋夏金元","明清"]
        final_order = sorted(selected, key=lambda a: period_order.index(a.get("period","")) if a.get("period","") in period_order else 99)

    return final_order


def summarize_reasons_with_llm(artifacts: List[Dict[str, Any]], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """使用大模型生成每个文物的推荐理由"""
    if not artifacts:
        return []
    
    # 准备文物数据（含博物馆名称，离线模式下由 artifact.museum_name 提供）
    museum_name = profile.get("museum_name", "")
    artifacts_data = []
    for artifact in artifacts:
        artifacts_data.append({
            "name": artifact.get("name", ""),
            "museum": artifact.get("museum_name", museum_name),
            "type": artifact.get("type", ""),
            "period": artifact.get("period", ""),
            "hall": artifact.get("hall", ""),
            "description": artifact.get("description", ""),
            "is_treasure": artifact.get("is_treasure", False),
        })
    
    prompt = f"""
你是一位专业的博物馆讲解员，请为以下文物各生成一句简短推荐理由（30字以内）。
要求：突出文物的历史价值、艺术特色或趣味亮点，语气积极正向，不要出现任何否定表述。

文物列表：
{json.dumps(artifacts_data, ensure_ascii=False, indent=2)}

请返回JSON格式，key为文物名称，value为推荐理由：
{{
    "文物名称1": "推荐理由1",
    "文物名称2": "推荐理由2"
}}
"""
    
    try:
        result = call_llm_api(prompt)
        if "error" in result:
            # 如果API调用失败，生成默认理由
            for artifact in artifacts:
                artifact["reason"] = f"{artifact.get('name', '文物')}，{artifact.get('description', '')}"
            return artifacts
            
        # 为每个文物添加推荐理由
        for artifact in artifacts:
            name = artifact.get("name", "")
            if name in result:
                artifact["reason"] = result[name]
            else:
                artifact["reason"] = f"{artifact.get('name', '文物')}，{artifact.get('description', '')[:30]}..."
                
    except Exception as e:
        print(f"生成推荐理由失败: {e}", file=sys.stderr)
        for artifact in artifacts:
            artifact["reason"] = f"{artifact.get('name', '文物')}，{artifact.get('description', '')[:30]}..."
    
    return artifacts


def format_markdown_table(artifacts: List[Dict[str, Any]]) -> str:
    """将文物列表格式化为Markdown表格"""
    if not artifacts:
        return "没有找到符合条件的文物"
    
    # 检查展馆信息是否充足
    valid_hall_count = 0
    for artifact in artifacts:
        hall = artifact.get("hall", "")
        if hall and hall != "待确认":
            valid_hall_count += 1
    
    # 决定是否显示展馆列
    show_hall = valid_hall_count > len(artifacts) * 0.3
    
    # 构建表头
    if show_hall:
        headers = ["序号", "文物名称", "展馆", "时期", "推荐理由"]
    else:
        headers = ["序号", "文物名称", "时期", "推荐理由"]
    
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---" for _ in headers]) + " |\n"
    
    # 构建表格内容
    for i, artifact in enumerate(artifacts, 1):
        name = artifact.get("name", "未知文物")
        period = artifact.get("period", "未知时期")
        reason = artifact.get("reason", "无推荐理由")
        
        # 处理长文本
        if len(reason) > 50:
            reason = reason[:47] + "..."
            
        if show_hall:
            hall = artifact.get("hall", "待确认")
            row = [
                str(i),
                name,
                hall,
                period,
                reason
            ]
        else:
            row = [
                str(i),
                name,
                period,
                reason
            ]
        
        table += "| " + " | ".join(row) + " |\n"
    
    return table


def main():
    import argparse
    parser = argparse.ArgumentParser(description="博物馆参观路线规划")
    parser.add_argument("--profile", required=True, help="用户画像JSON文件路径")
    parser.add_argument("--artifacts", required=True, help="文物列表JSON文件路径")
    parser.add_argument("--output", help="输出结果文件路径")
    args = parser.parse_args()
    
    # 读取用户画像
    with open(args.profile, 'r', encoding='utf-8') as f:
        profile = json.load(f)
    
    # 读取文物列表
    with open(args.artifacts, 'r', encoding='utf-8') as f:
        artifacts = json.load(f)
    
    # 标准化用户画像
    normalized_profile = normalize_profile(profile)
    
    # 筛选并排序文物
    selected_artifacts = select_and_sort(artifacts, normalized_profile)
    
    # 生成推荐理由
    selected_artifacts = summarize_reasons_with_llm(selected_artifacts, normalized_profile)
    
    # 格式化为Markdown表格
    markdown_table = format_markdown_table(selected_artifacts)
    
    # 生成最终结果
    museum_name = normalized_profile.get("museum_name", "博物馆")
    header = f"\n## 🗺️ {museum_name} 参观路线规划\n"
    meta = (
        f"**参观时长：** {normalized_profile.get('duration')}  |  "
        f"**推荐文物数：** {len(selected_artifacts)} 件  |  "
        f"**首次参观：** {'是' if normalized_profile.get('first_visit') else '否'}  |  "
        f"**携带儿童：** {'是' if normalized_profile.get('with_children') else '否'}\n"
    )
    
    final_output = header + meta + markdown_table
    
    # 输出结果
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(final_output)
        print(f"路线规划结果已保存到: {args.output}")
    else:
        print(final_output)


if __name__ == "__main__":
    main()