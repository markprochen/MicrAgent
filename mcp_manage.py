import os
import importlib.util
from pathlib import Path

class MCPManager:
    def __init__(self, skills_dir="./skills"):
        self.skills_dir = Path(skills_dir)
        self.tools = {}      # 存放 python 函数句柄
        self.skill_docs = {} # 存放 skill_name -> doc_path 的映射

    def scan_skills(self):
        """扫描 skills 目录，支持‘纯文档’技能和‘代码+文档’技能"""
        if not self.skills_dir.exists():
            self.skills_dir.mkdir()

        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir():
                skill_name = skill_path.name
                
                # 无论有没有逻辑文件，只要有 doc.md，就记录这个技能
                doc_file = skill_path / "doc.md"
                if doc_file.exists():
                    self.skill_docs[skill_name] = doc_file
                
                # 尝试加载逻辑代码
                logic_file = skill_path / "logic.py"
                if logic_file.exists():
                    self._load_logic(skill_name, logic_file)

        return list(self.skill_docs.keys()) # 注意：返回所有有文档的技能名

    def _load_logic(self, skill_name, file_path):
        """动态加载 Python 模块中的 get_skills"""
        try:
            spec = importlib.util.spec_from_file_location(f"skill_{skill_name}", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "get_skills"):
                self.tools.update(module.get_skills())
        except Exception as e:
            print(f"❌ 加载技能 {skill_name} 逻辑失败: {e}")

    def get_skill_detail(self, skill_name: str) -> str:
        """【关键工具】由 AI 调用，按需读取对应的 .md 文档"""
        doc_path = self.skill_docs.get(skill_name)
        if doc_path and doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f"\n[已加载技能 {skill_name} 的详细说明手册]:\n{f.read()}"
        return f"错误：未找到技能 {skill_name} 的详细手册。"

    def load_static_md(self, filename):
        """加载基础 MD 文件 (base.md 或 manifest.md)"""
        path = Path(filename)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

# 实例化管理器
mcp_manager = MCPManager()