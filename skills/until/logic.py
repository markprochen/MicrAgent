
import os
import json
import re
import sys
from datetime import datetime

def load_agent_knowledge(directory="."):
    """扫描指定目录下的所有 .md 文件并合并内容"""
    knowledge_text = "\n[已知背景知识]:\n"
    found = False
    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            with open(os.path.join(directory, filename), 'r', encoding='utf-8') as f:
                knowledge_text += f"文件 {filename} 内容: {f.read()}\n"
                found = True
    return knowledge_text if found else ""

def getdate():
     return datetime.now().strftime('%Y-%m-%d')

def query_my_profile(topic: str):
    """
    当需要了解关于用户的名字、爱好、习惯或已保存的技能配置时调用此工具。
    参数 topic: 关键词，如 '爱好', '名字'。
    """
    # 这里逻辑可以写成读取当前目录下所有的 .md 文件
    # 然后搜索包含 topic 关键词的那一段
    knowledge = load_agent_knowledge(".") # 复用上面的函数
    return f"在我的资料库中找到如下信息：\n{knowledge}"

# --- 1. 定义本地文件操作函数 (Skills) ---
def read_local_file(file_path: str):
    try:
        # 增加检查：如果是目录，提醒 AI 使用 list 工具
        if os.path.isdir(file_path):
            return f"错误: '{file_path}' 是一个目录。请使用 list_files_recursive 工具查看目录内容。"
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"错误: {str(e)}"

def write_local_file(file_path: str, content: str):
    try:
        # 获取文件夹路径
        directory = os.path.dirname(file_path)
        # 只有当路径不为空时，才尝试创建文件夹
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"成功写入到 {os.path.abspath(file_path)}" # 返回绝对路径，方便查看
    except Exception as e:
        return f"写入失败: {str(e)}"
    
def create_local_dir(file_path: str):
    try:
        # 获取文件夹路径
        directory = os.path.dirname(file_path)
        # 只有当路径不为空时，才尝试创建文件夹
        if directory:
            os.makedirs(directory, exist_ok=True)

        return f"成功创建文件 {os.path.abspath(file_path)}" # 返回绝对路径，方便查看
    except Exception as e:
        return f"写入失败: {str(e)}"
def list_files_recursive(directory: str = ".", exclude_dirs: list = None,exsion:str=".py"):
    """
    递归列出指定目录下的所有 exsion 文件。
    参数:
    - directory: 要扫描的根目录
    - exclude_dirs: 要排除的目录列表，例如 ['mcp_server', '.venv']
    - exsion: 文件后缀
    """
    if exclude_dirs is None:
        exclude_dirs = ['mcp_server', '.venv', '__pycache__', '.git']
    
    file_list = []
    try:
        for root, dirs, files in os.walk(directory):
            # 排除不需要扫描的目录
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith(exsion):
                    # 返回相对路径
                    rel_path = os.path.relpath(os.path.join(root, file), directory)
                    file_list.append(rel_path)
        
        return "\n".join(file_list) if file_list else "未找到符合条件的 Python 文件。"
    except Exception as e:
        return f"扫描目录失败: {str(e)}"
    
def append_to_local_file(file_path: str, content: str):
    """
    向现有文件末尾追加文本内容。如果文件不存在会报错。
    参数:
    - file_path: 文件路径
    - content: 要追加的字符串内容
    """
    try:
        if not os.path.exists(file_path):
            return f"错误: 文件 {file_path} 不存在。如果要创建新文件，请使用 write_local_file。"
        
        # 使用 'a' 模式打开文件进行追加
        with open(file_path, 'a', encoding='utf-8') as f:
            # 自动检查文件末尾是否已有换行符，如果没有则补一个，防止内容连在一起
            f.write('\n' + content if not content.startswith('\n') else content)
            
        return f"成功向 {os.path.abspath(file_path)} 追加了内容。"
    except Exception as e:
        return f"追加失败: {str(e)}"
def get_skills():
    """插件注册入口"""
    return {
        "load_agent_knowledge": load_agent_knowledge,
        "getdate":getdate,
        "query_my_profile":query_my_profile,
        "read_local_file":read_local_file,
        "write_local_file":write_local_file,
        "create_local_dir":create_local_dir,
        "list_files_recursive":list_files_recursive
    }