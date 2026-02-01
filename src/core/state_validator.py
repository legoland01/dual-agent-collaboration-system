"""State 结构验证器。

功能：
1. 验证 project_state.yaml 的结构是否符合 Schema
2. 检测 State 文件格式与代码期望是否兼容
3. 提供详细的验证错误信息
"""
from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass, field
import logging


logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """验证级别。"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationResult:
    """验证结果。"""
    
    def __init__(
        self,
        level: ValidationLevel,
        field: str,
        message: str,
        suggestion: str = ""
    ):
        self.level = level
        self.field = field
        self.message = message
        self.suggestion = suggestion
    
    def __str__(self):
        result = f"[{self.level.value.upper()}] {self.field}: {self.message}"
        if self.suggestion:
            result += f"\n  💡 {self.suggestion}"
        return result
    
    def to_dict(self) -> Dict:
        """转换为字典。"""
        return {
            "level": self.level.value,
            "field": self.field,
            "message": self.message,
            "suggestion": self.suggestion
        }


class StateValidator:
    """State 结构验证器。"""
    
    # Schema 定义
    SCHEMA = {
        "version": {
            "type": str,
            "required": True,
            "pattern": r"^\d+\.\d+\.\d+$",
            "error_message": "version 格式不正确，期望格式: X.Y.Z"
        },
        "project": {
            "type": dict,
            "required": True,
            "fields": {
                "name": {
                    "type": str,
                    "required": True,
                    "error_message": "project.name 缺失"
                },
                "type": {
                    "type": str,
                    "required": True,
                    "error_message": "project.type 缺失"
                },
                "phase": {
                    "type": str,
                    "required": True,
                    "enum": ["unknown", "requirements", "design", 
                             "development", "testing", "deployment", 
                             "completed"],
                    "error_message": "project.phase 值无效"
                }
            }
        },
        "requirements": {
            "type": [dict, list],
            "required": True,
            "error_message": "requirements 字段格式不正确"
        },
        "design": {
            "type": [dict, list],
            "required": True,
            "error_message": "design 字段格式不正确"
        },
        "test": {
            "type": dict,
            "required": True,
            "fields": {
                "status": {
                    "type": str,
                    "enum": ["pending", "in_progress", "passed", "failed"],
                    "error_message": "test.status 值无效"
                }
            }
        },
        "development": {
            "type": dict,
            "required": True,
            "fields": {
                "status": {
                    "type": str,
                    "enum": ["pending", "in_progress", "completed"],
                    "error_message": "development.status 值无效"
                }
            }
        },
        "deployment": {
            "type": dict,
            "required": True,
            "fields": {
                "status": {
                    "type": str,
                    "enum": ["pending", "in_progress", "released"],
                    "error_message": "deployment.status 值无效"
                }
            }
        },
        "iteration": {
            "type": dict,
            "required": False,
            "fields": {
                "current": {"type": str, "required": False},
                "status": {"type": str, "required": False}
            }
        },
        "iterations": {
            "type": dict,
            "required": False,
            "error_message": "iterations 应该是字典格式"
        }
    }
    
    def __init__(self, strict_mode: bool = False):
        """初始化验证器。
        
        Args:
            strict_mode: 严格模式，更多验证
        """
        self.strict_mode = strict_mode
        self.results: List[ValidationResult] = []
    
    def validate(self, state: Dict[str, Any]) -> List[ValidationResult]:
        """验证 State 结构。
        
        Args:
            state: State 字典
            
        Returns:
            验证结果列表
        """
        self.results = []
        
        if not isinstance(state, dict):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="root",
                message="State 应该是字典格式",
                suggestion="检查 project_state.yaml 文件格式是否正确"
            ))
            return self.results
        
        # 验证 version
        self._validate_version(state)
        
        # 验证 project
        self._validate_project(state)
        
        # 验证 requirements
        self._validate_field("requirements", state)
        
        # 验证 design
        self._validate_design(state)
        
        # 验证 test
        self._validate_test(state)
        
        # 验证 development
        self._validate_development(state)
        
        # 验证 deployment
        self._validate_deployment(state)
        
        # 验证 iteration
        if "iteration" in state:
            self._validate_iteration(state)
        
        return self.results
    
    def _validate_version(self, state: Dict[str, Any]):
        """验证 version 字段。"""
        if "version" not in state:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="version",
                message="version 字段缺失",
                suggestion="在 state 文件开头添加 version: X.Y.Z"
            ))
            return
        
        version = state["version"]
        
        if not isinstance(version, str):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="version",
                message=f"version 应该是字符串，实际: {type(version)}"
            ))
            return
        
        import re
        if not re.match(r"^\d+\.\d+\.\d+$", version):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="version",
                message=f"version 格式不正确: {version}",
                suggestion="期望格式: X.Y.Z (例如: 2.0.0 或 2.1.0)"
            ))
    
    def _validate_project(self, state: Dict[str, Any]):
        """验证 project 字段。"""
        if "project" not in state:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="project",
                message="project 字段缺失",
                suggestion="添加 project 字段，包含 name、type、phase"
            ))
            return
        
        project = state["project"]
        
        if not isinstance(project, dict):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="project",
                message=f"project 应该是字典格式，实际: {type(project)}"
            ))
            return
        
        # 验证 project.name
        if "name" not in project:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                field="project.name",
                message="project.name 缺失",
                suggestion="添加项目名称"
            ))
        
        # 验证 project.phase
        if "phase" not in project:
            # 检查是否在根级
            if "phase" in state:
                self.results.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field="project.phase",
                    message="phase 在根级而非 project.phase",
                    suggestion="考虑迁移 phase 到 project.phase"
                ))
            else:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field="project.phase",
                    message="project.phase 缺失"
                ))
        else:
            valid_phases = ["unknown", "requirements", "design", 
                           "development", "testing", "deployment", "completed"]
            if project["phase"] not in valid_phases:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field="project.phase",
                    message=f"无效的 phase 值: {project['phase']}",
                    suggestion=f"有效值: {valid_phases}"
                ))
    
    def _validate_field(self, field_name: str, state: Dict[str, Any]):
        """验证通用字段。"""
        schema = self.SCHEMA.get(field_name, {})
        
        if field_name not in state:
            if schema.get("required", False):
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=field_name,
                    message=f"{field_name} 字段缺失"
                ))
            return
        
        value = state[field_name]
        expected_types = schema.get("type", dict)
        
        if isinstance(expected_types, list):
            if not any(isinstance(value, t) for t in expected_types):
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field=field_name,
                    message=f"{field_name} 类型错误，期望: {expected_types}，实际: {type(value)}"
                ))
        elif not isinstance(value, expected_types):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field=field_name,
                message=f"{field_name} 类型错误，期望: {expected_types}，实际: {type(value)}"
            ))
    
    def _validate_design(self, state: Dict[str, Any]):
        """验证 design 字段（处理列表和字典两种格式）。"""
        if "design" not in state:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="design",
                message="design 字段缺失"
            ))
            return
        
        design = state["design"]
        
        # 列表格式
        if isinstance(design, list):
            for i, item in enumerate(design):
                if isinstance(item, dict):
                    if not item.get("version"):
                        self.results.append(ValidationResult(
                            level=ValidationLevel.WARNING,
                            field=f"design[{i}].version",
                            message="设计文档缺少 version 字段"
                        ))
        # 字典格式
        elif isinstance(design, dict):
            # 旧格式兼容
            logger.info("检测到 design 为字典格式，考虑迁移到列表格式")
    
    def _validate_test(self, state: Dict[str, Any]):
        """验证 test 字段。"""
        if "test" not in state:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="test",
                message="test 字段缺失"
            ))
            return
        
        test = state["test"]
        
        if not isinstance(test, dict):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="test",
                message=f"test 应该是字典格式，实际: {type(test)}"
            ))
            return
        
        # 验证 status
        if "status" in test:
            valid_statuses = ["pending", "in_progress", "passed", "failed"]
            if test["status"] not in valid_statuses:
                self.results.append(ValidationResult(
                    level=ValidationLevel.ERROR,
                    field="test.status",
                    message=f"无效的 test.status: {test['status']}",
                    suggestion=f"有效值: {valid_statuses}"
                ))
    
    def _validate_development(self, state: Dict[str, Any]):
        """验证 development 字段。"""
        if "development" not in state:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="development",
                message="development 字段缺失"
            ))
            return
        
        dev = state["development"]
        
        if not isinstance(dev, dict):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="development",
                message=f"development 应该是字典格式，实际: {type(dev)}"
            ))
            return
    
    def _validate_deployment(self, state: Dict[str, Any]):
        """验证 deployment 字段。"""
        if "deployment" not in state:
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="deployment",
                message="deployment 字段缺失"
            ))
            return
        
        deploy = state["deployment"]
        
        if not isinstance(deploy, dict):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="deployment",
                message=f"deployment 应该是字典格式，实际: {type(deploy)}"
            ))
            return
    
    def _validate_iteration(self, state: Dict[str, Any]):
        """验证 iteration 字段。"""
        iteration = state["iteration"]
        
        if not isinstance(iteration, dict):
            self.results.append(ValidationResult(
                level=ValidationLevel.ERROR,
                field="iteration",
                message=f"iteration 应该是字典格式，实际: {type(iteration)}"
            ))
            return
        
        if "current" not in iteration:
            self.results.append(ValidationResult(
                level=ValidationLevel.WARNING,
                field="iteration.current",
                message="iteration.current 缺失"
            ))
    
    def check_compatibility(self, state: Dict[str, Any]) -> List[ValidationResult]:
        """检测 State 文件格式与代码期望是否兼容。
        
        Args:
            state: State 字典
            
        Returns:
            兼容性问题列表
        """
        issues = []
        
        # 检测 design 字段类型
        if "design" in state:
            design = state["design"]
            if isinstance(design, list):
                issues.append(ValidationResult(
                    level=ValidationLevel.INFO,
                    field="design",
                    message="design 字段是列表格式",
                    suggestion="代码已兼容列表格式，无需修改"
                ))
            elif isinstance(design, dict):
                issues.append(ValidationResult(
                    level=ValidationLevel.WARNING,
                    field="design",
                    message="design 字段是字典格式，建议迁移到列表格式",
                    suggestion="使用 StateMigrator.migrate_v1_to_v2() 迁移"
                ))
        
        # 检测 phase 位置
        if "phase" in state:
            issues.append(ValidationResult(
                level=ValidationLevel.WARNING,
                field="phase",
                message="phase 在根级，建议迁移到 project.phase",
                suggestion="使用 StateMigrator.migrate_v1_to_v2() 迁移"
            ))
        
        return issues
    
    def is_valid(self) -> bool:
        """检查是否有错误级别的验证结果。"""
        return not any(r.level == ValidationLevel.ERROR for r in self.results)
    
    def get_errors(self) -> List[ValidationResult]:
        """获取所有错误级别的验证结果。"""
        return [r for r in self.results if r.level == ValidationLevel.ERROR]
    
    def get_warnings(self) -> List[ValidationResult]:
        """获取所有警告级别的验证结果。"""
        return [r for r in self.results if r.level == ValidationLevel.WARNING]


def validate_state_file(state_path: str) -> bool:
    """验证 State 文件。
    
    Args:
        state_path: State 文件路径
        
    Returns:
        验证是否通过
    """
    import yaml
    
    with open(state_path, 'r') as f:
        state = yaml.safe_load(f)
    
    validator = StateValidator()
    results = validator.validate(state)
    
    # 输出验证结果
    print("\n" + "=" * 50)
    print("🔍 State 结构验证结果")
    print("=" * 50)
    
    if results:
        for result in results:
            print(f"\n{result}")
        
        print("\n" + "-" * 50)
        if validator.is_valid():
            print("✅ 验证通过")
        else:
            print(f"❌ 验证失败，发现 {len(validator.get_errors())} 个错误")
    else:
        print("✅ State 结构有效")
    
    print("=" * 50 + "\n")
    
    return validator.is_valid()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        validate_state_file(sys.argv[1])
    else:
        # 测试验证器
        test_state = {
            "version": "2.0.0",
            "project": {
                "name": "Test Project",
                "type": "PYTHON",
                "phase": "development"
            },
            "design": [{"version": "v1", "status": "completed"}],
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        
        validator = StateValidator()
        results = validator.validate(test_state)
        
        print("测试 State 验证：")
        for r in results:
            print(f"  {r}")
        print(f"\n是否有效: {validator.is_valid()}")
