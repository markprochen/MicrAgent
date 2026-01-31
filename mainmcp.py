import os
import re
import json
from typing import Annotated, List, TypedDict
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from mcp_manage import mcp_manager
import ast
from langchain_ollama import ChatOllama  # 新增此行 导入 Ollama 模型

load_dotenv()

# --- 初始化 ---
# 扫描技能
mcp_manager.scan_skills()

# 将 get_skill_detail 本身也注册为一个工具，供 AI 按需调用
BASE_TOOLS = {
    "get_skill_detail": mcp_manager.get_skill_detail
}
ALL_TOOLS = {**BASE_TOOLS, **mcp_manager.tools}

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]



def get_model():
    """
    根据环境变量动态获取模型实例。
    支持 MODEL_PROVIDER=local (Ollama) 或 remote (OpenAI兼容API)
    """
    provider = os.getenv("MODEL_PROVIDER", "local").lower()
    model_name = os.getenv("MODEL_NAME", "deepseek-r1:14b")
    if provider == "remote":
        # 适用于 DeepSeek 官方 API, SiliconFlow, OpenAI 等
        print(f"--- [模型加载]: 远程模式 ({model_name}) ---")
        return ChatOpenAI(
            model=model_name,
            api_key=os.getenv("API_KEY"),
            base_url=os.getenv("BASE_URL"),
            temperature=0.6
        )
    else:
        # 适用于本地部署的 Ollama
        print(f"--- [模型加载]: 本地模式 Ollama ({model_name}) ---")
        return ChatOllama(
            model=model_name,
            temperature=0.6,
            # Ollama 默认超时较短，建议对于复杂任务加长
            timeout=120 
        )
llm = get_model()
def call_agent_node(state: AgentState):
    # 加载必须的背景资料
    base_info = mcp_manager.load_static_md("base.md")
    # 加载极简的技能清单
    manifest = mcp_manager.load_static_md("manifest.md")
    
    # 动态生成工具函数的基本列表 (仅名称描述)
    tools_list = "\n".join([f"- {name}: {func.__doc__.splitlines()[0] if func.__doc__ else ''}" for name, func in ALL_TOOLS.items()])

    system_prompt = f"""
{base_info}

[可用技能概览 (Manifest)]
{manifest}

[可用工具函数清单]
{tools_list}

[重要指令]
1. 为了节省资源，本系统采用按需加载模式。
2. 当你需要使用某个技能（如 excel_handler）但不知道其详细参数或 SOP 时，必须首先执行：
   Action: get_skill_detail
   Action Input: {{"skill_name": "文件夹名称"}}
3. 获取详细手册后，再进行具体的业务操作。一次只执行一个 Action。
"""
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

def execute_tool_node(state: AgentState):
    raw_content = state["messages"][-1].content
    # 1. 移除思考过程
    content = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL)
    
    # 2. 提取 Action 和 Action Input
    action_match = re.search(r"Action:\s*([\w\.]+)", content)
    input_match = re.search(r"Action Input:\s*({.*})", content, re.DOTALL)
    
    # 3. --- 核心创新：提取原始内容块 ---
    # 这样代码和 MD 就不需要转义，直接原样放在标签里即可
    payload_match = re.search(r"\[CONTENT_START\]\n?(.*?)\n?\[CONTENT_END\]", content, re.DOTALL)
    payload = payload_match.group(1) if payload_match else None

    if action_match and input_match:
        tool_name = action_match.group(1).split('.')[-1]
        try:
            # 这里的 JSON 变简单了，因为它不包含复杂的代码字符串
            args = json.loads(input_match.group(1).replace("'", '"'))
            
            # 如果存在 Payload，自动将其注入到工具参数中
            if payload and "content" in args:
                args["content"] = payload
            elif payload and tool_name == "deploy_new_skill": # 兼容你的进化工具
                args["code_content"] = payload

            if tool_name in ALL_TOOLS:
                print(f"--- [执行工具]: {tool_name} (Payload模式: {payload is not None}) ---")
                res = ALL_TOOLS[tool_name](**args)
                
                # 热重载逻辑
                if tool_name in ["write_local_file", "write_python_skill", "deploy_new_skill"]:
                    mcp_manager.scan_skills()
                    ALL_TOOLS.update(mcp_manager.tools)
                    
                return {"messages": [HumanMessage(content=f"执行结果: {res}")]}
        except Exception as e:
            return {"messages": [HumanMessage(content=f"解析错误: {str(e)}。请确保 Action Input 为简单 JSON，长文本放在 [CONTENT_START] 标签中。")]}
    
    return {"messages": [HumanMessage(content="未解析到 Action。")]}

# --- 构建图 ---
workflow = StateGraph(AgentState)
workflow.add_node("agent", call_agent_node)
workflow.add_node("tools", execute_tool_node)
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", lambda x: "tools" if "Action:" in x["messages"][-1].content else END)
workflow.add_edge("tools", "agent")
app = workflow.compile()

if __name__ == "__main__":
    print(f"Agent 已启动。已发现技能包: {list(mcp_manager.skill_docs.keys())}")
    while True:
        query = input("\n用户: ")
        for output in app.stream({"messages": [HumanMessage(content=query)]}):
            for key, value in output.items():
                if key == "agent": print(f"\n[AI]:\n{value['messages'][-1].content}")