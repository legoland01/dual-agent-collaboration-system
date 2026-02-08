"""SkillEnforcer: Skill强制加载检查器

FR-SKILL-001: 在CLI命令执行前，强制检查相关Skill是否已加载
"""
from pathlib import Path
from typing import Optional, Tuple, List
import yaml


class SkillEnforcerError(Exception):
    """SkillEnforcer 错误"""
    pass


class SkillNotFoundError(SkillEnforcerError):
    """Skill文件未找到"""
    pass


class SkillLoadError(SkillEnforcerError):
    """Skill加载失败"""
    pass


class SkillEnforcer:
    """Skill强制加载检查器"""
    
    REQUIRED_SKILLS = {
        "requirements_review": "oc_collab_requirements_review_guide",
        "development": "oc_collab_development_guide",
        "testing": "oc_collab_test_acceptance_guide",
        "deployment": "oc_collab_deployment_guide",
    }
    
    def __init__(self, skills_dir: Optional[str] = None):
        """
        初始化 SkillEnforcer
        
        Args:
            skills_dir: Skill目录路径，默认为项目根目录/skills
        """
        self.skills_dir = Path(skills_dir) if skills_dir else Path.cwd() / "skills"
    
    def check_required_skills(self, phase: str) -> Tuple[bool, List[str]]:
        """
        检查指定阶段需要的Skill是否已加载
        
        Args:
            phase: 当前阶段
            
        Returns:
            (是否全部加载, 未加载的Skill列表)
        """
        if phase not in self.REQUIRED_SKILLS:
            return True, []
        
        skill_name = self.REQUIRED_SKILLS[phase]
        skill_path = self.skills_dir / skill_name
        
        if not skill_path.exists():
            return False, [skill_name]
        
        return True, []
    
    def get_load_command(self, skill_name: str) -> str:
        """
        获取加载Skill的命令
        
        Args:
            skill_name: Skill名称
            
        Returns:
            加载命令字符串
        """
        return f"skill load {skill_name}"
    
    def list_loaded_skills(self) -> list[str]:
        """
        列出已加载的Skill
        
        Returns:
            已加载的Skill列表
        """
        if not self.skills_dir.exists():
            return []
        
        loaded = []
        for item in self.skills_dir.iterdir():
            if item.is_dir():
                content_file = item / "content.md"
                if content_file.exists():
                    loaded.append(item.name)
        return loaded
    
    def list_missing_skills(self) -> list[str]:
        """
        列出缺失的Skill
        
        Returns:
            缺失的Skill列表
        """
        missing = []
        for phase, skill_name in self.REQUIRED_SKILLS.items():
            skill_path = self.skills_dir / skill_name
            if not skill_path.exists():
                missing.append(skill_name)
        return missing
