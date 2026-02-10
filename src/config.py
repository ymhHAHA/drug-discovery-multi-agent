"""配置管理模块"""
import os
from dataclasses import dataclass

@dataclass
class Config:
    """系统配置"""
    # API配置
    api_key: str = os.getenv("DASHSCOPE_API_KEY", "")
    model: str = "qwen-max"
    
    # 温度参数
    temperature_literature: float = 0.7
    temperature_bio: float = 0.3
    temperature_chem: float = 0.4
    temperature_critic: float = 0.35
    temperature_planner: float = 0.5
    temperature_report: float = 0.3
    
    # 审查参数
    max_critique_rounds: int = 3
    critique_pass_score: int = 75
    def __post_init__(self):
		if not self.api_key:
			self.api_key = os.getenv("DASHSCOPE_API_KEY","")

    
    def validate(self):
        """验证配置"""
        if not self.api_key:
            raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
