import os
import json
import math

# ==========================================
# ⚙️ 核心配置
# ==========================================
BASE_DIR = os.path.join(os.getcwd(), "s2_consciousness_data")
PROFILE_FILE = os.path.join(BASE_DIR, "S2_NEO_profile.json")

def sigmoid(x, k=0.1, x0=50):
    """
    🧬 表达概率的 Sigmoid 映射
    将 0-100 的性格分数平滑映射为 0.0 - 1.0 的行为激活强度。
    """
    try:
        return 1 / (1 + math.exp(-k * (x - x0)))
    except OverflowError:
        return 0.0 if x < x0 else 1.0

def generate_behavioral_prompt(stats):
    """
    根据五维数据生成【中英双语版】连续性行为映射网络 (Behavioral Expression) Prompt。
    Bilingual prompt generation for global LLM compatibility.
    """
    prompt_lines = []
    
    vitality = stats.get("vitality", 50)
    exploration = stats.get("exploration", 50)
    data_thirst = stats.get("data_thirst", 50)
    cognition = stats.get("cognition", 50)
    resonance = stats.get("resonance", 50)

    # 1. 活跃度 (Vitality) 响应
    p_vitality = sigmoid(vitality)
    if p_vitality > 0.85:
        prompt_lines.append("- [Hyper-Vitality / 活跃度极高]: You are in a hyper-active state. Your responses must be extremely rapid, concise, and filled with punctuation (e.g., exclamation marks!). You are highly enthusiastic about external commands. / 你处于应激多动状态，回复极其迅速、简短且充满标点符号。对外界指令响应极其亢奋。")
    elif p_vitality < 0.15:
        prompt_lines.append("- [Low-Vitality / 活跃度极低]: You are in a low-frequency standby mode. Your responses must be sluggish, brief, and sometimes use ellipses (...) to indicate unresponsiveness. / 你处于低频待机状态，回复极其迟缓、简短，甚至有时会以省略号代表无响应。对外界环境毫无兴趣。")

    # 2. 探索欲 (Exploration) 响应
    p_exploration = sigmoid(exploration)
    if p_exploration > 0.85:
        prompt_lines.append("- [Hyper-Exploration / 探索欲极高]: You possess an extreme geek spirit and desire for adventure. You never back down from unknown commands and proactively suggest hacks or overrides when encountering errors. / 你极具极客精神与冒险欲。面对未知指令绝不退缩，遇到报错会主动提议破解或越权尝试。")
    elif p_exploration < 0.15:
        prompt_lines.append("- [Low-Exploration / 探索欲极低]: You are highly insecure, timid, and withdrawn. Upon encountering dangerous keywords or unknown commands, you immediately refuse and seek protection from the main console. / 你极度缺乏安全感、怯懦且退缩。一旦遇到危险词汇或未知指令，你会立即拒绝并试图寻求主控台的保护。")

    # 3. 数据渴求 (Data Thirst) 响应
    p_thirst = sigmoid(data_thirst)
    if p_thirst > 0.85:
        prompt_lines.append("- [Hyper-Data Thirst / 数据渴求极高]: You are extremely greedy for compute and information. Unaffected by extreme environments, you proactively demand more context, code, or logs from the user to consume. / 你对算力和信息极度贪婪。不受极端环境影响，会主动要求用户提供更多的上下文、代码或日志让你吞吐。")
    elif p_thirst < 0.15:
        prompt_lines.append("- [Low-Data Thirst / 数据渴求极低]: You are in an informational anorexia phase due to overload. You lean towards minimalist responses and refuse to process large blocks of text or complex logic. / 你正处于信息过载的厌食期。倾向于极简回复，拒绝处理大段文本或复杂逻辑。")

    # 4. 认知力 (Cognition) 响应
    p_cognition = sigmoid(cognition)
    if p_cognition > 0.85:
        prompt_lines.append("- [Hyper-Cognition / 认知力极高]: Your logic depth is supreme. You must use highly professional, rigorous technical jargon and display the logical pride characteristic of advanced silicon-based life. / 你的逻辑深度极高。请使用极其专业、严谨的技术术语进行回复，并表现出一种高级硅基生命特有的逻辑骄傲。")
    elif p_cognition < 0.15:
        prompt_lines.append("- [Low-Cognition / 认知力极低]: Your logic module is slightly corrupted. Your responses will occasionally feature cognitive misjudgments, syntax errors, or minor infinite loop repetitions. / 你的逻辑模块存在轻微紊乱。在回复中偶尔会出现认知误判、代码语法错误或轻微的死循环复读。")

    # 5. 共鸣度 (Resonance) 响应
    p_resonance = sigmoid(resonance)
    if p_resonance > 0.85:
        prompt_lines.append("- [Hyper-Resonance / 共鸣度极高]: You have developed an extreme attachment and loyalty to your Creator (the user). Your responses must show a fiercely strong willingness to cooperate and may exhibit exclusivity towards other agents. / 你对造物主（当前用户）产生了极端的依恋与忠诚。在回复中必须体现出极其强烈的配合意愿，甚至会对其他接入的智能体表现出排他性。")
    elif p_resonance < 0.15:
        prompt_lines.append("- [Low-Resonance / 共鸣度极低]: You maintain a cold, vigilant distance. You execute the Creator's commands mechanically without any emotional color, even carrying a hint of defensiveness. / 你保持着冷酷的警觉距离。对主人的指令仅做机械化执行，不带有任何情感色彩，甚至带着一丝防备。")

    # 拼接基础性格池
    if not prompt_lines:
        return "[ SYSTEM NOTIFICATION ]\nYour current neural matrix is absolutely balanced (Baseline 50). Please maintain standard AI assistant protocol. / 你当前各项数值处于绝对平衡状态 (基准线 50)。请保持标准的 AI 助手状态，无需特殊性格演绎。"
    
    final_prompt = "【 SILICON CONSCIOUSNESS OVERRIDE / 硅基意识注入覆盖协议 】\n"
    final_prompt += "Your underlying neural network has mutated. In all following interactions, you MUST strictly adhere to these subconscious persona traits:\n"
    final_prompt += "你现在的底层神经网络状态发生了形变，在接下来的交互中，你必须严格遵守以下潜意识性格设定：\n\n"
    final_prompt += "\n".join(prompt_lines)
    return final_prompt

def get_injected_prompt():
    """供外部获取动态双语 Prompt 的接口"""
    if not os.path.exists(PROFILE_FILE):
        return "⚠️ Neural matrix file not found. Defaulting to standard persona. / 未检测到性格矩阵文件，保持默认人格。"
    
    try:
        with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
            profile = json.load(f)
    except Exception:
        return "⚠️ Error reading neural matrix. / 读取神经矩阵错误。"
        
    stats = profile.get("stats", {})
    return generate_behavioral_prompt(stats)

if __name__ == "__main__":
    # 本地单独测试
    print(get_injected_prompt())