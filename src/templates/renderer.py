"""模板引擎模块。"""
from pathlib import Path
from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader, Template


class TemplateEngine:
    """模板引擎。"""
    
    TEMPLATES_DIR = "templates"
    
    def __init__(self, project_path: str):
        """初始化模板引擎。"""
        self.project_path = Path(project_path)
        self.templates_dir = self.project_path / self.TEMPLATES_DIR
        
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=True
        )
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """渲染模板。"""
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            raise ValueError(f"模板渲染失败: {e}")
    
    def render_string(self, template_str: str, context: Dict[str, Any]) -> str:
        """渲染模板字符串。"""
        template = self.env.from_string(template_str)
        return template.render(**context)
    
    def list_templates(self) -> list:
        """列出所有可用模板。"""
        return self.env.list_templates()
    
    def template_exists(self, template_name: str) -> bool:
        """检查模板是否存在。"""
        try:
            self.env.get_template(template_name)
            return True
        except Exception:
            return False


def render_template(template_name: str, context: Dict[str, Any], templates_dir: str) -> str:
    """渲染模板（简化函数）。"""
    env = Environment(loader=FileSystemLoader(templates_dir), autoescape=True)
    template = env.get_template(template_name)
    return template.render(**context)
