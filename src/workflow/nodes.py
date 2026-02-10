"""工作流节点定义"""
import os
import sys
import json
import re
from datetime import datetime
from langchain_core.messages import AIMessage, ToolMessage

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from src.workflow.state import AgentState
from src.agents import literature_agent, bio_agent, chem_agent, critic_agent
from src.config import Config
from src.llm_client import LLMClient

def planner_node(state: AgentState) -> dict:
    """规划节点"""
    config = Config()
    llm = LLMClient(config.api_key, config.model)
    
    disease = state["disease"]
    prompt = f"""你是一名药物发现项目的高级协调者。

疾病：{disease}

请将药物靶点发现任务分解为清晰、可执行的步骤。
每个步骤必须指定：
- step_id（从1开始递增）
- description（简洁描述）
- agent（只能从以下选择：literature_agent, bio_agent, chem_agent, report）

输出严格为JSON数组。"""

    response = llm.call(prompt, config.temperature_planner)
    
    try:
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        plan = json.loads(json_match.group(0)) if json_match else json.loads(response)
    except:
        plan = [
            {"step_id": 1, "description": "文献挖掘与候选基因识别", "agent": "literature_agent"},
            {"step_id": 2, "description": "生物信息学优先级评估", "agent": "bio_agent"},
            {"step_id": 3, "description": "化合物开发现状分析", "agent": "chem_agent"},
            {"step_id": 4, "description": "生成最终报告", "agent": "report"},
        ]
    
    return {
        "plan": plan,
        "current_step": 0,
        "shared_results": {},
        "revision_instructions": None,
        "messages": state["messages"] + [AIMessage(content=f"执行计划已生成，共{len(plan)}步")]
    }

def executor_node(state: AgentState) -> dict:
    """执行节点"""
    config = Config()
    llm = LLMClient(config.api_key, config.model)
    
    plan = state["plan"]
    idx = state["current_step"]
    
    if idx >= len(plan):
        return {"messages": state["messages"] + [AIMessage(content="所有步骤已执行完毕")]}

    step = plan[idx]
    agent_name = step["agent"]
    context = "\n".join([m.content[:600] for m in state["messages"][-20:] if isinstance(m, (AIMessage, ToolMessage))])
    revision_instructions = state.get("revision_instructions") or ""

    # 执行相应的agent
    if agent_name == "literature_agent":
        result = literature_agent.invoke({
            "disease": state["disease"],
            "context": context,
            "revision_instructions": revision_instructions
        })
        candidate_genes = result["candidate_genes"]
    elif agent_name == "bio_agent":
        genes = state["shared_results"].get("literature_agent", {}).get("candidate_genes", [])
        result = bio_agent.invoke({
            "genes": genes,
            "disease": state["disease"],
            "context": context,
            "revision_instructions": revision_instructions
        }) if genes else {}
        candidate_genes = state.get("candidate_genes", [])
    elif agent_name == "chem_agent":
        targets = state["shared_results"].get("bio_agent", {}).get("top_targets", [])
        result = chem_agent.invoke({
            "targets": targets,
            "disease": state["disease"],
            "context": context,
            "revision_instructions": revision_instructions
        }) if targets else {}
        candidate_genes = state.get("candidate_genes", [])
    elif agent_name == "report":
        # 生成最终报告
        lit = state["shared_results"].get("literature_agent", {}).get("analysis", "")
        bio = state["shared_results"].get("bio_agent", {}).get("analysis", "")
        chem = state["shared_results"].get("chem_agent", {}).get("analysis", "")
        
        prompt = f"""基于以下最终确认的分析结果，为疾病'{state["disease"]}'生成专业药物靶点发现报告。

文献分析：
{lit}

生物信息学分析：
{bio}

化学信息学分析：
{chem}

报告结构：
# {state["disease"]} 药物靶点发现报告

## 执行摘要
- 分析日期：{datetime.now().strftime('%Y年%m月%d日')}
- 关键发现（3-5条）
- 推荐靶点（前3个）

## 1. 候选靶点概述
## 2. 靶点优先级分析
## 3. 化合物开发现状
## 4. 开发建议
### 短期目标 (6-12个月)
### 中期目标 (1-3年)
## 5. 结论"""

        report = llm.call(prompt, config.temperature_report)
        return {
            "final_report": report,
            "messages": state["messages"] + [AIMessage(content="最终报告已生成")],
            "current_step": idx + 1,
            "revision_instructions": None
        }
    else:
        result = {}
        candidate_genes = state.get("candidate_genes", [])
    
    shared_results = state["shared_results"].copy()
    shared_results[agent_name] = result
    
    return {
        "shared_results": shared_results,
        "candidate_genes": candidate_genes,
        "messages": state["messages"] + [ToolMessage(content=json.dumps(result, ensure_ascii=False), tool_call_id="temp")],
        "current_critique_round": 0,
        "revision_instructions": None,
        "current_step": idx + 1
    }

def critic_node(state: AgentState) -> dict:
    """批评节点"""
    idx = state["current_step"] - 1
    step = state["plan"][idx]
    output = state["shared_results"].get(step["agent"], {})
    context = "\n".join([m.content[:600] for m in state["messages"][-20:]])
    
    critique = critic_agent.invoke({
        "task_description": step["description"],
        "output": output,
        "context": context
    })
    
    round_num = state.get("current_critique_round", 0) + 1
    suggestions = "\n".join(critique.get("suggestions", []))
    
    return {
        "messages": state["messages"] + [AIMessage(content=f"第{round_num}轮审查结果：\n{json.dumps(critique, ensure_ascii=False, indent=2)}")],
        "current_critique_round": round_num,
        "revision_instructions": None if critique.get("pass", False) else suggestions
    }

def decide_next(state: AgentState) -> str:
    """决策下一步"""
    config = Config()
    
    if state["current_step"] >= len(state["plan"]):
        return "end"
    
    current_agent = state["plan"][state["current_step"] - 1]["agent"]
    if current_agent == "report":
        return "executor"
    
    critique_msgs = [m for m in reversed(state["messages"]) if "审查结果" in m.content]
    if not critique_msgs:
        return "critic"
    
    latest = critique_msgs[0].content
    try:
        critique_json = json.loads(re.search(r'\{.*\}', latest).group(0))
        passed = critique_json.get("pass", False) and critique_json.get("score", 0) >= config.critique_pass_score
        max_rounds = state["current_critique_round"] >= config.max_critique_rounds
        return "executor" if passed or max_rounds else "critic"
    except:
        return "critic"
