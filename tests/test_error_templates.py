"""ErrorTemplates 单元测试。"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.error_templates import (
    ErrorCategory,
    ErrorTemplate,
    ErrorMessageFormatter,
    UserFacingError,
    format_git_error,
    format_yaml_error,
)


class TestErrorCategory:
    """错误类别测试。"""

    def test_error_category_values(self):
        """测试错误类别枚举值。"""
        assert ErrorCategory.GIT.value == "git"
        assert ErrorCategory.YAML.value == "yaml"
        assert ErrorCategory.FILE.value == "file"
        assert ErrorCategory.PERMISSION.value == "permission"
        assert ErrorCategory.NETWORK.value == "network"
        assert ErrorCategory.STATE.value == "state"
        assert ErrorCategory.UNKNOWN.value == "unknown"

    def test_all_categories_defined(self):
        """测试所有类别都已定义。"""
        categories = list(ErrorCategory)
        assert len(categories) == 7


class TestErrorTemplate:
    """错误模板测试。"""

    def test_error_template_init(self):
        """测试错误模板初始化。"""
        template = ErrorTemplate(
            pattern=r"test.*error",
            friendly_message="测试错误",
            suggestion="请检查测试代码",
            category=ErrorCategory.GIT
        )
        assert template.pattern == r"test.*error"
        assert template.friendly_message == "测试错误"
        assert template.suggestion == "请检查测试代码"
        assert template.category == ErrorCategory.GIT

    def test_error_template_match_positive(self):
        """测试错误模板匹配（成功）。"""
        template = ErrorTemplate(
            pattern=r"git.*error",
            friendly_message="Git 错误",
            suggestion="检查 Git 配置",
            category=ErrorCategory.GIT
        )
        assert template.match("Git operation error") is True
        assert template.match("GIT ERROR occurred") is True
        assert template.match("This is a git error message") is True

    def test_error_template_match_negative(self):
        """测试错误模板匹配（失败）。"""
        template = ErrorTemplate(
            pattern=r"git.*error",
            friendly_message="Git 错误",
            suggestion="检查 Git 配置",
            category=ErrorCategory.GIT
        )
        assert template.match("This is a file error") is False
        assert template.match("No match here") is False

    def test_error_template_default_category(self):
        """测试错误模板默认类别。"""
        template = ErrorTemplate(
            pattern=r"test",
            friendly_message="测试",
            suggestion="无"
        )
        assert template.category == ErrorCategory.UNKNOWN


class TestErrorMessageFormatter:
    """错误消息格式化器测试。"""

    def test_init(self):
        """测试初始化。"""
        formatter = ErrorMessageFormatter()
        assert len(formatter.templates) > 0

    def test_format_git_error(self):
        """测试格式化 Git 错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("git fetch failed"))
        
        assert result["category"] == ErrorCategory.GIT.value
        assert "Git" in result["friendly_message"]

    def test_format_yaml_error(self):
        """测试格式化 YAML 错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("YAML parse error"))
        
        assert result["category"] == ErrorCategory.YAML.value
        assert "YAML" in result["friendly_message"]

    def test_format_permission_error(self):
        """测试格式化权限错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("Permission denied"))
        
        assert result["category"] == ErrorCategory.PERMISSION.value
        assert "权限" in result["friendly_message"]

    def test_format_file_error(self):
        """测试格式化文件错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("File not found"))
        
        assert result["category"] == ErrorCategory.FILE.value
        assert "文件不存在" in result["friendly_message"]

    def test_format_network_error(self):
        """测试格式化网络错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("Connection refused"))
        
        assert result["category"] == ErrorCategory.NETWORK.value
        assert "网络" in result["friendly_message"]

    def test_format_state_error(self):
        """测试格式化状态错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("state version mismatch"))
        
        assert result["category"] == ErrorCategory.STATE.value
        assert "State" in result["friendly_message"] or "版本" in result["friendly_message"]

    def test_format_timeout_error(self):
        """测试格式化超时错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("Operation timeout"))
        
        assert result["category"] == ErrorCategory.NETWORK.value
        assert "超时" in result["friendly_message"]

    def test_format_unknown_error(self):
        """测试格式化未知错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("Some unknown error xyz"))
        
        assert result["category"] == ErrorCategory.UNKNOWN.value
        assert "未知错误" in result["friendly_message"]

    def test_format_with_context(self):
        """测试格式化带上下文的错误。"""
        formatter = ErrorMessageFormatter()
        context = {"file": "test.py", "line": 42}
        result = formatter.format(Exception("test error"), context=context)
        
        assert result["context"] == context

    def test_format_with_string(self):
        """测试格式化字符串错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format("This is a string error")
        
        assert "original_message" in result
        assert result["original_message"] == "This is a string error"

    def test_format_simple(self):
        """测试简单格式化。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format_simple(Exception("git push failed"))
        
        assert "Git 操作失败" in result
        assert "建议:" in result

    def test_add_template(self):
        """测试添加自定义模板。"""
        formatter = ErrorMessageFormatter()
        initial_count = len(formatter.templates)
        
        formatter.add_template(
            pattern=r"custom.*error",
            friendly_message="自定义错误",
            suggestion="自定义建议",
            category=ErrorCategory.FILE
        )
        
        assert len(formatter.templates) == initial_count + 1
        
        result = formatter.format(Exception("Custom error here"))
        assert result["category"] == ErrorCategory.FILE.value

    def test_get_categories(self):
        """测试获取所有错误类别。"""
        formatter = ErrorMessageFormatter()
        categories = formatter.get_categories()
        
        assert isinstance(categories, list)
        assert len(categories) == len(formatter.templates)
        assert ErrorCategory.GIT.value in categories

    def test_format_git_not_repo(self):
        """测试格式化非 Git 仓库错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("not a git repository"))
        
        assert result["category"] == ErrorCategory.GIT.value
        assert "Git 仓库" in result["friendly_message"]

    def test_format_git_username(self):
        """测试格式化 Git 用户名错误。"""
        formatter = ErrorMessageFormatter()
        result = formatter.format(Exception("could not read Username"))
        
        assert result["category"] == ErrorCategory.GIT.value
        assert "用户名" in result["friendly_message"]

    def test_all_templates_match(self):
        """测试所有默认模板都能正常匹配。"""
        formatter = ErrorMessageFormatter()
        
        test_cases = [
            ("git fetch failed", ErrorCategory.GIT),
            ("not a git repository", ErrorCategory.GIT),
            ("yaml parse error", ErrorCategory.YAML),
            ("Permission denied", ErrorCategory.PERMISSION),
            ("file not found", ErrorCategory.FILE),
            ("connection refused", ErrorCategory.NETWORK),
            ("state version error", ErrorCategory.STATE),
            ("timeout occurred", ErrorCategory.NETWORK),
        ]
        
        for error_msg, expected_category in test_cases:
            result = formatter.format(Exception(error_msg))
            assert result["category"] == expected_category.value, f"Failed for: {error_msg}"


