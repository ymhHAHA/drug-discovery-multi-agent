"""文件处理工具"""
from datetime import datetime
from typing import List

def save_report_to_md(disease: str, report: str, candidate_genes: List[str], output_dir: str = ".") -> str:
    """保存报告为Markdown文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/{disease.replace(' ', '_')}_药物靶点发现报告_{timestamp}.md"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {disease} 药物靶点发现报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**候选基因**: {', '.join(candidate_genes)}\n\n")
        f.write("---\n\n")
        f.write(report)
    
    return filename
