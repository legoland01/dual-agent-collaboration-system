"""
TODO迁移工具

将现有TODO迁移到Agent独立编号格式。
"""

from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import yaml
import shutil
import logging

logger = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """迁移结果"""
    source_file: str
    backup_file: str
    migrated_count: int = 0
    conflicts: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def is_success(self) -> bool:
        """是否成功"""
        return len(self.errors) == 0 and self.migrated_count > 0

    def summary(self) -> str:
        """摘要"""
        return f"迁移: {self.migrated_count}个, 错误: {len(self.errors)}个"


class TodoMigrator:
    """TODO编号迁移工具"""

    def __init__(self, source_file: str, backup_file: Optional[str] = None):
        """
        Args:
            source_file: 源YAML文件路径
            backup_file: 备份文件路径，为None则自动生成
        """
        self.source_file = Path(source_file)
        self.backup_file = self._generate_backup_path(backup_file)

    def _generate_backup_path(self, backup_file: Optional[str]) -> Path:
        """生成备份文件路径"""
        if backup_file:
            return Path(backup_file)
        return self.source_file.parent / f"{self.source_file.stem}_backup{self.source_file.suffix}"

    def migrate(self, agent_mapping: dict[str, str]) -> MigrationResult:
        """
        执行迁移

        Args:
            agent_mapping: TODO ID到Agent ID的映射

        Returns:
            MigrationResult: 迁移结果
        """
        result = MigrationResult(
            source_file=str(self.source_file),
            backup_file=str(self.backup_file),
            migrated_count=0,
            conflicts=[],
            errors=[]
        )

        try:
            # 1. 备份
            self._backup(result)

            # 2. 读取现有TODO
            data = self._load_source(result)
            if not data:
                return result

            # 3. 执行迁移
            self._process_todos(data, agent_mapping, result)

            # 4. 保存新格式
            self._save_result(data, result)

        except Exception as e:
            result.errors.append(str(e))
            logger.error(f"迁移过程出错: {e}")

        return result

    def _backup(self, result: MigrationResult):
        """创建备份"""
        try:
            shutil.copy(self.source_file, self.backup_file)
            logger.info(f"备份已创建: {self.backup_file}")
        except Exception as e:
            result.errors.append(f"备份失败: {e}")

    def _load_source(self, result: MigrationResult) -> Optional[dict]:
        """加载源文件"""
        try:
            if not self.source_file.exists():
                result.errors.append(f"源文件不存在: {self.source_file}")
                return None

            with open(self.source_file) as f:
                return yaml.safe_load(f)
        except Exception as e:
            result.errors.append(f"加载源文件失败: {e}")
            return None

    def _process_todos(self, data: dict, agent_mapping: dict[str, str], result: MigrationResult):
        """处理TODO"""
        todos = data.get("todos", [])

        for i, todo in enumerate(todos):
            old_id = todo.get("id", "")
            if old_id in agent_mapping:
                new_id = f"TODO-{agent_mapping[old_id]}-{old_id.split('-')[-1]}"
                todo["id"] = new_id
                result.migrated_count += 1
                logger.info(f"迁移: {old_id} -> {new_id}")

    def _save_result(self, data: dict, result: MigrationResult):
        """保存结果"""
        try:
            with open(self.source_file, "w") as f:
                yaml.dump(data, f, allow_unicode=True)
            logger.info(f"迁移结果已保存: {self.source_file}")
        except Exception as e:
            result.errors.append(f"保存失败: {e}")

    def rollback(self) -> bool:
        """回滚"""
        try:
            if self.backup_file.exists():
                shutil.copy(self.backup_file, self.source_file)
                logger.info(f"已回滚: {self.source_file}")
                return True
            return False
        except Exception as e:
            logger.error(f"回滚失败: {e}")
            return False

    def preview(self, agent_mapping: dict[str, str]) -> list[dict]:
        """
        预览迁移结果

        Args:
            agent_mapping: TODO ID到Agent ID的映射

        Returns:
            list: 预览结果列表
        """
        preview = []
        try:
            with open(self.source_file) as f:
                data = yaml.safe_load(f)

            for todo in data.get("todos", []):
                old_id = todo.get("id", "")
                if old_id in agent_mapping:
                    new_id = f"TODO-{agent_mapping[old_id]}-{old_id.split('-')[-1]}"
                    preview.append({
                        "old_id": old_id,
                        "new_id": new_id,
                        "content": todo.get("content", "")[:50]
                    })
        except Exception as e:
            logger.error(f"预览失败: {e}")

        return preview
