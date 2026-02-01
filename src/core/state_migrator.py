"""State 版本迁移器。

功能：
1. 将旧版本的 state 文件迁移到新版本
2. 支持 v1.0 → v2.0 → v2.1 的迁移
3. 迁移前自动备份
4. 验证迁移完整性
"""
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import yaml


logger = logging.getLogger(__name__)


class StateMigrator:
    """State 版本迁移器。"""
    
    # 支持的迁移路径
    MIGRATION_PATHS = {
        "1.0": ["2.0"],
        "1.1": ["2.0"],
        "2.0": ["2.1"],
    }
    
    CURRENT_VERSION = "2.1.0"
    
    def __init__(
        self,
        state_path: str,
        backup_dir: Optional[str] = None,
        dry_run: bool = False
    ):
        """初始化迁移器。
        
        Args:
            state_path: State 文件路径
            backup_dir: 备份目录 (默认: state/backups)
            dry_run: 演练模式，不实际修改文件
        """
        self.state_path = Path(state_path)
        self.backup_dir = Path(backup_dir) if backup_dir else self.state_path.parent / "backups"
        self.dry_run = dry_run
        
        # 创建备份目录
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def get_current_version(self, state: Dict[str, Any]) -> str:
        """获取当前版本号。"""
        return state.get("version", "1.0")
    
    def needs_migration(self, state: Dict[str, Any]) -> bool:
        """检查是否需要迁移。"""
        current_version = self.get_current_version(state)
        return current_version != self.CURRENT_VERSION
    
    def migrate(self, state: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """执行迁移。
        
        Args:
            state: State 字典
            
        Returns:
            (是否成功, 迁移后的状态或错误信息)
        """
        if not self.needs_migration(state):
            return True, state
        
        current_version = self.get_current_version(state)
        
        logger.info(f"开始迁移: {current_version} → {self.CURRENT_VERSION}")
        
        # 备份原始状态
        if not self.dry_run:
            self._create_backup(state)
        
        migrated_state = state.copy()
        
        # 执行迁移
        # v1.x → v2.0
        if current_version in ["1.0", "1.1"]:
            migrated_state = self._migrate_v1_to_v2(migrated_state)
            current_version = "2.0"
        
        # v2.0 → v2.1
        if current_version == "2.0":
            migrated_state = self._migrate_v2_to_v2_1(migrated_state)
            current_version = "2.1"
        
        # 更新版本号
        migrated_state["version"] = self.CURRENT_VERSION
        
        # 验证迁移结果
        is_valid, error = self._validate_migration(state, migrated_state)
        if not is_valid:
            logger.error(f"迁移验证失败: {error}")
            if not self.dry_run:
                self._rollback(state)
            return False, {"error": error}
        
        logger.info(f"迁移成功: {self.CURRENT_VERSION}")
        
        return True, migrated_state
    
    def migrate_file(self, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """迁移 State 文件。
        
        Args:
            output_path: 输出路径 (默认: 覆盖原文件)
            
        Returns:
            (是否成功, 消息)
        """
        # 读取原始状态
        if not self.state_path.exists():
            return False, f"文件不存在: {self.state_path}"
        
        with open(self.state_path, 'r') as f:
            state = yaml.safe_load(f)
        
        # 执行迁移
        success, result = self.migrate(state)
        
        if not success:
            return False, result.get("error", "迁移失败")
        
        # 保存迁移结果
        output = output_path or str(self.state_path)
        
        if not self.dry_run:
            with open(output, 'w') as f:
                yaml.dump(result, f, allow_unicode=True, sort_keys=False)
            
            logger.info(f"已保存迁移结果: {output}")
        
        return True, f"迁移成功: {result['version']}"
    
    def _migrate_v1_to_v2(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """v1.x → v2.0 迁移。"""
        logger.info("执行迁移: v1.x → v2.0")
        
        migrated = state.copy()
        
        # 1. phase 从根级迁移到 project.phase
        if "phase" in migrated:
            if "project" not in migrated:
                migrated["project"] = {}
            
            # 只有 project.phase 为空时才迁移
            if not migrated["project"].get("phase"):
                migrated["project"]["phase"] = migrated.pop("phase")
                logger.info("  ✓ phase 迁移到 project.phase")
        
        # 2. requirements 从字典转为列表
        if "requirements" in migrated:
            old_req = migrated["requirements"]
            if isinstance(old_req, dict):
                migrated["requirements"] = [{
                    "version": old_req.get("version", ""),
                    "status": old_req.get("status", "pending"),
                    "pm_signoff": old_req.get("pm_signoff", False),
                    "dev_signoff": old_req.get("dev_signoff", False)
                }]
                logger.info("  ✓ requirements 转换为列表格式")
        
        # 3. design 从字典转为列表
        if "design" in migrated:
            old_design = migrated["design"]
            if isinstance(old_design, dict):
                migrated["design"] = [{
                    "version": old_design.get("version", "v1"),
                    "status": old_design.get("status", "pending"),
                    "pm_signoff": old_design.get("pm_signoff", False),
                    "dev_signoff": old_design.get("dev_signoff", False),
                    "document": old_design.get("document", ""),
                    "review_document": old_design.get("review_document", "")
                }]
                logger.info("  ✓ design 转换为列表格式")
        
        # 4. 添加 history 字段（如果不存在）
        if "history" not in migrated:
            migrated["history"] = [{
                "id": "migration_v1_to_v2",
                "timestamp": datetime.now().isoformat(),
                "action": "migration",
                "agent_id": "system",
                "details": "从 v1.x 迁移到 v2.0"
            }]
        
        migrated["version"] = "2.0"
        
        return migrated
    
    def _migrate_v2_to_v2_1(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """v2.0 → v2.1 迁移。"""
        logger.info("执行迁移: v2.0 → v2.1")
        
        migrated = state.copy()
        
        # 1. 添加 agent_constraints 字段
        if "agent_constraints" not in migrated:
            migrated["agent_constraints"] = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "agent1": {
                    "role": "产品经理",
                    "allowed_actions": [
                        "CREATE_REQUIREMENTS",
                        "REVIEW_DESIGN",
                        "EXECUTE_BLACKBOX_TEST",
                        "CONFIRM_DEPLOYMENT",
                        "SIGN_OFF"
                    ],
                    "forbidden_actions": [
                        "CREATE_DESIGN",
                        "WRITE_CODE",
                        "EXECUTE_WHITEBOX_TEST",
                        "UPLOAD_PYPI"
                    ]
                },
                "agent2": {
                    "role": "开发",
                    "allowed_actions": [
                        "REVIEW_REQUIREMENTS",
                        "CREATE_DESIGN",
                        "WRITE_CODE",
                        "EXECUTE_WHITEBOX_TEST",
                        "UPLOAD_PYPI",
                        "SUPLEMENT_REQUIREMENTS"
                    ],
                    "forbidden_actions": [
                        "CREATE_REQUIREMENTS",
                        "SIGN_OFF_REQUIREMENTS",
                        "CONFIRM_DEPLOYMENT"
                    ]
                }
            }
            logger.info("  ✓ 添加 agent_constraints 字段")
        
        # 2. 添加 iteration 字段（如果不存在且 project.phase 存在）
        if "iteration" not in migrated and "project" in migrated:
            phase = migrated["project"].get("phase", "unknown")
            migrated["iteration"] = {
                "current": "v2.1.0",
                "start_date": datetime.now().isoformat(),
                "status": phase
            }
            logger.info("  ✓ 添加 iteration 字段")
        
        # 3. 添加 history 记录
        if "history" not in migrated:
            migrated["history"] = []
        
        migrated["history"].insert(0, {
            "id": "migration_v2_to_v2_1",
            "timestamp": datetime.now().isoformat(),
            "action": "migration",
            "agent_id": "system",
            "details": "从 v2.0 迁移到 v2.1"
        })
        
        migrated["version"] = "2.1"
        
        return migrated
    
    def _create_backup(self, state: Dict[str, Any]):
        """创建备份。"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"state_{timestamp}.yaml"
        
        with open(backup_file, 'w') as f:
            yaml.dump(state, f, allow_unicode=True, sort_keys=False)
        
        logger.info(f"已创建备份: {backup_file}")
        
        # 清理旧备份（保留最近 10 个）
        backups = sorted(self.backup_dir.glob("state_*.yaml"))
        for old_backup in backups[:-10]:
            old_backup.unlink()
            logger.info(f"  清理旧备份: {old_backup}")
    
    def _rollback(self, original_state: Dict[str, Any]):
        """回滚到原始状态。"""
        backup_files = sorted(self.backup_dir.glob("state_*.yaml"))
        
        if backup_files:
            latest_backup = backup_files[-1]
            
            with open(latest_backup, 'r') as f:
                backup_state = yaml.safe_load(f)
            
            with open(self.state_path, 'w') as f:
                yaml.dump(backup_state, f, allow_unicode=True, sort_keys=False)
            
            logger.info(f"已回滚到备份: {latest_backup}")
    
    def _validate_migration(
        self,
        original: Dict[str, Any],
        migrated: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """验证迁移结果。
        
        Args:
            original: 原始状态
            migrated: 迁移后的状态
            
        Returns:
            (是否有效, 错误消息)
        """
        # 检查版本号
        if migrated.get("version") != self.CURRENT_VERSION:
            return False, f"版本号错误: 期望 {self.CURRENT_VERSION}, 实际 {migrated.get('version')}"
        
        # 检查必填字段
        required_fields = ["project", "requirements", "design", "test", "development", "deployment"]
        for field in required_fields:
            if field not in migrated:
                return False, f"字段缺失: {field}"
        
        # 检查 project.phase
        if "phase" in migrated:
            return False, "phase 应该在 project 下，不应该在根级"
        
        logger.info("迁移验证通过")
        
        return True, None


def migrate_state_file(
    state_path: str,
    backup: bool = True,
    dry_run: bool = False
) -> bool:
    """迁移 State 文件的命令行工具。
    
    Args:
        state_path: State 文件路径
        backup: 是否备份
        dry_run: 演练模式
        
    Returns:
        是否成功
    """
    import sys
    
    migrator = StateMigrator(
        state_path=state_path,
        dry_run=dry_run
    )
    
    # 读取当前状态
    with open(state_path, 'r') as f:
        state = yaml.safe_load(f)
    
    current_version = state.get("version", "unknown")
    
    print("\n" + "=" * 50)
    print("🔄 State 迁移工具")
    print("=" * 50)
    print(f"当前版本: {current_version}")
    print(f"目标版本: {migrator.CURRENT_VERSION}")
    print(f"备份: {'是' if backup else '否'}")
    print(f"演练模式: {'是' if dry_run else '否'}")
    print("=" * 50)
    
    if migrator.needs_migration(state):
        if dry_run:
            print("\n演练模式：以下是将要执行的迁移操作：")
            # 显示迁移步骤
            if current_version in ["1.0", "1.1"]:
                print("  - phase 迁移到 project.phase")
                print("  - requirements 转换为列表格式")
                print("  - design 转换为列表格式")
            if current_version in ["1.0", "1.1", "2.0"]:
                print("  - 添加 agent_constraints 字段")
                print("  - 添加 iteration 字段")
        else:
            success, message = migrator.migrate_file()
            
            if success:
                print(f"\n✅ {message}")
            else:
                print(f"\n❌ 迁移失败: {message}")
                return False
    else:
        print(f"\n✅ 已是最新版本 ({current_version})，无需迁移")
    
    print()
    return True


if __name__ == "__main__":
    import sys
    
    state_path = sys.argv[1] if len(sys.argv) > 1 else "state/project_state.yaml"
    backup = "--no-backup" not in sys.argv
    dry_run = "--dry-run" in sys.argv
    
    migrate_state_file(state_path, backup, dry_run)
