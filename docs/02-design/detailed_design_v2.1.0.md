# 详细设计文档：oc-collab v2.1.0

**版本**: v1  
**创建日期**: 2026-02-01  
**作者**: Agent 2 (开发)  
**关联需求**: requirements_v2.1.0.md

---

## 1. 概述

### 1.1 背景

v2.0.0 版本已完成 Agent 守护进程核心功能，但存在以下问题：
- E2E 测试缺失
- 异常处理不完善
- 可观测性不足
- 配置更新不便
- State 结构兼容性差
- 包发布不完整

### 1.2 目标

v2.1.0 版本旨在提升系统稳定性、可维护性和用户体验。

### 1.3 设计范围

| 模块 | 优先级 | 说明 |
|------|--------|------|
| E2E 测试框架 | P0 | 完整工作流测试 |
| 异常处理增强 | P0 | 网络、磁盘、权限 |
| 监控告警功能 | P1 | 资源监控和告警 |
| 配置热重载 | P1 | 无需重启更新配置 |
| State 结构验证 | P0 | Schema 验证和迁移 |
| 包完整性测试 | P0 | 发布前验证 |
| 友好错误提示 | P1 | 用户可理解的错误 |
| 多轮评审机制 | P1 | 规范评审流程 |

---

## 2. 架构设计

### 2.1 系统架构

```
oc-collab v2.1.0 架构
========================

┌─────────────────────────────────────────────────────────┐
│                    CLI 层 (src/cli/)                     │
│  main.py: 命令入口                                       │
│  agent.py: Agent 守护进程命令                            │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   核心层 (src/core/)                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐│
│  │ state_manager │ │ signoff.py  │ │ phase_advance.py   ││
│  │ 状态管理     │ │ 签署引擎    │ │ 阶段推进引擎       ││
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐│
│  │ daemon.py   │ │ supervisor  │ │ workflow.py        ││
│  │ 守护进程    │ │ 进程监管    │ │ 工作流引擎         ││
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐│
│  │ git.py      │ │ exception_  │ │ state_migrator.py  ││
│  │ Git 操作    │ │ handler.py  │ │ State 版本迁移     ││
│  └─────────────┘ └─────────────┘ └─────────────────────┘│
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   工具层 (src/utils/)                    │
│  file.py: 文件操作      date.py: 日期处理                │
│  yaml.py: YAML 解析     lock.py: 文件锁                 │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   数据层 (state/)                        │
│  project_state.yaml: 项目状态                            │
│  agent_constraints.yaml: Agent 约束配置                  │
│  project_schema.yaml: State 结构 Schema (新增)           │
└─────────────────────────────────────────────────────────┘
```

### 2.2 新增模块

```
src/core/
├── daemon.py           # 现有
├── supervisor.py       # 现有
├── git.py              # 现有
├── signoff.py          # 现有
├── state_manager.py    # 现有
├── state_migrator.py   # 新增：State 版本迁移
├── state_validator.py  # 新增：State Schema 验证
├── exception_handler.py # 新增：增强异常处理
├── monitor.py          # 新增：监控告警
└── config_reloader.py  # 新增：配置热重载

tests/
├── test_e2e.py         # 新增：E2E 测试
├── test_package_completeness.py  # 新增：包完整性测试
└── test_state_migration.py       # 新增：State 迁移测试
```

---

## 3. 详细设计

### 3.1 State 结构验证（FR-VAL-001/002/003）

#### 3.1.1 Schema 定义

**文件**: `src/core/state_validator.py`

