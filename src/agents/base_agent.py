"""基础智能体"""
from abc import ABC, abstractmethod
from typing import Dict
from ..llm_client import LLMClient

class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, llm_client: LLMClient, temperature: float):
        self.llm = llm_client
        self.temperature = temperature
    
    @abstractmethod
    def process(self, **kwargs) -> Dict:
        """处理任务"""
        pass