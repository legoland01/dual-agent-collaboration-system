"""
TODO模板管理模块

管理TODO内容模板，支持配置文件和内置模板。
"""

import os
import yaml
from typing import Dict, Optional, List


DEFAULT_TEMPLATES = {
    "REQUIREMENT": {
        "content_prefix": "实现",
        "required_fields": ["requirement_id"],
        "optional_fields": ["acceptance_criteria"]
    },
    "BUG_FIX": {
        "content_prefix": "修复",
        "required_fields": ["bug_id", "root_cause"],
        "optional_fields": ["fix_plan", "test_case"]
    },
    "MANUAL": {
        "content_prefix": "",
        "required_fields": [],
        "optional_fields": []
    }
}


class TodoTemplate:
    """TODO模板管理"""
    
    def __init__(self, config_file: str = "config/templates.yaml"):
        """
        Args:
            config_file: 模板配置文件路径
        """
        self.config_file = config_file
        self.templates = DEFAULT_TEMPLATES.copy()
        self._load_templates()
    
    def _load_templates(self):
        """从配置文件加载模板"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    user_templates = yaml.safe_load(f)
                    if user_templates and "templates" in user_templates:
                        self.templates.update(user_templates["templates"])
            except Exception:
                pass
    
    def get_template(self, template_type: str) -> Optional[Dict]:
        """
        获取模板
        
        Args:
            template_type: 模板类型
        
        Returns:
            模板配置或None
        """
        return self.templates.get(template_type.upper())
    
    def list_templates(self) -> List[str]:
        """
        列出所有可用模板
        
        Returns:
            模板类型列表
        """
        return list(self.templates.keys())
    
    def apply(self, template_type: str, context: Dict) -> Dict:
        """
        应用模板
        
        Args:
            template_type: 模板类型
            context: 上下文数据
        
        Returns:
            填充后的字段
        """
        template = self.get_template(template_type)
        if not template:
            return context
        
        result = context.copy()
        
        # 添加前缀
        if template.get("content_prefix") and "content" in result:
            result["content"] = f"{template['content_prefix']}: {result['content']}"
        
        return result
    
    def validate_required_fields(self, template_type: str, data: Dict) -> tuple[bool, List[str]]:
        """
        验证必填字段
        
        Args:
            template_type: 模板类型
            data: 数据
        
        Returns:
            (是否通过, 缺失字段列表)
        """
        template = self.get_template(template_type)
        if not template:
            return True, []
        
        required = template.get("required_fields", [])
        missing = [f for f in required if f not in data or not data[f]]
        
        return len(missing) == 0, missing