class TestUserFacingError:
    """用户友好错误测试。"""

    def test_init_basic(self):
        """测试基本初始化。"""
        error = UserFacingError("测试错误")
        assert str(error) == "测试错误"
        assert error.suggestion == ""
        assert error.category == "unknown"

    def test_init_with_suggestion(self):
        """测试带建议的初始化。"""
        error = UserFacingError("测试错误", suggestion="请检查代码")
        assert error.suggestion == "请检查代码"

    def test_init_with_category(self):
        """测试带类别的初始化。"""
        error = UserFacingError("测试错误", category="git")
        assert error.category == "git"

    def test_str_with_suggestion(self):
        """测试带建议的字符串表示。"""
        error = UserFacingError("测试错误", suggestion="请重试")
        result = str(error)
        assert "测试错误" in result
        assert "建议: 请重试" in result

    def test_str_without_suggestion(self):
        """测试不带建议的字符串表示。"""
        error = UserFacingError("测试错误")
        result = str(error)
        assert result == "测试错误"


class TestFormatFunctions:
    """格式化函数测试。"""

    def test_format_git_error(self):
        """测试 Git 错误格式化函数。"""
        result = format_git_error(Exception("git push failed"))
        assert "category" in result
        assert result["category"] == ErrorCategory.GIT.value

    def test_format_yaml_error(self):
        """测试 YAML 错误格式化函数。"""
        result = format_yaml_error(Exception("yaml parse error"))
        assert "category" in result
        assert "YAML" in result["friendly_message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestMainBlock:
    """主模块测试。"""

    def test_module_can_be_imported(self):
        """测试模块可以被导入。"""
        from src.core import error_templates
        assert hasattr(error_templates, 'ErrorMessageFormatter')
        assert hasattr(error_templates, 'UserFacingError')
        assert hasattr(error_templates, 'format_git_error')
        assert hasattr(error_templates, 'format_yaml_error')