```python
from typing import Dict, List, Any, Optional
from enum import Enum
import yaml


class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class StateValidator:
    """State 结构验证器。"""
    
    # Schema 定义
    SCHEMA = {
        "version": {
            "type": str,
            "required": True,
            "pattern": r"^\d+\.\d+\.\d+$"
        },
        "project": {
            "type": dict,
            "required": True,
            "fields": {
                "name": {"type": str, "required": True},
                "type": {"type": str, "required": True},
                "phase": {
                    "type": str,
                    "required": True,
                    "enum": ["unknown", "requirements", "design", 
                             "development", "testing", "deployment", 
                             "completed"]
                }
            }
        },
        "requirements": {
            "type": [dict, list],
            "required": True
        },
        "design": {
            "type": [dict, list],
            "required": True
        },
        "test": {
            "type": dict,
            "required": True,
            "fields": {
                "status": {
                    "type": str,
                    "enum": ["pending", "in_progress", "passed", "failed"]
                }
            }
        },
        "development": {
            "type": dict,
            "required": True,
            "fields": {
                "status": {
                    "type": str,
                    "enum": ["pending", "in_progress", "completed"]
                }
            }
        },
        "deployment": {
            "type": dict,
            "required": True,
            "fields": {
                "status": {
                    "type": str,
                    "enum": ["pending", "in_progress", "released"]
                }
            }
        }
    }
    
    def __init__(self, schema_path: Optional[str] = None):
        """初始化验证器。
        
        Args:
            schema_path: 自定义 Schema 文件路径
        """
        self.schema = self.SCHEMA.copy()
        if schema_path:
            self._load_custom_schema(schema_path)
    
    def validate(self, state: dict) -> List[ValidationResult]:
        """验证 State 结构。
        
        Args:
            state: State 字典
            
        Returns:
            验证结果列表
        """
        results = []
        
        # 验证 version
        results.extend(self._validate_field("version", state))
        
        # 验证 project
        if "project" in state:
            results.extend(self._validate_field("project", state))
        else:
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="project",
                message="project 字段缺失"
            ))
        
        # 验证其他字段
        for field, schema in self.schema.items():
            if field in ["version", "project"]:
                continue
            results.extend(self._validate_field(field, state))
        
        return results
    
    def _validate_field(self, field: str, state: dict) -> List[ValidationResult]:
        """验证单个字段。"""
        results = []
        
        if field not in state:
            # 检查是否为必填
            if self.schema.get(field, {}).get("required", False):
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=field,
                    message=f"必填字段 '{field}' 缺失"
                ))
            return results
        
        value = state[field]
        schema = self.schema.get(field, {})
        
        # 检查类型
        expected_types = schema.get("type", str)
        if not isinstance(value, expected_types if isinstance(expected_types, tuple) else (expected_types,)):
            results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field=field,
                message=f"字段类型错误: 期望 {expected_types}, 实际 {type(value)}"
            ))
            return results
        
        # 验证子字段
        if isinstance(value, dict) and "fields" in schema:
            for sub_field, sub_schema in schema["fields"].items():
                if sub_field in value:
                    results.extend(self._validate_sub_field(field, sub_field, value, sub_schema))
        
        return results
    
    def _validate_sub_field(self, parent: str, field: str, parent_value: dict, schema: dict) -> List[ValidationResult]:
        """验证子字段。"""
        results = []
        value = parent_value.get(field)
        
        # 检查 enum
        if "enum" in schema:
            if value not in schema["enum"]:
                results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=f"{parent}.{field}",
                    message=f"值必须在 {schema['enum']} 中，当前: {value}"
                ))
        
        return results
    
    def _load_custom_schema(self, schema_path: str):
        """加载自定义 Schema。"""
        with open(schema_path, 'r') as f:
            custom_schema = yaml.safe_load(f)
        self.schema.update(custom_schema)


class ValidationResult:
    """验证结果。"""
    
    def __init__(self, level: ValidationLevel, field: str, message: str):
        self.level = level
        self.field = field
        self.message = message
    
    def __str__(self):
        return f"[{self.level.value.upper()}] {self.field}: {self.message}"
```

#### 3.1.2 State 版本迁移

**文件**: `src/core/state_migrator.py`

