"""质量审查智能体"""
import json
import re
from typing import Dict
from langchain_core.tools import tool

@tool
def critic_agent(task_description: str, output: Dict, context: str) -> Dict:
    """质量审查"""
    from src.config import Config
    from src.llm_client import LLMClient
    
    config = Config()
    llm = LLMClient(config.api_key, config.model)
    
    output_str = json.dumps(output, ensure_ascii=False, indent=2)
    prompt = f"""你是药物发现领域的严格评审专家。

任务描述：{task_description}

被评审输出：
{output_str}

历史上下文：
{context}

请从以下维度严格评估：
1. 科学准确性
2. 完整性与逻辑性
3. 与疾病的相关性
4. 是否符合最新研究趋势
5. 是否存在明显错误或遗漏

返回严格JSON格式：
{{
  "pass": true 或 false,
  "score": 0-100,
  "issues": ["问题1", "问题2"],
  "suggestions": ["详细改进建议1", "详细改进建议2"]
}}"""
    
    response = llm.call(prompt, config.temperature_critic)
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    
    try:
        return json.loads(json_match.group(0)) if json_match else {"pass": False, "score": 30, "issues": ["解析失败"], "suggestions": []}
    except:
        return {"pass": False, "score": 30, "issues": ["解析失败"], "suggestions": []}
