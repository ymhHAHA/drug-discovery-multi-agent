"""主程序入口"""
import os
import sys

project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from langchain_core.messages import HumanMessage
from src.config import Config
from src.workflow import build_workflow
from src.utils import save_report_to_md

def run_analysis(disease: str, save_report: bool = True):
    """运行药物靶点发现分析"""
    # 验证配置
    config = Config()
    config.validate()
    
    print(f"开始分析疾病：{disease}")
    
    # 构建工作流
    app = build_workflow()
    
    # 初始状态
    initial_state = {
        "disease": disease,
        "messages": [HumanMessage(content=f"请对疾病 {disease} 进行药物靶点发现分析")],
        "plan": [],
        "current_step": 0,
        "shared_results": {},
        "candidate_genes": [],
        "final_report": "",
        "current_critique_round": 0,
        "revision_instructions": None
    }
    
    # 运行工作流
    final_state = None
    for state in app.stream(initial_state, stream_mode="values"):
        final_state = state
        if state.get("current_step", 0) > 0 and state["current_step"] <= len(state.get("plan", [])):
            step_info = state["plan"][state["current_step"]-1]
            print(f"[步骤 {state['current_step']}] {step_info.get('description', '处理中...')}")
    
    # 保存结果
    if final_state and final_state.get("final_report") and save_report:
        candidate_genes = final_state["shared_results"].get("literature_agent", {}).get("candidate_genes", [])
        filename = save_report_to_md(
            disease,
            final_state['final_report'],
            candidate_genes
        )
        print(f"\n报告已保存至: {filename}")
        print(f"候选基因: {', '.join(candidate_genes)}")
    
    return final_state

if __name__ == "__main__":
    disease = sys.argv[1] if len(sys.argv) > 1 else "肺癌"
    run_analysis(disease)


#if __name__ == "__main__":
#    # 设置API Key
#    os.environ["DASHSCOPE_API_KEY"] = "your-api-key-here"  # 替换为实际的API Key
    
    # 运行分析
#    run_analysis("肺癌")