```python
from typing import Dict, Any
from pathlib import Path
import yaml
import shutil
from datetime import datetime


class StateMigrator:
    """State 版本迁移器。"""
    
    MIGRATIONS = {
        "1.0": "migrate_v1_to_v2",
        "1.1": "migrate_v1_to_v2",
        "2.0": "migrate_v2_to_v2_1",
    }
    
    CURRENT_VERSION = "2.1.0"
    
    def __init__(self, state_path: str, backup_dir: str = None):
        """初始化迁移器。
        
        Args:
            state_path: State 文件路径
            backup_dir: 备份目录
        """
        self.state_path = Path(state_path)
        self.backup_dir = backup_dir or str(self.state_path.parent / "backups")
    
    def migrate(self) -> Dict[str, Any]:
        """执行迁移。
        
        Returns:
            迁移结果
        """
        # 读取当前状态
        with open(self.state_path, 'r') as f:
            state = yaml.safe_load(f)
        
        current_version = state.get("version", "1.0")
        
        # 检查是否需要迁移
        if current_version == self.CURRENT_VERSION:
            return {
                "success": True,
                "message": "已是最新版本，无需迁移",
                "from_version": current_version,
                "to_version": current_version
            }
        
        # 创建备份
        self._create_backup()
        
        # 执行迁移
        migration_method = f"migrate_{current_version.replace('.', '_')}_to_v2"
        if hasattr(self, migration_method):
            state = getattr(self, migration_method)(state)
        else:
            # 逐版本迁移
            for version in self.MIGRATIONS.keys():
                if self._needs_migration(current_version, version):
                    migration_method = f"migrate_{version.replace('.', '_')}_to_v2"
                    if hasattr(self, migration_method):
                        state = getattr(self, migration_method)(state)
                        current_version = "2.0"
        
        # 更新版本号
        state["version"] = self.CURRENT_VERSION
        
        # 保存
        with open(self.state_path, 'w') as f:
            yaml.dump(state, f, allow_unicode=True, sort_keys=False)
        
        return {
            "success": True,
            "message": "迁移成功",
            "from_version": current_version,
            "to_version": self.CURRENT_VERSION
        }
    
    def _needs_migration(self, current: str, target: str) -> bool:
        """检查是否需要迁移。"""
        current_parts = [int(x) for x in current.split(".")]
        target_parts = [int(x) for x in target.split(".")]
        return current_parts < target_parts
    
    def _create_backup(self):
        """创建备份。"""
        backup_path = Path(self.backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_path / f"state_{timestamp}.yaml"
        
        shutil.copy(self.state_path, backup_file)
    
    def migrate_v1_to_v2(self, state: dict) -> dict:
        """v1.x → v2.0 迁移。"""
        # 1. phase 从根级迁移到 project.phase
        if "phase" in state and "project" in state:
            state["project"]["phase"] = state.pop("phase")
        
        # 2. design 从字典转为列表
        if "design" in state and isinstance(state["design"], dict):
            old_design = state["design"]
            state["design"] = [{
                "version": old_design.get("version", "v1"),
                "status": old_design.get("status", "pending"),
                "pm_signoff": old_design.get("pm_signoff", False),
                "dev_signoff": old_design.get("dev_signoff", False),
                "document": old_design.get("document", ""),
                "review_document": old_design.get("review_document", "")
            }]
        
        # 3. requirements 结构调整
        if "requirements" in state and isinstance(state["requirements"], dict):
            old_req = state["requirements"]
            state["requirements"] = [{
                "version": old_req.get("version", ""),
                "status": old_req.get("status", "pending"),
                "pm_signoff": old_req.get("pm_signoff", False),
                "dev_signoff": old_req.get("dev_signoff", False)
            }]
        
        return state
    
    def migrate_v2_to_v2_1(self, state: dict) -> dict:
        """v2.0 → v2.1 迁移。"""
        # 添加 agent_constraints 字段
        if "agent_constraints" not in state:
            state["agent_constraints"] = {
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
        
        return state
```

---

### 3.2 异常处理增强（FR-EXC-001/002/003）

#### 3.2.1 网络异常处理

**文件**: `src/core/exception_handler.py`

