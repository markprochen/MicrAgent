# 核心系统工具手册 (until)

本模块负责与本地操作系统交互、管理用户记忆及文件基础操作。

## 函数列表
1. **getdate**: `{}` 
   - 获取当前日期 (YYYY-MM-DD)。涉及时间计算时必调。
2. **query_my_profile**: `{"topic": "关键词"}`
   - 从本地记忆中检索用户的名字、爱好、习惯或项目背景。
3. **read_local_file**: `{"file_path": "路径"}`
   - 读取文件内容。**严禁读取目录路径**。
4. **write_local_file**: `{"file_path": "路径", "content": "内容"}`
   - 写入内容到文件。会自动创建不存在的中间目录。
5. **create_local_dir**: `{"file_path": "文件夹路径"}`
   - 创建文件夹。
6. **list_files_recursive**: `{"directory": "路径", "exclude_dirs": ["排除项"], "exsion": ".py"}`
   - 递归扫描文件夹下的特定后缀文件。
7. **append_to_local_file**: `{"file_path": "路径", "content": "内容"}`
   - **描述**: 在现有文件的末尾添加新内容，而不会删除原有的东西。
   - **场景**: 
     - 完善已有的 `doc.md` 手册。
     - 在 `logic.py` 中添加新的函数。
     - 记录任务日志或用户的最新指令。

## 操作规范 (SOP)
- **扫描先行**：在读取不确定的文件前，先用 `list_files_recursive` 确认文件是否存在。
- **目录保护**：如果尝试 `read_local_file` 报错权限拒绝，请检查是否误读了目录。
- **记忆更新**：当用户提到重要的个人信息时，使用 `write_local_file` 记录到 `.md` 文件中。