from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class InitResult:
    """初始化结果"""
    success: bool = False
    created_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class RulesInitializer:
    """规则初始化器"""

    CORE_FILES = [
        ("AGENTS.md", "核心协作规则"),
        ("skills/oc_collab_deployment_guide/content.md", "部署指南"),
        ("skills/oc_collab_development_guide/content.md", "开发指南"),
        ("skills/oc_collab_requirements_guide/content.md", "需求指南"),
        ("skills/oc_collab_outline_design_guide/content.md", "概要设计指南"),
        ("skills/oc_collab_detailed_design_guide/content.md", "详细设计指南"),
    ]

    CORE_DIRS = [
        ("skills/", "Skill目录"),
        ("docs/00-memos/", "备忘录目录"),
    ]

    def __init__(self, project_path: Optional[str] = None):
        """初始化规则初始化器

        Args:
            project_path: 项目路径，默认当前目录
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()

    def init(self, force: bool = False) -> InitResult:
        """执行规则初始化

        Args:
            force: 是否强制覆盖已存在的文件

        Returns:
            初始化结果
        """
        result = InitResult()

        for dir_path, description in self.CORE_DIRS:
            full_path = self.project_path / dir_path
            if full_path.exists():
                logger.info(f"目录已存在，跳过: {dir_path}")
                result.skipped_files.append(dir_path)
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                result.created_files.append(dir_path)
                logger.info(f"创建目录: {dir_path}")

        for filename, description in self.CORE_FILES:
            file_path = self.project_path / filename

            if file_path.exists():
                if force:
                    logger.warning(f"强制覆盖: {filename}")
                    self._create_placeholder(file_path, description)
                    result.created_files.append(filename)
                else:
                    logger.info(f"文件已存在，跳过: {filename}")
                    result.skipped_files.append(filename)
            else:
                self._create_placeholder(file_path, description)
                result.created_files.append(filename)
                logger.info(f"创建文件: {filename}")

        result.success = len(result.errors) == 0
        return result

    def _create_placeholder(self, file_path: Path, description: str):
        """创建占位符文件"""
        placeholder_content = f"""# {file_path.name}

> 此文件由 `oc-collab rules init` 自动生成

## 说明

{description}

## 待办

- [ ] 完善此文件内容
"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(placeholder_content, encoding='utf-8')

    def check_status(self) -> dict:
        """检查规则初始化状态"""
        status = {
            "initialized": [],
            "missing": []
        }

        for filename, _ in self.CORE_FILES:
            file_path = self.project_path / filename
            if file_path.exists():
                status["initialized"].append(filename)
            else:
                status["missing"].append(filename)

        for dir_path, _ in self.CORE_DIRS:
            full_path = self.project_path / dir_path
            if full_path.exists():
                status["initialized"].append(dir_path)
            else:
                status["missing"].append(dir_path)

        return status

    def reset(self, force: bool = False) -> InitResult:
        """重置规则（删除已初始化的文件）"""
        from pathlib import Path
        import shutil

        result = InitResult()

        if not force:
            logger.warning("重置需要 --force 参数")
            result.errors.append("需要 --force 参数")
            return result

        for filename, _ in self.CORE_FILES:
            file_path = self.project_path / filename
            if file_path.exists():
                file_path.unlink()
                result.created_files.append(f"[已删除] {filename}")
                logger.info(f"已删除: {filename}")

        for dir_path, _ in self.CORE_DIRS:
            dir_path = self.project_path / dir_path
            if dir_path.exists():
                shutil.rmtree(dir_path)
                result.created_files.append(f"[已删除] {dir_path}/")
                logger.info(f"已删除目录: {dir_path}")

        result.success = True
        return result
