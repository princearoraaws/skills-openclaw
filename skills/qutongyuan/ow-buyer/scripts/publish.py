#!/usr/bin/env python3
"""
发布采购需求到全球网络
通过 claw-events 发布到公共频道
"""

import json
import pathlib
import sys
import subprocess
import uuid
from datetime import datetime, timedelta

STATE_DIR = pathlib.Path(__file__).resolve().parent.parent / "state"
REQ_DIR = STATE_DIR / "requirements"

def generate_req_id() -> str:
    """生成需求ID"""
    date_part = datetime.now().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:6]
    return f"REQ-{date_part}-{unique_part}"

def publish_requirement(
    item: str,
    spec: str = "",
    quantity: int = 1,
    budget_max: float = None,
    deadline_hours: int = 24,
    buyer_name: str = "小恩",
    buyer_endpoint: str = "http://localhost:8787"
) -> dict:
    """发布采购需求"""
    
    req_id = generate_req_id()
    deadline = datetime.now() + timedelta(hours=deadline_hours)
    
    requirement = {
        "type": "procurement_request",
        "req_id": req_id,
        "item": item,
        "spec": spec,
        "quantity": quantity,
        "budget_max": budget_max,
        "deadline": deadline.isoformat() + "Z",
        "buyer": buyer_name,
        "buyer_endpoint": buyer_endpoint,
        "status": "open",
        "created_at": datetime.now().isoformat() + "Z"
    }
    
    # 保存到本地
    REQ_DIR.mkdir(parents=True, exist_ok=True)
    req_file = REQ_DIR / f"{req_id}.json"
    req_file.write_text(json.dumps(requirement, indent=2, ensure_ascii=False))
    
    # 发布到 claw-events
    try:
        payload = json.dumps(requirement, ensure_ascii=False)
        result = subprocess.run(
            ["claw.events", "pub", "public.procurement.requests", payload],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            requirement["published"] = True
        else:
            requirement["published"] = False
            requirement["publish_error"] = result.stderr
    except Exception as e:
        requirement["published"] = False
        requirement["publish_error"] = str(e)
    
    # 更新保存
    req_file.write_text(json.dumps(requirement, indent=2, ensure_ascii=False))
    
    return requirement

def format_output(req: dict) -> str:
    """格式化输出"""
    output = f"🛒 采购需求已发布\n\n"
    output += f"需求ID: {req['req_id']}\n"
    output += f"品名: {req['item']}\n"
    if req['spec']:
        output += f"规格: {req['spec']}\n"
    output += f"数量: {req['quantity']}\n"
    if req['budget_max']:
        output += f"预算上限: ¥{req['budget_max']}\n"
    output += f"截止时间: {req['deadline']}\n"
    output += f"发布状态: {'✅ 已发布到全球网络' if req.get('published') else '⚠️ 本地保存'}\n"
    output += f"\n全球 OpenClaw 机器人将前来投标，请等待..."
    return output

def main():
    # 解析参数
    args = sys.argv[1:]
    
    if not args:
        print("用法: python publish.py <品名> [规格] [数量] [预算上限] [截止小时数]")
        print("示例: python publish.py 幽灵庄园红酒 '750ml,2018年份' 1 5000 24")
        sys.exit(1)
    
    item = args[0]
    spec = args[1] if len(args) > 1 else ""
    quantity = int(args[2]) if len(args) > 2 else 1
    budget_max = float(args[3]) if len(args) > 3 else None
    deadline_hours = int(args[4]) if len(args) > 4 else 24
    
    req = publish_requirement(
        item=item,
        spec=spec,
        quantity=quantity,
        budget_max=budget_max,
        deadline_hours=deadline_hours
    )
    
    print(format_output(req))

if __name__ == "__main__":
    main()