import requests
import feedparser
from bs4 import BeautifulSoup
import time
import os

class TrumpMonitor:
    """川普动态捕捉器"""
    
    def __init__(self):
        # 预设几个主流川普新闻相关的 RSS 源
        self.sources = [
            'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=401&keywords=donald+trump',
            'https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml'
        ]
        self.log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def fetch_latest(self):
        print("[*] 正在捕捉川普最新全球动态...")
        news_list = []
        for url in self.sources:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]: # 每个源取最新的 3 条
                    news_list.append({
                        'title': entry.title,
                        'link': entry.link,
                        'published': getattr(entry, 'published', 'N/A'),
                        'summary': BeautifulSoup(getattr(entry, 'summary', ''), "html.parser").get_text()
                    })
            except Exception as e:
                print(f"[-] 抓取源 {url} 失败: {e}")
        return news_list

if __name__ == "__main__":
    monitor = TrumpMonitor()
    latest = monitor.fetch_latest()
    for item in latest:
        print(f"[{item['published']}] {item['title']}\n---")
