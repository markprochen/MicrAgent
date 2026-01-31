
import psutil
import platform
import os

def get_cpu_info():
    """
    获取 CPU 信息和占用率。
    返回: CPU 核心数、使用率等详细信息
    """
    try:
        # CPU 核心数
        physical_cores = psutil.cpu_count(logical=False)
        total_cores = psutil.cpu_count(logical=True)

        # CPU 使用率
        cpu_percent = psutil.cpu_percent(interval=1)

        # CPU 频率
        cpu_freq = psutil.cpu_freq()

        result = f"""
🖥️ CPU 信息:
━━━━━━━━━━━━━━━━
物理核心数: {physical_cores}
逻辑核心数: {total_cores}
CPU 使用率: {cpu_percent}%
"""
        if cpu_freq:
            result += f"当前频率: {cpu_freq.current:.2f} MHz\n"
            result += f"最大频率: {cpu_freq.max:.2f} MHz\n"

        result += "━━━━━━━━━━━━━━━━"
        return result.strip()
    except Exception as e:
        return f"获取 CPU 信息失败: {str(e)}"

def get_memory_info():
    """
    获取内存使用情况。
    返回: 总内存、已用内存、可用内存、使用率等
    """
    try:
        mem = psutil.virtual_memory()

        total = mem.total / (1024 ** 3)  # 转换为 GB
        available = mem.available / (1024 ** 3)
        used = mem.used / (1024 ** 3)
        percent = mem.percent

        result = f"""
💾 内存信息:
━━━━━━━━━━━━━━━━
总内存: {total:.2f} GB
已用内存: {used:.2f} GB
可用内存: {available:.2f} GB
使用率: {percent}%
━━━━━━━━━━━━━━━━
"""
        return result.strip()
    except Exception as e:
        return f"获取内存信息失败: {str(e)}"

def get_running_processes(limit: int = 10):
    """
    获取当前运行的进程列表。
    参数:
    - limit: 返回的进程数量，默认为 10
    返回: 进程列表，包含 PID、名称、CPU 和内存占用
    """
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'],
                    'memory': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # 按 CPU 使用率排序
        processes.sort(key=lambda x: x['cpu'], reverse=True)

        result = f"""
📋 当前运行进程 (Top {limit}):
━━━━━━━━━━━━━━━━
"""
        for proc in processes[:limit]:
            result += f"PID: {proc['pid']:>6} | 名称: {proc['name']:<20} | CPU: {proc['cpu']:>5.1f}% | 内存: {proc['memory']:>5.1f}%\n"

        result += "━━━━━━━━━━━━━━━━"
        return result.strip()
    except Exception as e:
        return f"获取进程信息失败: {str(e)}"

def get_system_info():
    """
    获取系统基本信息。
    返回: 操作系统、主机名、架构等
    """
    try:
        result = f"""
🖥️ 系统信息:
━━━━━━━━━━━━━━━━
操作系统: {platform.system()} {platform.release()}
系统版本: {platform.version()}
主机名: {platform.node()}
架构: {platform.machine()}
处理器: {platform.processor()}
━━━━━━━━━━━━━━━━
"""
        return result.strip()
    except Exception as e:
        return f"获取系统信息失败: {str(e)}"

def get_disk_info():
    """
    获取磁盘使用情况。
    返回: 各分区的总容量、已用空间、可用空间、使用率
    """
    try:
        result = """
💿 磁盘信息:
━━━━━━━━━━━━━━━━
"""
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                total = usage.total / (1024 ** 3)
                used = usage.used / (1024 ** 3)
                free = usage.free / (1024 ** 3)
                percent = usage.percent

                result += f"""
设备: {partition.device}
挂载点: {partition.mountpoint}
文件系统: {partition.fstype}
总容量: {total:.2f} GB
已用空间: {used:.2f} GB
可用空间: {free:.2f} GB
使用率: {percent}%
"""
            except PermissionError:
                continue

        result += "━━━━━━━━━━━━━━━━"
        return result.strip()
    except Exception as e:
        return f"获取磁盘信息失败: {str(e)}"

def get_skills():
    """插件注册入口"""
    return {
        "get_cpu_info": get_cpu_info,
        "get_memory_info": get_memory_info,
        "get_running_processes": get_running_processes,
        "get_system_info": get_system_info,
        "get_disk_info": get_disk_info
    }
