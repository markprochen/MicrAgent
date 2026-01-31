from duckduckgo_search import DDGS
from playwright.sync_api import sync_playwright
import sys

# --- 新增功能 1：网页搜索 ---
def web_search(query: str):
    """
    当需要搜索实时新闻、技术文档或本地知识库没有的信息时使用。
    """
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=5)]
            if not results:
                return "未找到相关搜索结果。"
            # 格式化输出，方便 AI 阅读
            formatted_res = ""
            for i, r in enumerate(results):
                formatted_res += f"[{i+1}] 标题: {r['title']}\n链接: {r['href']}\n摘要: {r['body']}\n\n"
            return formatted_res
    except Exception as e:
        return f"搜索出错: {str(e)}"
def get_skills():
    """插件注册入口"""
    return {
        "web_search": web_search
    }