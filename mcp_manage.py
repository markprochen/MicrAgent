import os
import re
import sys
import importlib.util
from pathlib import Path

class MCPManager:
    def __init__(self, skills_dir="./skills"):
        self.skills_dir = Path(skills_dir)
        self.tools = {}               # 存放函数名 -> 函数句柄的映射
        self.skill_docs = {}          # 存放技能包名 -> doc.md 绝对路径的映射
        self.skill_to_brain_map = {}  # 存放技能包名 -> 建议大脑(如 coder)的映射
        
        # 初始扫描
        self.scan_skills()

    def scan_skills(self):
        """
        全量扫描技能目录，建立工具索引和文档索引，并解析模型路由偏好。
        """
        if not self.skills_dir.exists():
            self.skills_dir.mkdir(parents=True, exist_ok=True)

        # 扫描每个子目录
        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir():
                skill_name = skill_path.name
                
                # 1. 解析文档与路由偏好 (doc.md)
                doc_file = skill_path / "doc.md"
                if doc_file.exists():
                    self.skill_docs[skill_name] = doc_file
                    self._extract_brain_preference(skill_name, doc_file)
                
                # 2. 加载逻辑代码 (logic.py)
                logic_file = skill_path / "logic.py"
                if logic_file.exists():
                    self._load_logic(skill_name, logic_file)
        
        return list(self.skill_docs.keys())

    def _extract_brain_preference(self, skill_name, doc_path):
        """
        从 doc.md 中提取 # Preferred Brain: xxx 标签。
        用于支持隐式路由。
        """
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 匹配格式: # Preferred Brain: coder 或 Preferred Brain: reasoner
                match = re.search(r"Preferred Brain:\s*(\w+)", content)
                if match:
                    brain_id = match.group(1).lower()
                    self.skill_to_brain_map[skill_name] = brain_id
                    # print(f"📍 技能 [{skill_name}] 已绑定大脑偏好: {brain_id}")
        except Exception as e:
            print(f"⚠️ 解析技能 [{skill_name}] 路由标签失败: {e}")

    def _load_logic(self, skill_name, file_path):
        """
        动态加载逻辑模块并调用其 get_skills 入口。
        """
        try:
            # 模块命名空间处理
            module_name = f"skills.{skill_name}.logic"
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            
            # 允许模块内使用相对导入
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 调用约定好的 get_skills 函数
            if hasattr(module, "get_skills"):
                new_tools = module.get_skills()
                if isinstance(new_tools, dict):
                    # 注册工具，同时保留包名信息 (如: until.read_local_file)
                    for func_name, func_handle in new_tools.items():
                        self.tools[func_name] = func_handle
                        # 同时支持全限定名调用，方便 AI 区分
                        self.tools[f"{skill_name}.{func_name}"] = func_handle
                    # print(f"✅ 技能模块 [{skill_name}] 逻辑加载成功")
        except Exception as e:
            print(f"❌ 加载技能模块 [{skill_name}] 失败: {e}")

    def get_skill_detail(self, skill_name: str) -> str:
        """
        【AI可用工具】按需读取技能的详细 doc.md 说明手册。
        """
        doc_path = self.skill_docs.get(skill_name)
        if doc_path and os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f"\n--- [{skill_name}] 详细操作手册 ---\n{f.read()}"
        return f"错误：未找到技能 [{skill_name}] 的详细手册文档。"

    def load_static_md(self, filename: str) -> str:
        """
        读取项目根目录下的静态 MD 文件 (如 manifest.md, base.md)。
        """
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read()
        return f"警告：文件 {filename} 不存在。"

# 全局单例
mcp_manager = MCPManager()