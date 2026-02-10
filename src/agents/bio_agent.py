"""生物信息学智能体"""
from typing import Dict, List
from langchain_core.tools import tool

@tool
def bio_agent(genes: List[str], disease: str, context: str = "", revision_instructions: str = "") -> Dict:
    """生物信息学评估"""
    from src.config import Config
    from src.llm_client import LLMClient
    
    config = Config()
    llm = LLMClient(config.api_key, config.model)
    
    base_prompt = f"""你是一名生物信息学专家。对以下基因作为'{disease}'治疗靶点进行优先级评估。

候选基因：{', '.join(genes)}

历史上下文：
{context}

评估维度：
- 可药性 (1-10分)
- 安全性 (1-10分)
- 有效性 (1-10分)
- 总结优势与挑战

请按优先级从高到低排序，并详细说明理由。"""

    prompt = f"""请根据以下改进建议修正你的上一次输出：

改进建议：
{revision_instructions}

原任务要求：
{base_prompt}

请重新生成完整的评估报告。""" if revision_instructions else base_prompt
    
    response = llm.call(prompt, config.temperature_bio)
    return {"analysis": response, "top_targets": genes[:3]}
