"""工作流图构建"""

import os
import sys


project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from langgraph.graph import StateGraph, END
from src.workflow.state import AgentState
from src.workflow.nodes import planner_node, executor_node, critic_node, decide_next

def build_workflow():
    """构建工作流"""
    workflow = StateGraph(AgentState)
    
    # 添加节点
    workflow.add_node("planner", planner_node)
    workflow.add_node("executor", executor_node)
    workflow.add_node("critic", critic_node)
    
    # 设置入口
    workflow.set_entry_point("planner")
    
    # 添加边
    workflow.add_edge("planner", "executor")
    
    # 添加条件边
    workflow.add_conditional_edges(
        "executor",
        lambda s: "critic" if s["current_step"] < len(s["plan"]) and s["plan"][s["current_step"]-1]["agent"] != "report" else "end",
        {"critic": "critic", "end": END}
    )
    
    workflow.add_conditional_edges(
        "critic",
        decide_next,
        {"critic": "executor", "executor": "executor", "end": END}
    )
    
    return workflow.compile()