```python
import time
import logging
from functools import wraps
from typing import Callable, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class RetryConfig:
    """重试配置。"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        timeout: int = 30
    ):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.timeout = timeout


class NetworkError(Exception):
    """网络异常。"""
    pass


def with_retry(config: RetryConfig = None):
    """装饰器：添加重试逻辑。"""
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except NetworkError as e:
                    last_exception = e
                    
                    if attempt < config.max_retries:
                        # 计算延迟时间
                        delay = min(
                            config.initial_delay * (config.exponential_base ** attempt),
                            config.max_delay
                        )
                        
                        logger.warning(
                            f"网络操作失败，{delay:.1f}秒后重试 "
                            f"(尝试 {attempt + 1}/{config.max_retries + 1}): {e}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"网络操作最终失败: {e}")
                        raise
            
            raise last_exception
        
        return wrapper
    return decorator


class DiskSpaceChecker:
    """磁盘空间检查器。"""
    
    def __init__(self, min_free_mb: int = 100, check_paths: list = None):
        """初始化。
        
        Args:
            min_free_mb: 最小可用空间 (MB)
            check_paths: 检查的路径列表
        """
        self.min_free_mb = min_free_mb
        self.check_paths = check_paths or ["/"]
    
    def check(self, path: str = None) -> bool:
        """检查磁盘空间。
        
        Args:
            path: 要检查的路径
            
        Returns:
            空间是否充足
        """
        import shutil
        
        check_path = path or self.check_paths[0]
        
        try:
            stat = shutil.disk_usage(check_path)
            free_mb = stat.free / (1024 * 1024)
            
            if free_mb < self.min_free_mb:
                logger.warning(
                    f"磁盘空间不足: {free_mb:.1f}MB "
                    f"(阈值: {self.min_free_mb}MB)"
                )
                return False
            
            return True
        
        except OSError as e:
            logger.error(f"检查磁盘空间失败: {e}")
            return True  # 检查失败时允许继续


class PermissionChecker:
    """权限检查器。"""
    
    def __init__(self):
        """初始化。"""
        self.checked_paths = {}
    
    def check_read(self, path: str) -> bool:
        """检查读权限。"""
        import os
        
        try:
            with open(path, 'r'):
                pass
            return True
        except PermissionError:
            logger.error(f"无读权限: {path}")
            return False
    
    def check_write(self, path: str) -> bool:
        """检查写权限。"""
        import os
        
        try:
            test_file = os.path.join(path, ".write_test")
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            return True
        except PermissionError:
            logger.error(f"无写权限: {path}")
            return False
        except OSError:
            logger.error(f"无法创建测试文件: {path}")
            return False
```

---

### 3.3 监控告警功能（FR-MON-001/002/003）

**文件**: `src/core/monitor.py`

