import os

def write_python_skill(skill_name: str, code_content: str):
    """
    【进化工具】专门用于自动部署一个新技能的 Python 逻辑。
    参数:
    - skill_name: 技能的名称（即 ./skills/ 下的目录名，如 'weather_query'）
    - code_content: 原始的 Python 代码内容。
    """
    try:
        # 统一指向 ./skills 目录
        target_dir = os.path.join("./skills", skill_name)
        
        # 1. 自动创建目录
        os.makedirs(target_dir, exist_ok=True)
        
        # 2. 写入核心逻辑 logic.py (注意：你的架构里叫 logic.py 而不是 skill_name.py)
        logic_path = os.path.join(target_dir, "logic.py")
        with open(logic_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
            
        # 3. 自动生成 __init__.py 确保目录可被识别为包
        init_path = os.path.join(target_dir, "__init__.py")
        if not os.path.exists(init_path):
            with open(init_path, 'w', encoding='utf-8') as f:
                f.write(f"# {skill_name} package")
                
        return f"✅ 技能 [{skill_name}] 代码部分已部署至 {logic_path}。请继续写入对应的 doc.md 完成进化。"
    except Exception as e:
        return f"❌ 技能部署失败: {str(e)}"