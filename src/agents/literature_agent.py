"""文献挖掘智能体"""
import re
from typing import Dict, List
from langchain_core.tools import tool
from .base_agent import BaseAgent

@tool
def literature_agent(disease: str, context: str = "", revision_instructions: str = "") -> Dict:
    """文献挖掘：识别5个候选基因"""
    from src.config import Config
    from src.llm_client import LLMClient
    
    config = Config()
    llm = LLMClient(config.api_key, config.model)
    
    base_prompt = f"""你是一名文献挖掘专家。请为疾病'{disease}'识别5个最相关的治疗靶点候选基因（标准HGNC符号）。

历史上下文：
{context}

要求：
1. 基于最新研究
2. 与疾病关联性强
3. 考虑可药性潜力

输出格式：
首先直接列出5个基因（逗号分隔）：
GENE1, GENE2, GENE3, GENE4, GENE5

然后逐个解释每个基因与疾病的关联性。"""

    prompt = f"""请根据以下改进建议修正你的上一次输出：

改进建议：
{revision_instructions}

原任务要求：
{base_prompt}

请重新生成完整的文献分析输出。""" if revision_instructions else base_prompt
    
    response = llm.call(prompt, config.temperature_literature)
    genes = list(dict.fromkeys(re.findall(r'\b[A-Z][A-Z0-9]{2,}\b', response)))[:5]
    
    if len(genes) < 5:
        fallback = llm.call(f"请直接列出5个与{disease}最相关的HGNC基因符号，用逗号分隔。", config.temperature_literature)
        genes = list(dict.fromkeys(re.findall(r'\b[A-Z][A-Z0-9]{2,}\b', fallback)))[:5]
    
    return {"candidate_genes": genes, "analysis": response}