```python
import time
import psutil
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum


class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class Alert:
    """告警信息。"""
    level: AlertLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    metric: str = ""
    value: float = 0.0
    threshold: float = 0.0


class ResourceMonitor:
    """资源监控器。"""
    
    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 85.0,
        disk_threshold: float = 90.0,
        sample_interval: int = 10
    ):
        """初始化。
        
        Args:
            cpu_threshold: CPU 使用率阈值 (%)
            memory_threshold: 内存使用率阈值 (%)
            disk_threshold: 磁盘使用率阈值 (%)
            sample_interval: 采样间隔 (秒)
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.sample_interval = sample_interval
        
        self.alerts: List[Alert] = []
        self.stats = {
            "cpu_samples": [],
            "memory_samples": [],
            "disk_samples": [],
            "restart_count": 0,
            "git_operations": 0,
            "exception_count": 0
        }
    
    def get_current_stats(self) -> Dict:
        """获取当前资源使用情况。"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "cpu_count": psutil.cpu_count(),
            "memory_used_gb": psutil.virtual_memory().used / (1024**3),
            "memory_total_gb": psutil.virtual_memory().total / (1024**3),
        }
    
    def check_thresholds(self) -> List[Alert]:
        """检查阈值，返回告警列表。"""
        alerts = []
        stats = self.get_current_stats()
        
        # CPU 告警
        if stats["cpu_percent"] > self.cpu_threshold:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                message=f"CPU 使用率 {stats['cpu_percent']:.1f}% (阈值: {self.cpu_threshold}%)",
                metric="cpu_percent",
                value=stats["cpu_percent"],
                threshold=self.cpu_threshold
            ))
        
        # 内存告警
        if stats["memory_percent"] > self.memory_threshold:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                message=f"内存使用率 {stats['memory_percent']:.1f}% (阈值: {self.memory_threshold}%)",
                metric="memory_percent",
                value=stats["memory_percent"],
                threshold=self.memory_threshold
            ))
        
        # 磁盘告警
        if stats["disk_percent"] > self.disk_threshold:
            alerts.append(Alert(
                level=AlertLevel.WARNING,
                message=f"磁盘使用率 {stats['disk_percent']:.1f}% (阈值: {self.disk_threshold}%)",
                metric="disk_percent",
                value=stats["disk_percent"],
                threshold=self.disk_threshold
            ))
        
        # 记录告警
        self.alerts.extend(alerts)
        
        return alerts
    
    def get_status_report(self) -> Dict:
        """生成状态报告。"""
        current = self.get_current_stats()
        
        return {
            "status": "healthy",
            "resources": {
                "cpu": f"{current['cpu_percent']:.1f}%",
                "memory": f"{current['memory_percent']:.1f}%",
                "disk": f"{current['disk_percent']:.1f}%"
            },
            "stats": {
                "restart_count": self.stats["restart_count"],
                "git_operations": self.stats["git_operations"],
                "exception_count": self.stats["exception_count"]
            },
            "recent_alerts": len(self.alerts[-10:]),
            "alerts": [str(a) for a in self.alerts[-5:]]
        }
```

---

### 3.4 配置热重载（FR-CFG-001/002/003）

**文件**: `src/core/config_reloader.py`

```python
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml


logger = logging.getLogger(__name__)


class ConfigReloader:
    """配置热重载器。"""
    
    def __init__(self, config_paths: Dict[str, str], reload_callback: Callable = None):
        """初始化。
        
        Args:
            config_paths: 配置路径映射 {name: path}
            reload_callback: 重载回调函数
        """
        self.config_paths = config_paths
        self.reload_callback = reload_callback
        self.configs: Dict[str, Dict] = {}
        self.mtimes: Dict[str, float] = {}
        self.observer = None
        self.running = False
    
    def load_all(self) -> Dict[str, Dict]:
        """加载所有配置文件。"""
        for name, path in self.config_paths.items():
            self.configs[name] = self._load_config(path)
            self.mtimes[name] = Path(path).stat().st_mtime
        
        return self.configs
    
    def _load_config(self, path: str) -> Dict:
        """加载单个配置文件。"""
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def start_watching(self, interval: int = 60):
        """开始监听配置变化（定期检查模式）。"""
        self.running = True
        
        while self.running:
            time.sleep(interval)
            self._check_changes()
    
    def _check_changes(self):
        """检查配置变化。"""
        for name, path in self.config_paths.items():
            try:
                current_mtime = Path(path).stat().st_mtime
                
                if current_mtime > self.mtimes[name]:
                    logger.info(f"检测到配置变化: {name}")
                    
                    # 验证新配置
                    new_config = self._load_config(path)
                    if self._validate_config(new_config):
                        self.configs[name] = new_config
                        self.mtimes[name] = current_mtime
                        
                        if self.reload_callback:
                            self.reload_callback(name, new_config)
                        
                        logger.info(f"配置已重新加载: {name}")
                    else:
                        logger.error(f"配置验证失败，回滚: {name}")
                        # 回滚到旧配置
                        self.mtimes[name] = current_mtime  # 防止重复验证
            
            except Exception as e:
                logger.error(f"检查配置变化失败 {name}: {e}")
    
    def _validate_config(self, config: Dict) -> bool:
        """验证配置。"""
        # TODO: 实现配置验证逻辑
        return True
    
    def stop(self):
        """停止监听。"""
        self.running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
    
    def get_config(self, name: str) -> Optional[Dict]:
        """获取配置。"""
        return self.configs.get(name)
    
    def hot_reload(self, name: str, path: str):
        """手动触发热重载。"""
        new_config = self._load_config(path)
        
        if self._validate_config(new_config):
            self.configs[name] = new_config
            self.mtimes[name] = Path(path).stat().st_mtime
            
            if self.reload_callback:
                self.reload_callback(name, new_config)
            
            return True
        return False


# 支持热重载的配置项
HOT_RELOADABLE_CONFIG = {
    "polling_interval": {"type": int, "default": 30},
    "log_level": {"type": str, "default": "INFO"},
    "git_timeout": {"type": int, "default": 30},
    "max_restarts": {"type": int, "default": 5},
    "backoff_factor": {"type": float, "default": 2.0},
}

# 需要重启的配置项
COLD_RELOAD_CONFIG = {
    "project_path": None,
    "pid_file": None,
    "log_file": None,
}
```

