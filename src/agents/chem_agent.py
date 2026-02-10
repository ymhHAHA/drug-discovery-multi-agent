"""化学信息学智能体"""
from typing import Dict, List
from langchain_core.tools import tool

@tool
def chem_agent(targets: List[str], disease: str, context: str = "", revision_instructions: str = "") -> Dict:
    """化学信息学分析"""
    from src.config import Config
    from src.llm_client import LLMClient
    
    config = Config()
    llm = LLMClient(config.api_key, config.model)
    
    base_prompt = f"""你是一名药物化学专家。分析以下靶点的化合物开发现状。

靶点：{', '.join(targets)}
疾病：{disease}

历史上下文：
{context}

请详细分析：
- 已上市药物
- 临床试验中的化合物
- 主要开发挑战
- 市场机会
- 推荐开发策略"""

    prompt = f"""请根据以下改进建议修正你的上一次输出：

改进建议：
{revision_instructions}

原任务要求：
{base_prompt}

请重新生成完整的化学信息学分析。""" if revision_instructions else base_prompt
    
    response = llm.call(prompt, config.temperature_chem)
    return {"analysis": response}
