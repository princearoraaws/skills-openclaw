import random
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

from trump_monitor import TrumpMonitor

class TrumpUnreliableModel:
    """川普不靠谱模型 (Unreliable Model v1.0)"""
    
    def __init__(self):
        self.unreliable_keywords = [
            'huge', 'believe me', 'tremendous', 'disaster', 'fake news', 
            'winning', 'sad', 'wall', 'again', 'very soon', 'perfect'
        ]

    def predict(self, news_item):
        text = news_item['title'] + " " + news_item['summary']
        
        # 核心算法：词频统计 + 情感分析
        score = 50 # 初始分值（满分 100）
        
        # 1. 关键词命中（中得越多，不靠谱度越高/变动越大）
        hit_count = 0
        for kw in self.unreliable_keywords:
            if kw.lower() in text.lower():
                hit_count += 1
                score += 5 
        
        # 2. 情感极端性检测
        if TextBlob:
            blob = TextBlob(text)
            sentiment_mag = abs(blob.sentiment.polarity)
            score += sentiment_mag * 20 # 情感越极端，分值越高
            
        # 3. 随机波动因子
        chaos_factor = random.randint(-15, 15)
        
        # 计算不靠谱指数 (0-100)
        unreliability_index = min(max(score + chaos_factor, 0), 100)
        
        # 预测执行概率与市场冲击
        exec_prob = 100 - unreliability_index
        if unreliability_index > 75:
            impact = {"zh": "🔥 全球关注", "en": "🔥 Global Attention (High Alert)"}
        else:
            impact = {"zh": "⚖️ 常规变动", "en": "⚖️ Routine Fluctuations"}
        
        return {
            'index': unreliability_index,
            'exec_prob': f"{exec_prob:.1f}%",
            'impact': impact,
            'comment': self.get_comment(unreliability_index)
        }

    def get_comment(self, index):
        if index > 85: 
            return {
                'zh': "极度不靠谱：基本就是随口一说，别太当真。",
                'en': "Extremely Unreliable: Likely just off-the-cuff remarks, don't take it too seriously."
            }
        if index > 60: 
            return {
                'zh': "中度不靠谱：逻辑极其跳跃，存在反转可能。",
                'en': "Moderately Unreliable: Wild logical leaps, high possibility of reversal."
            }
        if index > 30: 
            return {
                'zh': "中规中矩：看起来像是个认真写的推特/言论。",
                'en': "Standard: Seems like a carefully drafted tweet or statement."
            }
        return {
            'zh': "异常严肃：他这次可能是说真的，建议立刻介入。",
            'en': "Dead Serious: He might actually mean it this time. Action recommended."
        }

def run_demo():
    print("==================================================")
    print("🇺🇸 川普不靠谱模型 / Trump Unreliable Model (v1.0)")
    print("==================================================")
    
    # 模拟最新捕捉到的动态 (由于 RSS 可能受限，这里载入最新的热点)
    mock_news = [
        {
            'title': "Trump takes executive action to pay TSA workers, blames 'Democrat Chaos'",
            'summary': "Donald Trump announced executive action to pay 50,000 airport security workers due to a stalled deal in Congress.",
            'published': "2026-03-27"
        },
        {
            'title': "Trump extends Iran deadline to April 6, says talks are 'going very well'",
            'summary': "Trump extended the deadline for Iran to open the Strait of Hormuz, claiming the US has 'already won' in a certain sense.",
            'published': "2026-03-27"
        },
        {
            'title': "US Treasury to put Trump's signature on new paper currency",
            'summary': "The US Treasury plans to put Donald Trump's signature on new paper currency, a first for a sitting president.",
            'published': "2026-03-26"
        }
    ]

    print(f"[*] 已捕获到 {len(mock_news)} 条最新动态，正在进行预测分析...")
    print(f"[*] Captured {len(mock_news)} updates, running predictive analysis...\n")
    
    model = TrumpUnreliableModel()
    for i, item in enumerate(mock_news):
        pred = model.predict(item)
        print(f"📊 动态 {i+1} / Update {i+1}:")
        print(f"   📢 Title: {item['title'][:60]}...")
        # 简单模拟翻译展示
        print(f"   ├─ 不靠谱指数 / Unreliability: {pred['index']:.1f}")
        print(f"   ├─ 预期执行率 / Exec Probability: {pred['exec_prob']}")
        
        print(f"   ├─ 市场冲击力 / Market Impact: {pred['impact']['zh']} ({pred['impact']['en']})")
        
        print(f"   └─ 模型点评 / AI Comment:")
        print(f"      [CN]: {pred['comment']['zh']}")
        print(f"      [EN]: {pred['comment']['en']}")
        print("-" * 60)

if __name__ == "__main__":
    import sys
    # 强制输出为 UTF-8
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    run_demo()
