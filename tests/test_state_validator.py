"""StateValidator 单元测试。

测试用例：
- version 格式验证
- project 字段验证
- requirements 字段验证
- design 字段验证
- 兼容性检测
- 错误信息完整性
"""
import pytest
import tempfile
import os
from pathlib import Path

from src.core.state_validator import StateValidator, ValidationLevel, ValidationResult


class TestStateValidatorVersion:
    """version 字段验证测试。"""

    def test_valid_version(self):
        """测试有效版本号。"""
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{"version": "v1", "status": "approved"}],
            "design": [{"version": "v1", "status": "completed"}],
            "test": {"status": "pending"},
            "development": {"status": "in_progress"},
            "deployment": {"status": "pending"}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        version_errors = [r for r in results if r.field == "version"]
        assert len(version_errors) == 0, f"不应有版本错误: {version_errors}"

    def test_invalid_version_missing(self):
        """测试缺失版本号。"""
        state = {
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        version_errors = [r for r in results if r.field == "version"]
        assert len(version_errors) == 1
        assert version_errors[0].level == ValidationLevel.ERROR

    def test_invalid_version_format(self):
        """测试错误版本格式。"""
        state = {
            "version": "invalid",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        version_errors = [r for r in results if r.field == "version"]
        assert len(version_errors) == 1
        assert version_errors[0].level == ValidationLevel.ERROR


class TestStateValidatorProject:
    """project 字段验证测试。"""

    def test_valid_project(self):
        """测试有效 project。"""
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        # project.name 缺失警告是预期的
        project_errors = [r for r in results if r.field == "project"]
        assert len(project_errors) == 0

    def test_missing_project(self):
        """测试缺失 project。"""
        state = {
            "version": "2.0.0",
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        project_errors = [r for r in results if r.field == "project"]
        assert len(project_errors) == 1
        assert project_errors[0].level == ValidationLevel.ERROR

    def test_invalid_phase(self):
        """测试无效 phase。"""
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "invalid_phase"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        phase_errors = [r for r in results if r.field == "project.phase"]
        assert len(phase_errors) == 1


class TestStateValidatorRequirements:
    """requirements 字段验证测试。"""

    def test_valid_requirements_list(self):
        """测试有效 requirements 列表格式。"""
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{"version": "v1", "status": "approved"}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        req_errors = [r for r in results if r.field == "requirements"]
        assert len(req_errors) == 0

    def test_missing_requirements(self):
        """测试缺失 requirements。"""
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        req_errors = [r for r in results if r.field == "requirements"]
        assert len(req_errors) == 1


class TestStateValidatorDesign:
    """design 字段验证测试。"""

    def test_valid_design_list(self):
        """测试有效 design 列表格式。"""
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{"version": "v1", "status": "completed"}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        design_errors = [r for r in results if r.field == "design"]
        assert len(design_errors) == 0

    def test_design_dict_format_warning(self):
        """测试 design 字典格式（应警告）。"""
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": {"status": "completed"},
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        # 字典格式应该被检测到
        design_results = [r for r in results if r.field == "design"]
        assert len(design_results) >= 1


class TestStateValidatorCompatibility:
    """兼容性检测测试。"""

    def test_check_compatibility_design_list(self):
        """测试 design 列表格式兼容性。"""
        state = {
            "version": "2.0.0",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{"version": "v1", "status": "completed"}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        issues = validator.check_compatibility(state)
        
        # 列表格式应该被识别
        assert len(issues) >= 1

    def test_check_compatibility_phase_in_root(self):
        """测试 phase 在根级的兼容性。"""
        state = {
            "version": "1.0",
            "phase": "development",
            "project": {"name": "Test", "type": "PYTHON"},
            "requirements": {},
            "design": {},
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        issues = validator.check_compatibility(state)
        
        # 应该检测到 phase 在根级的问题
        phase_issues = [r for r in issues if "phase" in r.field.lower()]
        assert len(phase_issues) >= 1


class TestStateValidatorErrorMessages:
    """错误信息完整性测试。"""

    def test_error_has_suggestion(self):
        """测试错误信息包含建议。"""
        state = {
            "version": "invalid",
            "project": {"name": "Test", "type": "PYTHON", "phase": "development"},
            "requirements": [{}],
            "design": [{}],
            "test": {},
            "development": {},
            "deployment": {}
        }
        
        validator = StateValidator()
        results = validator.validate(state)
        
        for result in results:
            if result.level == ValidationLevel.ERROR:
                # 错误应该有建议
                assert result.suggestion, f"错误 {result.field} 缺少建议"


class TestStateValidatorEdgeCases:
    """边界情况测试。"""

    def test_empty_state(self):
        """测试空 state。"""
        state = {}
        
        validator = StateValidator()
        results = validator.validate(state)
        
        # 应该检测到多个错误
        assert len(results) >= 3

    def test_is_valid_method(self):
        """测试 is_valid() 方法。"""
        validator = StateValidator()
        
        # 空 state 应该无效（未验证过）
        assert validator.is_valid() is False
        
        # 有效 state 应该有效
        validator._validated = True
        validator.results = []
        assert validator.is_valid() is True

    def test_get_errors_method(self):
        """测试 get_errors() 方法。"""
        state = {"version": "invalid"}
        
        validator = StateValidator()
        validator.validate(state)
        
        errors = validator.get_errors()
        assert len(errors) >= 1
        assert all(e.level == ValidationLevel.ERROR for e in errors)

    def test_get_warnings_method(self):
        """测试 get_warnings() 方法。"""
        state = {"version": "2.0.0"}
        
        validator = StateValidator()
        validator.validate(state)
        
        warnings = validator.get_warnings()
        assert all(w.level == ValidationLevel.WARNING for w in warnings)


class TestValidationResult:
    """ValidationResult 类测试。"""

    def test_to_dict(self):
        """测试 to_dict() 方法。"""
        result = ValidationResult(
            level=ValidationLevel.ERROR,
            field="test.field",
            message="错误信息",
            suggestion="修复建议"
        )
        
        data = result.to_dict()
        
        assert data["level"] == "error"
        assert data["field"] == "test.field"
        assert data["message"] == "错误信息"
        assert data["suggestion"] == "修复建议"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
