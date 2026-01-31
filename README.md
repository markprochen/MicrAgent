# 🤖 AI Agent 项目

一个基于 LangChain 和 LangGraph 构建的智能 Agent 系统，支持模块化技能扩展和多种大模型后端。

# 待改进点

- 给自学习机制提供代码沙箱，为logic提供测试能力，实现测试驱动开发（待完成）
- 添加多模型路由 (Model Router)（待完成）
- 接入标准 MCP 生态 （待完成）
- 记忆的向量化 (Vectorized Context) （待完成）

## ✨ 特性

- 🧩 **模块化技能系统** - 支持动态加载和扩展技能
- 🔄 **多模型支持** - 支持 Ollama 本地模型和 OpenAI 兼容 API
- 📊 **丰富的内置技能** - 包含天气查询、系统监控、Excel 处理、网页搜索等
- 📝 **按需文档加载** - 智能加载技能文档，节省系统资源
- 🌐 **网络能力** - 支持网页搜索和浏览器自动化

## 📁 项目结构

```
Agents/
├── skills/              # 技能模块目录
│   ├── excel_utils/    # Excel 数据处理
│   ├── web_search/     # 网页搜索
│   ├── web_browser/    # 网页浏览器
│   ├── weather/        # 天气查询
│   ├── system_monitor/# 系统监控
│   └── self_learning/  # 自我学习能力
├── mainmcp.py          # 主程序入口
├── mcp_manage.py       # 技能管理器
├── requirements.txt    # 项目依赖
├── base.md            # Agent 基础信息
└── manifest.md        # 技能清单
```

## 🚀 快速开始

### 环境要求

- Python 3.12.10 或更高版本

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd MicrAgent
```

2. **创建虚拟环境**（推荐）
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **安装 Playwright 浏览器驱动**（可选，如需使用网页浏览功能）
```bash
playwright install
```

### 配置说明

创建 `.env` 文件在项目根目录，配置以下内容：

```env
# 模型提供商选择：local (Ollama) 或 remote (OpenAI兼容API)
MODEL_PROVIDER=local

# 本地模式：Ollama 模型名称
MODEL_NAME=deepseek-r1:14b

# 远程模式：API 配置
API_KEY=your-api-key
BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
```

### 启动项目

```bash
python mainmcp.py
```

## 📚 内置技能说明

### 1. 天气查询 (weather)
- 查询全球城市的实时天气信息
- 支持中文和英文城市名
- 返回温度、湿度、风速和天气状况

### 2. 系统监控 (system_monitor)
- CPU 信息监控
- 内存使用情况
- 进程列表查看
- 磁盘空间检查
- 系统基本信息

### 3. Excel 数据处理 (excel_utils)
- 创建 Excel 文件
- 读取表格数据
- 追加数据
- 合并多个文件

### 4. 网页搜索 (web_search)
- 使用 DuckDuckGo 搜索引擎
- 获取实时信息
- 支持中英文搜索

### 5. 网页浏览器 (web_browser)
- 访问指定 URL
- 提取网页内容
- 模拟点击和输入操作

### 6. 系统工具 (until)
- 文件读写操作
- 目录管理
- 日期查询
- 用户画像管理

### 7. 自我学习 (self_learning)
- 创建新技能
- 编写技能代码
- 生成技能文档

## 🔧 扩展技能

项目支持通过 `self_learning` 模块动态创建新技能。新技能需要包含：

1. `logic.py` - 技能逻辑代码
2. `doc.md` - 技能说明文档
3. `__init__.py` - Python 包初始化文件

技能创建流程：
1. 使用 `write_python_skill` 创建逻辑代码
2. 使用 `write_local_file` 创建文档
3. 系统自动扫描并加载新技能

## 📝 使用示例

```python
# 启动 Agent 后，可以直接与它交互
用户: 查询北京的天气
用户: 查看当前 CPU 使用率
用户: 搜索 Python 最新版本
用户: 创建一个 Excel 表格
```

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [Ollama](https://ollama.com/)
- [Open-Meteo](https://open-meteo.com/)
