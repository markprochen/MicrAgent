import sys
from duckduckgo_search import DDGS
from playwright.sync_api import sync_playwright

def web_browser(action: str, url: str = None, selector: str = None, text: str = None):
    """
    网页操作工具。
    Action 选项:
    - 'goto': 访问网页并提取纯文本。
    - 'click': 点击指定 CSS 选择器的元素。
    - 'type': 在指定选择器输入文本。
    """
    try:
        with sync_playwright() as p:
            # 启动浏览器 (headless=True 为后台运行，想看过程改为 False)
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            if action == 'goto':
                page.goto(url, wait_until="networkidle")
                content = page.inner_text("body") # 获取全网页文本
                browser.close()
                return f"页面内容前 2000 字:\n{content[:2000]}"
            
            elif action == 'click':
                page.goto(url)
                page.click(selector)
                page.wait_for_timeout(2000) # 等待加载
                content = page.content()
                browser.close()
                return "点击成功"
                
            browser.close()
            return "未知操作"
    except Exception as e:
        return f"浏览器操作失败: {str(e)}"
    
def get_skills():
    """插件注册入口"""
    return {
        "web_browser": web_browser
    }