"""
来源标签管理模块

管理TODO来源标签，支持自动推断和手动指定。
"""

from typing import Optional, Dict, List


class SourceTag:
    """TODO来源标签管理"""
    
    VALID_SOURCES = ["REQUIREMENT", "BUG", "FEEDBACK", "MANUAL"]
    
    KEYWORDS = {
        "BUG": ["bug", "修复", "错误", "defect", "fix"],
        "REQUIREMENT": ["需求", "实现", "功能", "requirement", "feature", "implement"],
        "FEEDBACK": ["反馈", "意见", "feedback", "suggestion"]
    }
    
    def __init__(self):
        pass
    
    def validate(self, source: str) -> bool:
        """
        验证来源是否有效
        
        Args:
            source: 来源类型
        
        Returns:
            是否有效
        """
        return source.upper() in self.VALID_SOURCES
    
    def get_source_from_context(self, content: str) -> str:
        """
        从内容自动推断来源
        
        Args:
            content: TODO内容
        
        Returns:
            来源类型
        """
        content_lower = content.lower()
        
        for source, keywords in self.KEYWORDS.items():
            if any(kw in content_lower for kw in keywords):
                return source
        
        return "MANUAL"
    
    def normalize(self, source: str) -> str:
        """
        标准化来源名称
        
        Args:
            source: 来源类型
        
        Returns:
            标准化的来源类型
        """
        return source.upper() if self.validate(source) else "MANUAL"
    
    def get_valid_sources(self) -> List[str]:
        """获取所有有效来源类型"""
        return self.VALID_SOURCES.copy()
