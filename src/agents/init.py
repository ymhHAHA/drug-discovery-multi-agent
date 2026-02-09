"""智能体模块"""
from .literature_agent import literature_agent
from .bio_agent import bio_agent
from .chem_agent import chem_agent
from .critic_agent import critic_agent

__all__ = ['literature_agent', 'bio_agent', 'chem_agent', 'critic_agent']