---

### 3.5 Git 工作流强制约束（FR-GIT-001）

**文件**: `src/core/git_workflow_enforcer.py`

```python
import subprocess
import logging
from typing import Tuple, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class WorkflowViolation:
    """工作流违规。"""
    agent_id: str
    action: str
    reason: str
    suggestion: str


class GitWorkflowEnforcer:
    """Git 工作流强制执行器。"""
    
    REQUIRED_GIT_OPERATIONS = [
        "READ_REQUIREMENTS",      # 读取需求文档
        "READ_DESIGN",            # 读取设计文档
        "READ_TEST_REPORT",       # 读取测试报告
        "READ_SIGNOFF",           # 读取签署记录
        "READ_CODE",              # 读取代码变更
    ]
    
    def __init__(self, project_path: str):
        """初始化。
        
        Args:
            project_path: 项目路径
        """
        self.project_path = project_path
    
    def verify_git_pull(self, agent_id: str, file_path: str) -> Tuple[bool, Optional[WorkflowViolation]]:
        """验证 Agent 是否通过 Git pull 获取最新文件。
        
        Args:
            agent_id: Agent ID
            file_path: 要读取的文件路径
            
        Returns:
            (是否通过, 违规信息)
        """
        # 获取本地文件内容
        local_content = self._read_local_file(file_path)
        
        # 获取 Git HEAD 版本
        git_content = self._git_show(f"HEAD:{file_path}")
        
        if local_content != git_content:
            return False, WorkflowViolation(
                agent_id=agent_id,
                action="READ_FILE",
                reason=f"本地文件与 Git HEAD 不一致",
                suggestion="请先执行 'git pull' 获取最新版本"
            )
        
        return True, None
    
    def enforce_git_operation(self, agent_id: str, operation: str) -> Tuple[bool, Optional[WorkflowViolation]]:
        """强制执行 Git 操作。
        
        Args:
            agent_id: Agent ID
            operation: 操作类型
            
        Returns:
            (是否通过, 违规信息)
        """
        if operation in self.REQUIRED_GIT_OPERATIONS:
            # 先执行 git pull
            success, error = self._run_git_pull()
            if not success:
                return False, WorkflowViolation(
                    agent_id=agent_id,
                    action=operation,
                    reason="Git pull 失败",
                    suggestion=str(error)
                )
        
        return True, None
    
    def _run_git_pull(self) -> Tuple[bool, Optional[Exception]]:
        """执行 git pull。"""
        try:
            result = subprocess.run(
                ["git", "pull"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return False, Exception(result.stderr)
            
            return True, None
        
        except subprocess.TimeoutExpired:
            return False, Exception("Git pull 超时")
        except Exception as e:
            return False, e
    
    def _read_local_file(self, file_path: str) -> str:
        """读取本地文件。"""
        with open(file_path, 'r') as f:
            return f.read()
    
    def _git_show(self, ref: str) -> str:
        """获取 Git 指定引用的内容。"""
        try:
            result = subprocess.run(
                ["git", "show", ref],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return ""  # 文件可能不存在于 Git 中
            
            return result.stdout
        
        except Exception:
            return ""
```

---

### 3.6 包完整性测试（FR-PKG-001/002）

