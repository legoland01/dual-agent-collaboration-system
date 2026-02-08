"""RequirementsChecker: 需求文档完整性检查器

FR-AUTO-001: CLI自动检查需求文档的完整性，检测缺失项
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
import yaml
import re


class RequirementsCheckerError(Exception):
    """RequirementsChecker 错误"""
    pass


class RequirementsChecker:
    """需求文档完整性检查器"""
    
    REQUIRED_SECTIONS = [
        "概述",
        "功能需求",
        "CLI命令清单",
        "工时预估",
        "依赖关系",
        "签署确认",
    ]
    
    def __init__(self, docs_dir: Optional[str] = None):
        """
        初始化 RequirementsChecker
        
        Args:
            docs_dir: 需求文档目录，默认为项目根目录/docs/01-requirements
        """
        self.docs_dir = Path(docs_dir) if docs_dir else Path.cwd() / "docs" / "01-requirements"
    
    def check_completeness(self, doc_path: str) -> Dict[str, Any]:
        """
        检查需求文档完整性
        
        Args:
            doc_path: 文档路径
            
        Returns:
            {
                "complete": bool,
                "missing_sections": list[str],
                "missing_验收标准": list[str],
                "工时不一致": bool,
            }
        """
        doc = Path(doc_path)
        if not doc.exists():
            raise RequirementsCheckerError(f"文档不存在: {doc_path}")
        
        try:
            with open(doc, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            raise RequirementsCheckerError(f"读取文档失败: {str(e)}")
        
        missing_sections = []
        for section in self.REQUIRED_SECTIONS:
            if section not in content:
                missing_sections.append(section)
        
        has验收标准 = "验收标准" in content or "Acceptance Criteria" in content
        
        验收标准_count = len(re.findall(r"-\s*\[\s*\]", content))
        
        工时_in_section = 0
        工时_match = re.search(r"工时.*?(\d+)h", content)
        if 工时_match:
            工时_in_section = int(工时_match.group(1))
        
        工时_list = re.findall(r"(\d+)h", content)
        工时_total = sum(int(h) for h in 工时_list if int(h) <= 10)
        
        工时_inconsistent = False
        if len(工时_list) > 1 and 工时_in_section > 0:
            if 工时_total != 工时_in_section:
                工时_inconsistent = True
        
        return {
            "complete": len(missing_sections) == 0,
            "missing_sections": missing_sections,
            "has_验收标准": has验收标准,
            "验收标准_count": 验收标准_count,
            "工时_inconsistent": 工时_inconsistent,
            "工时明细": [int(h) for h in 工时_list],
        }
    
    def generate_report(self, doc_path: str) -> str:
        """
        生成完整性报告
        
        Args:
            doc_path: 文档路径
            
        Returns:
            报告字符串
        """
        result = self.check_completeness(doc_path)
        
        lines = []
        lines.append("=" * 50)
        lines.append("需求文档完整性报告")
        lines.append("=" * 50)
        lines.append(f"文档: {doc_path}")
        lines.append("")
        
        if result["complete"]:
            lines.append("✅ 文档完整")
        else:
            lines.append("❌ 文档不完整")
            lines.append("")
            lines.append("缺失章节:")
            for section in result["missing_sections"]:
                lines.append(f"  - {section}")
        
        lines.append("")
        lines.append(f"验收标准数量: {result['验收标准_count']}")
        
        if result["工时_inconsistent"]:
            lines.append("⚠️ 工时预估不一致")
            lines.append(f"  明细: {result['工时明细']}")
        
        lines.append("")
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def list_requirement_docs(self) -> List[Path]:
        """
        列出所有需求文档
        
        Returns:
            需求文档路径列表
        """
        if not self.docs_dir.exists():
            return []
        
        docs = []
        for f in self.docs_dir.iterdir():
            if f.is_file() and f.suffix in [".md", ".markdown"]:
                if "requirements" in f.name.lower() or "proposal" in f.name.lower():
                    docs.append(f)
        return docs
