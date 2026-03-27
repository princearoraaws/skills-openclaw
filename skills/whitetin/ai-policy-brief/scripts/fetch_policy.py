#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI政策爬虫脚本 - fetch_policy.py
用途：爬取国内各政府官网和权威媒体的AI相关政策，输出JSON供AI分析
依赖：pip install requests beautifulsoup4 lxml python-dateutil
用法：python fetch_policy.py --days 30 --keywords 人工智能 AI 大模型
"""

import argparse
import json
import re
import sys
import time
import random
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
    from dateutil import parser as dateparser
except ImportError as e:
    print(json.dumps({
        "error": f"缺少依赖库: {e}。请运行: pip install requests beautifulsoup4 lxml python-dateutil",
        "results": []
    }, ensure_ascii=False), file=sys.stdout)
    sys.exit(1)

# 只输出错误到stderr，不污染stdout的JSON
logging.basicConfig(stream=sys.stderr, level=logging.WARNING,
                    format='[%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("policy_crawler")

# ─────────────────────────────────────────────
# 通用请求配置
# ─────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
]

REQUEST_TIMEOUT = 15
MAX_RETRIES = 2


def get_headers(referer=None):
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }
    if referer:
        headers["Referer"] = referer
    return headers


def fetch_html(url, retries=MAX_RETRIES, sleep_range=(0.5, 1.5), verify_ssl=True):
    """获取页面HTML，带重试、随机延迟和SSL错误处理"""
    import urllib3
    
    # 禁用SSL验证时，抑制警告
    if not verify_ssl:
        urllib3.disable_warnings()
    
    for attempt in range(retries + 1):
        try:
            time.sleep(random.uniform(*sleep_range))
            resp = requests.get(
                url,
                headers=get_headers(referer=url),
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
                verify=verify_ssl
            )
            resp.encoding = resp.apparent_encoding or 'utf-8'
            if resp.status_code == 200:
                return resp.text
            else:
                logger.warning(f"HTTP {resp.status_code}: {url}")
        except requests.exceptions.SSLError as e:
            logger.warning(f"SSL错误 (第{attempt+1}次): {url} -> {e}")
            if attempt == retries:
                # 最后一次尝试，禁用SSL验证
                try:
                    urllib3.disable_warnings()
                    logger.info(f"尝试禁用SSL验证: {url}")
                    resp = requests.get(
                        url,
                        headers=get_headers(referer=url),
                        timeout=REQUEST_TIMEOUT,
                        allow_redirects=True,
                        verify=False
                    )
                    resp.encoding = resp.apparent_encoding or 'utf-8'
                    if resp.status_code == 200:
                        logger.info(f"禁用SSL验证后成功: {url}")
                        return resp.text
                except Exception as e2:
                    logger.error(f"禁用SSL验证后仍失败: {url} -> {e2}")
        except requests.exceptions.Timeout as e:
            logger.warning(f"连接超时 (第{attempt+1}次): {url} -> {e}")
        except requests.exceptions.ConnectionError as e:
            logger.warning(f"连接错误 (第{attempt+1}次): {url} -> {e}")
        except Exception as e:
            logger.warning(f"请求失败 (第{attempt+1}次): {url} -> {e}")
    return None


# ─────────────────────────────────────────────
# 日期解析工具
# ─────────────────────────────────────────────
CN_DATE_PATTERN = re.compile(
    r'(\d{4})[年\-/.](\d{1,2})[月\-/.](\d{1,2})[日]?'
)


def parse_date(text):
    """解析中文/英文日期，返回 datetime 对象，失败返回 None"""
    if not text:
        return None
    text = text.strip()
    # 中文日期格式
    m = CN_DATE_PATTERN.search(text)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except Exception:
            pass
    # dateutil 通用解析
    try:
        return dateparser.parse(text, fuzzy=True)
    except Exception:
        return None


def is_within_days(date_obj, days):
    """判断日期是否在最近N天内"""
    if date_obj is None:
        return True  # 无法判断时保留
    cutoff = datetime.now() - timedelta(days=days)
    return date_obj >= cutoff


# ─────────────────────────────────────────────
# 关键词过滤
# ─────────────────────────────────────────────
def matches_keywords(text, keywords):
    """判断文本是否包含任意关键词"""
    if not keywords:
        return True
    text_lower = text.lower()
    for kw in keywords:
        if kw.lower() in text_lower:
            return True
    return False


# ─────────────────────────────────────────────
# 通用列表页解析器（适合大多数政府网站）
# ─────────────────────────────────────────────
def parse_generic_list(html, base_url, source_name, source_type):
    """通用解析器：提取列表页中的标题、链接、日期"""
    if not html:
        return []
    soup = BeautifulSoup(html, 'lxml')
    items = []

    # 尝试多种常见列表结构
    selectors = [
        ('ul.list li', 'a', '.date, .time, span[class*="date"], span[class*="time"]'),
        ('ul.news-list li', 'a', 'span'),
        ('div.list-body li', 'a', 'span'),
        ('div.news-list li', 'a', 'span'),
        ('table.list tr', 'a', 'td:last-child'),
        ('div.zwgk-list li', 'a', 'span'),
        ('ul li', 'a', 'span'),
    ]

    for list_sel, link_sel, date_sel in selectors:
        rows = soup.select(list_sel)
        if len(rows) < 3:
            continue
        for row in rows:
            link_el = row.select_one(link_sel)
            if not link_el:
                continue
            title = link_el.get_text(strip=True)
            href = link_el.get('href', '')
            if not title or not href or len(title) < 5:
                continue
            url = urljoin(base_url, href)
            # 日期
            date_el = row.select_one(date_sel) if date_sel else None
            date_text = date_el.get_text(strip=True) if date_el else ''
            # 备用：从整行文本提取日期
            if not date_text:
                row_text = row.get_text()
                m = CN_DATE_PATTERN.search(row_text)
                date_text = m.group(0) if m else ''
            items.append({
                'title': title,
                'url': url,
                'date_text': date_text,
                'source': source_name,
                'source_type': source_type,
            })
        if items:
            break

    # 最后兜底：找所有带日期特征的 <a> 标签
    if not items:
        for a in soup.find_all('a', href=True):
            title = a.get_text(strip=True)
            if len(title) < 8:
                continue
            parent = a.parent
            parent_text = parent.get_text() if parent else ''
            m = CN_DATE_PATTERN.search(parent_text)
            date_text = m.group(0) if m else ''
            href = a.get('href', '')
            url = urljoin(base_url, href)
            domain = urlparse(base_url).netloc
            if domain not in url:
                continue
            items.append({
                'title': title,
                'url': url,
                'date_text': date_text,
                'source': source_name,
                'source_type': source_type,
            })

    return items


# ─────────────────────────────────────────────
# 各站点专用爬虫函数
# ─────────────────────────────────────────────

def crawl_guowuyuan(days, keywords):
    """国务院政策文件"""
    source = "国务院"
    urls = [
        "https://www.gov.cn/",
        "https://www.gov.cn/zhengce/zuixin/",
    ]
    results = []
    for url in urls:
        html = fetch_html(url)
        items = parse_generic_list(html, url, source, "central")
        results.extend(items)
    return results


def crawl_cac(days, keywords):
    """网信办政策法规"""
    source = "网信办"
    urls = [
        
        "https://www.cac.gov.cn/",
    ]
    results = []
    for url in urls:
        html = fetch_html(url)
        items = parse_generic_list(html, url, source, "central")
        results.extend(items)
    return results


def crawl_miit(days, keywords):
    """工信部政策文件"""
    source = "工信部"
    urls = [
        "https://www.miit.gov.cn/",
        "https://www.miit.gov.cn/zwgk/zcwj/wjfb/index.html",
    ]
    results = []
    for url in urls:
        html = fetch_html(url)
        items = parse_generic_list(html, url, source, "central")
        results.extend(items)
    return results


def crawl_most(days, keywords):
    """科技部政策法规"""
    source = "科技部"
    urls = [
        "https://www.most.gov.cn/index.html",
        "https://www.most.gov.cn/satp/",
    ]
    results = []
    for url in urls:
        html = fetch_html(url)
        items = parse_generic_list(html, url, source, "central")
        results.extend(items)
    return results


def crawl_ndrc(days, keywords):
    """发改委政策文件"""
    source = "发改委"
    url = "https://www.ndrc.gov.cn/xxgk/zcfb/"
    html = fetch_html(url)
    return parse_generic_list(html, url, source, "central")


def crawl_gd(days, keywords):
    """广东省人民政府"""
    source = "广东省"
    results = []
    for url in [
        "http://www.gd.gov.cn/zwgk/wjk/index.html",     # 文件库
        "http://www.gd.gov.cn/zwgk/gsgg/index.html",    # 公示公告
    ]:
        html = fetch_html(url)
        results.extend(parse_generic_list(html, url, source, "guangdong"))
    return results


def crawl_gz(days, keywords):
    """广州市人民政府"""
    source = "广州市"
    results = []
    for url in [
        "https://www.gz.gov.cn/gzzcwjk/index.html",        # 政策文件库
        "https://www.gz.gov.cn/zwgk/fggw/index.html",      # 法规公文
        "https://www.gz.gov.cn/zwgk/zcjd/index.html",      # 政策解读
    ]:
        html = fetch_html(url)
        results.extend(parse_generic_list(html, url, source, "guangdong"))
    return results


def crawl_sz(days, keywords):
    """深圳市人民政府"""
    source = "深圳市"
    results = []
    # 使用深圳市政府的其他可用页面
    urls = [
        "https://www.sz.gov.cn/zcjd/index.html",   # 政策解读（https）
    ]
    for url in urls:
        html = fetch_html(url, verify_ssl=False)
        results.extend(parse_generic_list(html, url, source, "guangdong"))
    return results


def crawl_foshan(days, keywords):
    """佛山市人民政府"""
    source = "佛山市"
    results = []
    for url in [
        "https://www.foshan.gov.cn/zwgk/zcwj/zcjd/bmjd/",   # 政策解读
        "https://www.foshan.gov.cn/zwgk/zwdt/bmdt/",         # 政策解读
        "https://www.foshan.gov.cn/gfxwj/szfgfxwj/",         # 规范性文件
        "https://www.foshan.gov.cn/zwgk/zwdt/jryw/",          # 今日要闻
    ]:
        html = fetch_html(url, verify_ssl=False)
        results.extend(parse_generic_list(html, url, source, "guangdong"))
    return results


def crawl_dongguan(days, keywords):
    """东莞市人民政府"""
    source = "东莞市"
    results = []
    for url in [
        "http://www.dg.gov.cn/zwgk/zfgb/zfgb/index.html",   # 政府公报
        "http://www.dg.gov.cn/jjdz/zwgg/index.html",          # 政务公告
        "http://www.dg.gov.cn/zdlyxxgk/index.html",           # 重点领域信息
    ]:
        html = fetch_html(url)
        results.extend(parse_generic_list(html, url, source, "guangdong"))
    return results


def crawl_thepaper(days, keywords):
    """澎湃新闻"""
    source = "澎湃新闻"
    urls = [
        "https://www.thepaper.cn/",
        "https://www.thepaper.cn/channel_121666",  # 科技频道
    ]
    results = []
    for url in urls:
        html = fetch_html(url)
        items = parse_generic_list(html, url, source, "media")
        results.extend(items)
    return results


def crawl_sina(days, keywords):
    """新浪新闻科技频道"""
    source = "新浪新闻"
    urls = [
        "https://tech.sina.com.cn/news/",  # 科技新闻列表
    ]
    results = []
    for url in urls:
        html = fetch_html(url)
        items = parse_generic_list(html, "https://tech.sina.com.cn", source, "media")
        results.extend(items)
    return results


def crawl_ifeng(days, keywords):
    """凤凰网资讯"""
    source = "凤凰网"
    url = "https://tech.ifeng.com/shanklist/2-0-1/"
    html = fetch_html(url)
    items = parse_generic_list(html, "https://tech.ifeng.com", source, "media")
    if not items:
        url2 = "https://news.ifeng.com/c/special/7pSRIpVxkBj"
        html2 = fetch_html(url2)
        items = parse_generic_list(html2, "https://news.ifeng.com", source, "media")
    return items


def crawl_xinhua(days, keywords):
    """新华社科技频道"""
    source = "新华社"
    # 新华社科技AI关键词搜索
    url = "https://so.news.cn/#search?keyword=%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E6%94%BF%E7%AD%96&lang=cn&curPage=1&sortField=0&searchFields=1&dateFrom=&dateTo="
    html = fetch_html(url)
    items = parse_generic_list(html, "https://www.xinhuanet.com", source, "media")
    if not items:
        url2 = "http://www.xinhuanet.com/tech/"
        html2 = fetch_html(url2)
        items = parse_generic_list(html2, url2, source, "media")
    return items


def crawl_people(days, keywords):
    """人民日报"""
    source = "人民日报"
    url = "http://politics.people.com.cn/GB/1024/index.html"
    html = fetch_html(url)
    items = parse_generic_list(html, "http://www.people.com.cn", source, "media")
    return items


def crawl_cctv(days, keywords):
    """央视网"""
    source = "央视网"
    url = "https://news.cctv.com/tech/"
    html = fetch_html(url)
    return parse_generic_list(html, url, source, "media")


def crawl_smartcity(days, keywords):
    """智慧城市行业分析 - 人工智能大模型政策库"""
    from urllib.parse import unquote
    source = "智慧城市行业分析"
    base_url = "https://www.smartcity.team/category/policies/%e5%a4%a7%e6%a8%a1%e5%9e%8b%e6%94%bf%e7%ad%96%e5%ba%93/"
    html = fetch_html(base_url)
    if not html:
        return []
    
    soup = BeautifulSoup(html, 'lxml')
    items = []
    
    # 查找政策文章列表
    for article in soup.select('.post'):
        # 标题和链接
        title_elem = article.select_one('h2 a')
        if not title_elem:
            continue
        title = title_elem.get_text(strip=True)
        href = title_elem.get('href', '')
        if not title or not href:
            continue
        
        # href already is urlencoded, need unquote to get correct url
        url = unquote(href)
        
        # 日期信息
        date_text = ''
        meta_elem = article.select_one('.post-meta')
        if meta_elem:
            date_match = re.search(r'\d{4}年\d{1,2}月\d{1,2}日', meta_elem.get_text())
            if date_match:
                date_text = date_match.group(0)
        
        items.append({
            'title': title,
            'url': url,
            'date_text': date_text,
            'source': source,
            'source_type': 'media',
        })
    
    return items


# ─────────────────────────────────────────────
# 爬虫任务注册表
# ─────────────────────────────────────────────
CRAWLERS = [
    # ── 国家级（5个）──
    ("国务院",   crawl_guowuyuan),
    ("网信办",   crawl_cac),
    ("工信部",   crawl_miit),
    ("科技部",   crawl_most),
    ("发改委",   crawl_ndrc),
    # ── 广东省（保留你指定的：省 + 广州、深圳、东莞、佛山/顺德）──
    ("广东省",   crawl_gd),
    ("广州市",   crawl_gz),
    ("深圳市",   crawl_sz),
    ("佛山市",   crawl_foshan),
    ("东莞市",   crawl_dongguan),
    # ── 权威媒体（保留全部6个）──
    ("新华社",   crawl_xinhua),
    ("人民日报", crawl_people),
    ("央视网",   crawl_cctv),
    ("澎湃新闻", crawl_thepaper),
    ("新浪新闻", crawl_sina),
    ("凤凰网",   crawl_ifeng),
    # ── 行业政策库 ──
    ("智慧城市行业分析", crawl_smartcity),
]


# ─────────────────────────────────────────────
# 去重
# ─────────────────────────────────────────────
def deduplicate(items):
    seen_urls = set()
    seen_titles = set()
    result = []
    for item in items:
        url = item.get('url', '').strip()
        title = item.get('title', '').strip()
        if url and url in seen_urls:
            continue
        if title and title in seen_titles:
            continue
        if url:
            seen_urls.add(url)
        if title:
            seen_titles.add(title)
        result.append(item)
    return result


# ─────────────────────────────────────────────
# 正文片段抓取（可选，耗时较长）
# ─────────────────────────────────────────────
def fetch_snippet(url, max_chars=200):
    """抓取文章正文前N字，失败返回空字符串"""
    try:
        html = fetch_html(url, retries=1, sleep_range=(0.2, 0.5))
        if not html:
            return ""
        soup = BeautifulSoup(html, 'lxml')
        # 移除脚本/样式
        for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()
        # 尝试找正文区域
        content = soup.select_one(
            'div.article, div.content, div#content, div.main-content, '
            'div.text, article, div.zwyw_content, div.article-content'
        )
        text = (content or soup.body or soup).get_text(separator=' ', strip=True)
        # 清理多余空白
        text = re.sub(r'\s+', ' ', text)
        return text[:max_chars]
    except Exception as e:
        logger.debug(f"snippet fetch failed: {url} -> {e}")
        return ""


# ─────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description='爬取国内政府官网AI相关政策，输出JSON到stdout'
    )
    parser.add_argument(
        '--days', type=int, default=30,
        help='时间范围（天），默认30天'
    )
    parser.add_argument(
        '--keywords', nargs='+',
        default=['人工智能', 'AI', '大模型', '算法', '算力', '数字经济', '数据要素', '智能制造'],
        help='关键词列表，默认为常用AI关键词'
    )
    parser.add_argument(
        '--sources', nargs='+',
        default=None,
        help='指定爬取的来源（默认全部），如: 国务院 工信部 广东省'
    )
    parser.add_argument(
        '--no-snippet', action='store_true',
        help='不抓取正文片段（更快）'
    )
    parser.add_argument(
        '--workers', type=int, default=5,
        help='并发线程数，默认5'
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='输出调试日志到stderr'
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    # 过滤指定来源
    active_crawlers = CRAWLERS
    if args.sources:
        active_crawlers = [(name, fn) for name, fn in CRAWLERS if name in args.sources]
        if not active_crawlers:
            print(json.dumps({"error": f"未找到指定来源，可用: {[n for n,_ in CRAWLERS]}", "results": []},
                             ensure_ascii=False))
            return

    logger.info(f"开始爬取 {len(active_crawlers)} 个来源，时间范围: {args.days}天，关键词: {args.keywords}")

    raw_items = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        future_map = {
            executor.submit(fn, args.days, args.keywords): name
            for name, fn in active_crawlers
        }
        for future in as_completed(future_map):
            name = future_map[future]
            try:
                items = future.result()
                logger.info(f"[{name}] 获取 {len(items)} 条原始数据")
                raw_items.extend(items)
            except Exception as e:
                logger.error(f"[{name}] 爬取失败: {e}")

    # 过滤 + 去重
    filtered = []
    for item in raw_items:
        title = item.get('title', '')
        # 关键词过滤
        if not matches_keywords(title, args.keywords):
            continue
        # 日期过滤
        date_obj = parse_date(item.get('date_text', ''))
        if not is_within_days(date_obj, args.days):
            continue
        # 标准化日期
        item['date'] = date_obj.strftime('%Y-%m-%d') if date_obj else ''
        item.pop('date_text', None)
        filtered.append(item)

    filtered = deduplicate(filtered)

    # 可选：抓正文片段
    if not args.no_snippet and filtered:
        logger.info(f"开始抓取 {len(filtered)} 条政策正文片段...")
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            future_map = {
                executor.submit(fetch_snippet, item['url']): i
                for i, item in enumerate(filtered)
            }
            for future in as_completed(future_map):
                i = future_map[future]
                try:
                    filtered[i]['content_snippet'] = future.result()
                except Exception:
                    filtered[i]['content_snippet'] = ''
    else:
        for item in filtered:
            item.setdefault('content_snippet', '')

    # 按日期降序排列
    filtered.sort(key=lambda x: x.get('date', ''), reverse=True)

    # 输出结果
    output = {
        "query_date": datetime.now().strftime('%Y-%m-%d'),
        "date_range": {
            "days": args.days,
            "from": (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d'),
            "to": datetime.now().strftime('%Y-%m-%d'),
        },
        "keywords": args.keywords,
        "total": len(filtered),
        "results": filtered,
    }

    # 修复Windows stdout编码问题，强制utf-8输出
    json_str = json.dumps(output, ensure_ascii=False, indent=2)
    if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
        sys.stdout.reconfigure(encoding='utf-8')
    print(json_str)
    logger.info(f"完成，共输出 {len(filtered)} 条政策")


if __name__ == '__main__':
    main()