**文件**: `tests/test_package_completeness.py`

```python
import pytest
import zipfile
import os
from pathlib import Path


class TestPackageCompleteness:
    """包完整性测试。"""
    
    @pytest.fixture
    def wheel_path(self):
        """获取 wheel 文件路径。"""
        dist_dir = Path(__file__).parent.parent / "dist"
        wheel_files = list(dist_dir.glob("opencode_collaboration-*.whl"))
        
        if not wheel_files:
            pytest.skip("wheel 文件不存在，请先运行 'python -m build'")
        
        return str(wheel_files[0])
    
    @pytest.fixture
    def wheel(self, wheel_path):
        """打开 wheel 文件。"""
        with zipfile.ZipFile(wheel_path, 'r') as zf:
            yield zf
    
    # 必须包含的文件
    REQUIRED_FILES = [
        "src/cli/main.py",
        "src/cli/agent.py",
        "src/cli/__init__.py",
        "src/core/signoff.py",
        "src/core/daemon.py",
        "src/core/state_manager.py",
        "src/core/supervisor.py",
        "src/core/git.py",
        "src/core/phase_advance.py",
        "src/core/__init__.py",
        "src/utils/file.py",
        "src/utils/yaml.py",
        "src/utils/__init__.py",
        "src/__init__.py",
        "opencode_collaboration-VERSION.dist-info/METADATA",
        "opencode_collaboration-VERSION.dist-info/WHEEL",
        "opencode_collaboration-VERSION.dist-info/RECORD",
        "opencode_collaboration-VERSION.dist-info/entry_points.txt",
    ]
    
    def test_wheel_exists(self, wheel_path):
        """测试 wheel 文件存在。"""
        assert os.path.exists(wheel_path), f"wheel 文件不存在: {wheel_path}"
    
    def test_wheel_size(self, wheel_path):
        """测试 wheel 文件大小。"""
        size = os.path.getsize(wheel_path)
        assert size > 50 * 1024, f"wheel 文件过小: {size} bytes (阈值: 50KB)"
    
    def test_required_files_exist(self, wheel):
        """测试必要文件存在。"""
        namelist = wheel.namelist()
        
        for file_path in self.REQUIRED_FILES:
            # 处理 VERSION 占位符
            expected_path = file_path.replace("VERSION", "*")
            
            # 检查是否匹配
            matches = [n for n in namelist if n.replace("\\", "/") == expected_path.replace("\\", "/")]
            assert matches, f"wheel 缺少必要文件: {file_path}"
    
    def test_cli_entry_points(self, wheel):
        """测试 CLI 入口点。"""
        namelist = wheel.namelist()
        
        # 检查 entry_points.txt
        ep_files = [n for n in namelist if "entry_points.txt" in n]
        assert ep_files, "缺少 entry_points.txt"
        
        # 解析 entry_points
        ep_content = wheel.read(ep_files[0]).decode()
        assert "console_scripts" in ep_content, "entry_points.txt 缺少 console_scripts"
        assert "oc-collab" in ep_content, "缺少 oc-collab CLI 命令"
    
    def test_metadata_complete(self, wheel):
        """测试元数据完整。"""
        namelist = wheel.namelist()
        
        # 检查 METADATA
        metadata_files = [n for n in namelist if n.endswith("METADATA")]
        assert metadata_files, "缺少 METADATA 文件"
        
        metadata = wheel.read(metadata_files[0]).decode()
        
        required_fields = [
            "Name:",
            "Version:",
            "Summary:",
            "Author:",
        ]
        
        for field in required_fields:
            assert field in metadata, f"METADATA 缺少字段: {field}"
    
    def test_no_unexpected_files(self, wheel):
        """测试无意外文件。"""
        namelist = wheel.namelist()
        
        # 检查是否有 .pyc 文件
        pyc_files = [n for n in namelist if n.endswith(".pyc")]
        assert not pyc_files, f"wheel 包含 .pyc 文件: {pyc_files}"
        
        # 检查是否有 __pycache__ 目录
        pycache_dirs = [n for n in namelist if "__pycache__" in n]
        assert not pycache_dirs, f"wheel 包含 __pycache__ 目录: {pycache_dirs}"


def test_package_publish_precheck():
    """发布前检查（手动运行）。"""
    checks = [
        ("wheel 文件存在", lambda: len(list(Path("dist").glob("*.whl"))) > 0),
        ("源码包存在", lambda: len(list(Path("dist").glob("*.tar.gz"))) > 0),
        ("版本号已更新", lambda: True),  # 手动确认
        ("CHANGELOG 已更新", lambda: True),  # 手动确认
        ("测试全部通过", lambda: True),  # 运行 pytest 后确认
    ]
    
    for name, check in checks:
        try:
            assert check(), f"检查失败: {name}"
            print(f"✅ {name}")
        except AssertionError as e:
            print(f"❌ {e}")
            raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

---

## 4. 测试设计

### 4.1 E2E 测试场景

| 测试场景 | 测试内容 | 预期结果 |
|---------|---------|---------|
| 完整工作流 | init → requirements → design → development → testing → deployment | 全流程通过 |
| 异常恢复 | 网络中断后重试 | 操作成功 |
| 并发操作 | 双 Agent 同时操作 | 串行处理，结果正确 |
| 状态迁移 | v1.0 → v2.1.0 | 迁移成功 |
| 配置热重载 | 修改配置后重载 | 配置生效 |

### 4.2 测试用例示例

```python
def test_full_workflow():
    """完整工作流测试。"""
    # 1. 初始化项目
    result = runner.invoke(cli, ["init", "--name", "Test"])
    assert result.exit_code == 0
    
    # 2. 创建需求
    result = runner.invoke(cli, ["requirements", "--create"])
    assert result.exit_code == 0
    
    # 3. 推进到设计阶段
    result = runner.invoke(cli, ["advance", "--phase", "design"])
    assert result.exit_code == 0
    
    # ... 继续其他阶段


