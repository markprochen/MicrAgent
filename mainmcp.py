import os
import re
import json
import ast
from typing import Annotated, List, Union, TypedDict
from datetime import datetime
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver  # 导入持久化记忆

from mcp_manage import MCPManager
from ModelManager import ModelManager

load_dotenv()

# --- 1. 初始化管理中心 ---
mcp_manager = MCPManager()
# 初始工具集
ALL_TOOLS = {
    "get_skill_detail": mcp_manager.get_skill_detail,
    **mcp_manager.tools
}

# --- 2. 定义状态 ---
class AgentState(TypedDict):
    # add_messages 会将新消息追加到历史中
    messages: Annotated[List[BaseMessage], add_messages]
    # next_model 将由 execute_tool_node 更新并持久化
    next_model: str 

# --- 3. 模型管理 ---
model_manager = ModelManager()

# --- 4. 节点定义 ---
def call_agent_node(state: AgentState):
    # 1. 获取当前用户选定的模型
    target_model_id = state.get("next_model") or "reasoner"
    llm = model_manager.get_model(target_model_id)
    
    # 2. 清洗历史上下文 (Context Cleaning)
    # 如果当前不是 R1 模型，我们把历史消息里的 <think> 标签全部删掉再发给它
    processed_messages = []
    for msg in state["messages"]:
        if isinstance(msg, (HumanMessage, SystemMessage)):
            processed_messages.append(msg)
        elif hasattr(msg, "content"):
            # 如果是 AI 的消息，且当前模型不是 reasoner (假设只有 reasoner 会产出 think)
            if target_model_id != "reasoner":
                clean_content = re.sub(r"<think>.*?</think>", "", msg.content, flags=re.DOTALL).strip()
                processed_messages.append(msg.__class__(content=clean_content))
            else:
                processed_messages.append(msg)

    # 3. 加载 manifests... (保持不变)
    base_info = mcp_manager.load_static_md("base.md")
    manifest = mcp_manager.load_static_md("manifest.md")
    
    system_prompt = f"{base_info}\n\n[当前大脑]: {target_model_id}\n\n{manifest}"
    
    # 使用清洗后的消息发送给 LLM
    final_input = [SystemMessage(content=system_prompt)] + processed_messages
    
    response = llm.invoke(final_input)
    return {"messages": [response]}
def execute_tool_node(state: AgentState):
    last_message = state["messages"][-1]
    content = last_message.content
    
    # 依然保留从 state 获取 next_model 的逻辑，保证模型状态在图中流转
    current_model = state.get("next_model", "reasoner")

    # 解析 Action / Input (保持原来的正则和 Payload 逻辑)
    # ... (省略解析代码) ...

    # 执行完成后
    return {
        "messages": [HumanMessage(content=f"工具执行反馈...")],
        "next_model": current_model # 保持用户选择的模型，不要去修改它
    }

# --- 5. 构建图 ---
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_agent_node)
workflow.add_node("tools", execute_tool_node)

workflow.add_edge(START, "agent")
# 条件边：根据模型输出是否包含 Action 决定去工具节点还是结束
workflow.add_conditional_edges(
    "agent", 
    lambda x: "tools" if "Action:" in x["messages"][-1].content else END
)
workflow.add_edge("tools", "agent")

# 启用持久化记忆
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)

# --- 6. 交互入口 ---
if __name__ == "__main__":
    # 1. 启动时显示可用模型列表 (由 ModelManager 动态生成)
    print(model_manager.get_models_menu())
    
    # 2. 初始化默认模型
    # 寻找配置文件中标记为 default 的 ID
    current_model_id = "reasoner"
    for cfg in model_manager.config['models']:
        if cfg.get('default'):
            current_model_id = cfg['id']
            break
    
    # 为 LangGraph 准备持久化配置
    config = {"configurable": {"thread_id": "Wink_User_Session"}}
    
    print(f"✅ 系统就绪。当前默认大脑: [{current_model_id}]")

    while True:
        prompt_str = f"\n({current_model_id}) 用户 > "
        query = input(prompt_str).strip()
        
        if not query:
            continue
        if query.lower() in ["exit", "quit", "q"]:
            break

        # --- 3. 动态路由指令处理 ---
        if query.startswith("/"):
            parts = query.split()
            cmd = parts[0].lower()
            
            # /list 指令：重新显示菜单
            if cmd == "/list":
                print(model_manager.get_models_menu())
                continue
            
            # /use [id] 指令：切换模型
            elif cmd == "/use" and len(parts) > 1:
                target_id = parts[1].lower()
                if target_id in model_manager.get_all_ids():
                    current_model_id = target_id
                    print(f"🧠 已切换大脑为: [{current_model_id}]")
                else:
                    print(f"❌ 错误: 找不到 ID 为 '{target_id}' 的模型。输入 /list 查看可用 ID。")
                continue
            
            else:
                print("❓ 未知指令。可用指令: /list, /use [id]")
                continue

        # --- 4. 运行 Agent 图 ---
        # 每次运行前，将当前选定的 current_model_id 放入 initial_state
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "next_model": current_model_id 
        }

        # 运行流
        # 注意：这里我们使用 stream_mode="values" 或 "updates"
        for output in app.stream(initial_state, config=config, stream_mode="updates"):
            for node_name, node_state in output.items():
                if node_name == "agent":
                    # 打印 AI 的回答，同时标识是哪个模型生成的
                    last_msg = node_state['messages'][-1]
                    print(f"\n[{current_model_id}]:\n{last_msg.content}")
                elif node_name == "tools":
                    # 打印工具执行过程
                    tool_res = node_state['messages'][-1]
                    print(f"\n[系统执行结果]: {tool_res.content}")