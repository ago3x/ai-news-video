#!/usr/bin/env python3
"""
AI新闻搜索工具
自动搜索最新AI热点新闻
"""

import sys
import json
from typing import Optional, List, Dict

def search_ai_news(query: str = None, count: int = 5) -> List[Dict]:
    """
    搜索AI新闻
    
    Args:
        query: 搜索关键词，为空则返回今日热点
        count: 返回数量
    
    Returns:
        新闻列表 [{title, url, summary, source, date}]
    """
    try:
        from tavily import TavilyClient
    except ImportError:
        print("请安装 tavily-python: pip install tavily-python")
        return []
    
    # 使用Tavily搜索
    client = TavilyClient()
    
    if query:
        results = client.search(
            query=f"{query} AI news",
            search_depth="basic",
            max_results=count,
            include_answer=True
        )
    else:
        # 默认搜索AI热点
        results = client.search(
            query="AI artificial intelligence news latest",
            search_depth="basic",
            max_results=count,
            include_answer=True,
            topic="news"
        )
    
    news_list = []
    for item in results.get("results", []):
        news_list.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "summary": item.get("content", "")[:200],
            "source": item.get("source", ""),
            "date": item.get("published_date", "")
        })
    
    return news_list


def extract_news_content(url: str) -> Dict:
    """
    提取新闻详情
    
    Args:
        url: 新闻URL
    
    Returns:
        {title, content, author, date}
    """
    try:
        from tavily import TavilyClient
        client = TavilyClient()
        
        results = client.extract(urls=[url])
        
        if results and len(results) > 0:
            return {
                "url": url,
                "content": results[0].get("raw_content", "")[:5000],
                "title": results[0].get("title", "")
            }
    except Exception as e:
        print(f"提取失败: {e}")
    
    return {}


def generate_video_script(news: Dict) -> Dict:
    """
    从新闻生成视频脚本
    
    Args:
        news: 新闻信息 {title, summary, content}
    
    Returns:
        视频脚本
    """
    title = news.get("title", "")
    summary = news.get("summary", "")
    content = news.get("content", summary)
    
    # 简单提取关键信息
    # 实际应用中可以使用LLM生成更好的脚本
    
    script = {
        "topic": title,
        "voiceover": f"刚刚，{title}。{summary}",
        "shots": [
            {"type": "cover", "duration": 5},
            {"type": "features", "duration": 8},
            {"type": "compare", "duration": 7},
            {"type": "ending", "duration": 5}
        ]
    }
    
    return script


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法: python search_news.py [关键词]")
        print("示例: python search_news.py 'OpenAI GPT'")
        print("      python search_news.py  # 搜索今日AI热点")
        sys.exit(1)
    
    query = sys.argv[1] if len(sys.argv) > 1 else None
    
    print(f"🔍 搜索AI新闻: {query or '今日热点'}\n")
    
    news_list = search_ai_news(query)
    
    if not news_list:
        print("未找到相关新闻")
        sys.exit(1)
    
    for i, news in enumerate(news_list, 1):
        print(f"{i}. {news['title']}")
        print(f"   来源: {news['source']}")
        print(f"   摘要: {news['summary'][:100]}...")
        print(f"   链接: {news['url']}")
        print()


if __name__ == "__main__":
    main()