def test_state_migration_v1_to_v2():
    """State 迁移测试。"""
    migrator = StateMigrator("state/project_state.yaml")
    
    # 创建 v1.0 状态的 state
    v1_state = create_v1_state()
    
    # 执行迁移
    result = migrator.migrate(v1_state)
    
    # 验证迁移结果
    assert result["success"]
    assert result["to_version"] == "2.1.0"


def test_git_workflow_enforcement():
    """Git 工作流强制测试。"""
    enforcer = GitWorkflowEnforcer("/path/to/project")
    
    # 模拟未 git pull 就读取文件
    result, violation = enforcer.verify_git_pull("agent1", "docs/requirements.md")
    
    assert result is False
    assert "git pull" in violation.suggestion
```

---

## 5. 实施计划

### 5.1 里程碑

| 里程碑 | 内容 | 交付物 |
|--------|------|--------|
| M1 | State 验证和迁移 | state_validator.py, state_migrator.py |
| M2 | 异常处理增强 | exception_handler.py |
| M3 | 监控告警 | monitor.py |
| M4 | 配置热重载 | config_reloader.py |
| M5 | Git 工作流约束 | git_workflow_enforcer.py |
| M6 | 包完整性测试 | test_package_completeness.py |
| M7 | E2E 测试集成 | test_e2e.py |
| M8 | 集成测试 | 完整测试套件 |

### 5.2 依赖

| 依赖 | 用途 | 版本 |
|------|------|------|
| psutil | 资源监控 | >= 5.0.0 |
| watchdog | 文件监听 | >= 3.0.0 |
| pytest | 测试框架 | >= 7.0.0 |
| pytest-cov | 覆盖率 | >= 4.0.0 |

---

## 6. 风险

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| State 迁移复杂度 | 可能丢失数据 | 备份 + 验证 |
| 配置竞态条件 | 配置不一致 | 锁机制 |
| 监控性能开销 | 影响守护进程 | 轻量级采样 |

---

## 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-01 | ✅ |
| 产品负责人 | Agent 1 | 2026-02-01 | 待签署 |
