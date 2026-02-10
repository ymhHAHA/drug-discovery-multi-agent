"""LLM客户端模块"""
import dashscope
from dashscope import Generation
from typing import Optional

class LLMClient:
    """大语言模型客户端"""
    
    def __init__(self, api_key: str, model: str = "qwen-max"):
        self.model = model
        dashscope.api_key = api_key
    
    def call(self, prompt: str, temperature: float = 0.5) -> str:
        """调用LLM"""
        try:
            response = Generation.call(
                model=self.model,
                prompt=prompt,
                temperature=temperature,
                result_format='text'
            )
            if response.status_code == 200:
                return response.output.text.strip()
            return ""
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return ""
