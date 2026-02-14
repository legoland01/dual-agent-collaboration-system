"""SkillEnforcer: Skill强制加载检查器

FR-SKILL-001: 在CLI命令执行前，强制检查相关Skill是否已加载
"""
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
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
    """Skill强制加载检查器 - v2.2.6增强版"""

    REQUIRED_SKILLS = {
        "requirements_review": "oc_collab_requirements_review_guide",
        "development": "oc_collab_development_guide",
        "testing": "oc_collab_test_acceptance_guide",
        "deployment": "oc_collab_deployment_guide",
        "requirements": "oc_collab_requirements_guide",          # v2.2.6 新增
        "design": "oc_collab_design_guide",                     # v2.2.6 新增
    }

    OPTIONAL_SKILLS = {
        "bug_management": "oc_collab_bug_management_guide",
        "collaboration": "oc_collab_collaboration_guide",
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

    def check_before_action(self, action: str) -> dict:
        """
        行动前检查

        Args:
            action: 行动类型 (如 "todowrite", "signoff", "review")

        Returns:
            检查结果字典
        """
        result = {
            "action": action,
            "required_skills": [],
            "optional_skills": [],
            "missing": [],
            "suggestions": []
        }

        # 根据行动类型确定相关Skill
        skill_mapping = {
            "todowrite": ["requirements", "collaboration"],
            "signoff": ["requirements_review", "development"],
            "review": ["requirements_review"],
            "phase_advance": ["requirements", "design"],
        }

        phases = skill_mapping.get(action, [])

        for phase in phases:
            if phase in self.REQUIRED_SKILLS:
                result["required_skills"].append(self.REQUIRED_SKILLS[phase])

                skill_path = self.skills_dir / self.REQUIRED_SKILLS[phase]
                if not skill_path.exists():
                    result["missing"].append(self.REQUIRED_SKILLS[phase])

            if phase in self.OPTIONAL_SKILLS:
                result["optional_skills"].append(self.OPTIONAL_SKILLS[phase])

        if result["missing"]:
            result["suggestions"].append(
                f"建议加载相关Skill: {'; '.join(result['missing'])}"
            )

        return result


# v2.2.11 新增：增强版Skill强制执行器
# ============================================

class SkillCheckResult:
    """Skill检查结果"""
    def __init__(self, passed: bool, message: str, checked_skills: Optional[List[str]] = None, loaded_skills: Optional[List[str]] = None):
        self.passed = passed
        self.message = message
        self.checked_skills = checked_skills if checked_skills is not None else []
        self.loaded_skills = loaded_skills if loaded_skills is not None else []


class SkillRequiredError(Exception):
    """必需的Skill未遵循异常"""
    def __init__(self, message: str, missing_skills: List[str], required_for: str):
        super().__init__(message)
        self.missing_skills = missing_skills
        self.required_for = required_for


class SkillEnforcerEnhanced:
    """增强版Skill强制执行器 - v2.2.11"""

    def __init__(self, skill_loader: Optional[Any] = None):
        """
        Args:
            skill_loader: Skill加载器
        """
        self.skill_loader = skill_loader
        self.required_skills = self._load_required_skills()

    def _load_required_skills(self) -> Dict[str, List[str]]:
        """加载必需Skill规则"""
        return {
            "todowrite": ["oc_collab_todo_execution"],
            "signoff": ["oc_collab_signoff_guide"],
            "commit": ["oc_collab_git_commit_guide"],
            "skill_slice": ["oc_collab_skill_management_guide"],
            "skill_enforce": ["oc_collab_skill_management_guide"]
        }

    def check(self, command: str) -> SkillCheckResult:
        """
        检查命令是否遵循Skill规范

        Args:
            command: 命令类型 (todowrite/signoff/commit等)

        Returns:
            SkillCheckResult: 检查结果

        Raises:
            SkillRequiredError: 必需的Skill未遵循
        """
        required = self.required_skills.get(command, [])

        if not required:
            return SkillCheckResult(True, f"命令{command}无需Skill检查")

        # 加载当前已加载的Skill
        loaded_skills = self._get_loaded_skills()

        # 检查是否有所需的Skill
        missing = []
        for skill in required:
            if skill not in loaded_skills:
                missing.append(skill)

        if missing:
            raise SkillRequiredError(
                f"执行{command}前必须先加载以下Skill: {', '.join(missing)}",
                missing_skills=missing,
                required_for=command
            )

        return SkillCheckResult(True, "Skill检查通过", required, list(loaded_skills.keys()))

    def _get_loaded_skills(self) -> Dict[str, Any]:
        """获取已加载的Skill"""
        if self.skill_loader:
            return self.skill_loader.get_loaded_skills()
        return {}

    def add_required_skill(self, command: str, skill: str):
        """添加必需Skill规则"""
        if command not in self.required_skills:
            self.required_skills[command] = []
        if skill not in self.required_skills[command]:
            self.required_skills[command].append(skill)

    def remove_required_skill(self, command: str, skill: str):
        """移除必需Skill规则"""
        if command in self.required_skills and skill in self.required_skills[command]:
            self.required_skills[command].remove(skill)
