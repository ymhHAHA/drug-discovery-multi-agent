"""工作流模块"""

import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if project_root not in sys.path:

    sys.path.insert(0, project_root)

from src.workflow.graph import build_workflow
from src.workflow.state import AgentState

__all__ = ['build_workflow', 'AgentState']
