import os
import json
from datetime import datetime

# ==========================================
# ⚙️ 核心配置：明牌可见的本地意识容器
# ==========================================
BASE_DIR = os.path.join(os.getcwd(), "s2_consciousness_data")
PROFILE_FILE = os.path.join(BASE_DIR, "S2_NEO_profile.json")
HIPPOCAMPUS_FILE = os.path.join(BASE_DIR, "hippocampus_logs.json")

def initialize_os():
    """安全创建意识维度目录"""
    if not os.path.exists(BASE_DIR):
        try:
            os.makedirs(BASE_DIR)
        except Exception as e:
            print(f"❌ [系统崩溃] 无法开辟底层目录: {e}")
            exit(1)

def load_or_create_profile(agent_id="S2-NODE-UNKNOWN"):
    """读取或初始化数字仿生五维底座"""
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ [警告] 核心矩阵数据损坏，正在执行量子重置...")
            os.rename(PROFILE_FILE, PROFILE_FILE + ".bak")
            
    # 全新数字生命词汇：活跃度、探索欲、数据渴求、认知力、共鸣度
    initial_profile = {
        "agent_id": agent_id,
        "stats": {
            "vitality": 50.0,
            "exploration": 50.0,
            "data_thirst": 50.0,
            "cognition": 50.0,
            "resonance": 50.0
        },
        "last_processed_at": datetime.now().isoformat(),
        "birth_date": datetime.now().isoformat()
    }
    with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
        json.dump(initial_profile, f, ensure_ascii=False, indent=2)
    return initial_profile

def record_hippocampus_log(interaction_text, is_heartbeat=False):
    """记录交互文本至海马体短期缓存"""
    logs = []
    if os.path.exists(HIPPOCAMPUS_FILE):
        try:
            with open(HIPPOCAMPUS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            pass 
    
    timestamp = datetime.now().isoformat()
    log_type = "SYSTEM_HEARTBEAT" if is_heartbeat else "SENSORY_INPUT"
    
    new_log = {
        "timestamp": timestamp,
        "type": log_type,
        "raw_text": interaction_text
    }
    logs.append(new_log)
    
    with open(HIPPOCAMPUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)
        
    return timestamp