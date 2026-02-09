"""工作流状态定义"""
from typing import Annotated, Sequence, List, Dict, TypedDict, Optional
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """智能体状态"""
    messages: Annotated[Sequence[BaseMessage], "add_messages"]
    disease: str
    plan: List[Dict]
    current_step: int
    shared_results: Dict[str, Dict]
    candidate_genes: List[str]
    final_report: str
    current_critique_round: int
    revision_instructions: Optional[str]