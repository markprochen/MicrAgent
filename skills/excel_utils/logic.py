import pandas as pd
import openpyxl
import os
import sys

def create_excel_with_headers(file_path: str, headers: list, sheet_name: str = 'Sheet1'):
    """
    创建一个全新的 Excel 文件并初始化表头。
    参数:
    - file_path: 文件保存路径
    - headers: 表头列表，例如 ["姓名", "年龄", "职位"]
    - sheet_name: 工作表名称
    """
    try:
        df = pd.DataFrame(columns=headers)
        directory = os.path.dirname(file_path)
        if directory: os.makedirs(directory, exist_ok=True)
        df.to_excel(file_path, index=False, sheet_name=sheet_name)
        return f"成功创建 Excel 文件: {file_path}"
    except Exception as e:
        return f"创建失败: {str(e)}"

def read_excel(file_path: str, sheet_name: str = None):
    """
    读取 Excel 文件内容。返回列表格式的数据。
    参数:
    - file_path: 文件路径
    - sheet_name: 指定读取的工作表名，不填则读取第一个
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        # 将数据转为 List[Dict] 格式，方便 AI 理解
        data = df.to_dict(orient='records')
        return f"读取成功，数据如下：\n{data[:10]}..." if len(data) > 10 else str(data)
    except Exception as e:
        return f"读取失败: {str(e)}"

def append_to_excel(file_path: str, data: list, sheet_name: str = 'Sheet1'):
    """
    向已有的 Excel 文件追加一行或多行数据。
    参数:
    - file_path: 文件路径
    - data: 要追加的数据列表，例如 [{"姓名": "张三", "年龄": 25}]
    - sheet_name: 工作表名称
    """
    try:
        if not os.path.exists(file_path):
            return "错误: 文件不存在，请先使用 create_excel_with_headers 创建文件。"
        
        new_df = pd.DataFrame(data)
        # 读取原有数据进行合并
        old_df = pd.read_excel(file_path, sheet_name=sheet_name)
        combined_df = pd.concat([old_df, new_df], ignore_index=True)
        
        combined_df.to_excel(file_path, index=False, sheet_name=sheet_name)
        return f"成功向 {file_path} 追加了 {len(data)} 条数据。"
    except Exception as e:
        return f"追加失败: {str(e)}"

def get_excel_info(file_path: str):
    """
    获取 Excel 文件的元数据（所有工作表名称、列名等）。
    """
    try:
        xl = pd.ExcelFile(file_path)
        info = {
            "sheet_names": xl.sheet_names,
            "columns": pd.read_excel(file_path).columns.tolist()
        }
        return str(info)
    except Exception as e:
        return f"获取信息失败: {str(e)}"

def merge_excel_files(file_paths: list, output_path: str):
    """
    合并多个 Excel 文件到一个新的文件中。
    参数:
    - file_paths: 文件路径列表
    - output_path: 合并后的保存路径
    """
    try:
        dfs = [pd.read_excel(f) for f in file_paths]
        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df.to_excel(output_path, index=False)
        return f"合并完成，保存至: {output_path}"
    except Exception as e:
        return f"合并失败: {str(e)}"

def get_skills():
    """插件注册入口，供主程序动态加载"""
    return {
        "create_excel_with_headers": create_excel_with_headers,
        "read_excel": read_excel,
        "append_to_excel": append_to_excel,
        "get_excel_info": get_excel_info,
        "merge_excel_files": merge_excel_files
    }