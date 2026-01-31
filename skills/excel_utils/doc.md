# Excel 数据处理手册 (excel_utils)

专门用于处理 .xlsx 表格。输入输出均采用 JSON 格式以便 AI 理解。

## 函数列表
1. **create_excel_with_headers**: `{"file_path": "路径", "headers": ["列1", "列2"]}`
   - 初始化一个全新的 Excel 文件。
2. **read_excel**: `{"file_path": "路径", "sheet_name": "表名"}`
   - 读取数据，返回 `List[Dict]` 格式。
3. **append_to_excel**: `{"file_path": "路径", "data": [{"列1": "值"}], "sheet_name": "Sheet1"}`
   - 向已有表格追加数据。`data` 必须是字典列表。
4. **get_excel_info**: `{"file_path": "路径"}`
   - 查看表格的 Sheet 名字和列名。

## 操作规范 (SOP)
- **结构检查**：在向表格写入数据前，务必先调用 `get_excel_info` 确认列名是否一致。
- **流程顺序**：如果是新任务，必须先执行 `create` 再执行 `append`。
- **大数据处理**：读取表格后，如果数据量过大，请自行进行逻辑摘要，不要全部输出给用户。