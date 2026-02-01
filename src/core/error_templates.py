"""错误消息格式化模块。

功能：
1. 将技术错误转为用户友好提示
2. 提供错误模板和修复建议
3. 支持多语言错误消息
"""
import logging
import re
from typing import Dict, Optional, List
from enum import Enum


logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """错误类别。"""
    GIT = "git"
    YAML = "yaml"
    FILE = "file"
    PERMISSION = "permission"
    NETWORK = "network"
    STATE = "state"
    UNKNOWN = "unknown"


class ErrorTemplate:
    """错误模板。"""
    
    def __init__(
        self,
        pattern: str,
        friendly_message: str,
        suggestion: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN
    ):
        self.pattern = pattern
        self.friendly_message = friendly_message
        self.suggestion = suggestion
        self.category = category
    
    def match(self, error_message: str) -> bool:
        """检查错误消息是否匹配。"""
        return bool(re.search(self.pattern, error_message, re.IGNORECASE))


class ErrorMessageFormatter:
    """错误消息格式化器。"""
    
    def __init__(self):
        """初始化错误模板。"""
        self.templates: List[ErrorTemplate] = []
        self._register_default_templates()
    
    def _register_default_templates(self):
        """注册默认错误模板。"""
        self.templates = [
            ErrorTemplate(
                pattern=r"git (fetch|pull|push|clone)",
                friendly_message="Git 操作失败",
                suggestion="请检查网络连接和 Git 仓库权限，然后重试。",
                category=ErrorCategory.GIT
            ),
            ErrorTemplate(
                pattern=r"not a git repository",
                friendly_message="当前目录不是 Git 仓库",
                suggestion="请在项目根目录执行 git 操作，或使用 'git init' 初始化仓库。",
                category=ErrorCategory.GIT
            ),
            ErrorTemplate(
                pattern=r"could not read.*username",
                friendly_message="无法读取 Git 用户名",
                suggestion="请配置 Git 用户信息: git config --global user.name 'Your Name'",
                category=ErrorCategory.GIT
            ),
            ErrorTemplate(
                pattern=r"yaml|YAML",
                friendly_message="YAML 格式错误",
                suggestion="请检查 YAML 文件的缩进和格式，确保使用空格而非 Tab。",
                category=ErrorCategory.YAML
            ),
            ErrorTemplate(
                pattern=r"permission denied|access denied",
                friendly_message="权限不足",
                suggestion="请检查文件或目录的访问权限，必要时使用 chmod 调整。",
                category=ErrorCategory.PERMISSION
            ),
            ErrorTemplate(
                pattern=r"file not found|no such file",
                friendly_message="文件不存在",
                suggestion="请检查文件路径是否正确，文件是否已被移动或删除。",
                category=ErrorCategory.FILE
            ),
            ErrorTemplate(
                pattern=r"connection refused|network is unreachable",
                friendly_message="网络连接失败",
                suggestion="请检查网络连接，确保可以访问远程服务器。",
                category=ErrorCategory.NETWORK
            ),
            ErrorTemplate(
                pattern=r"state.*version|invalid.*version",
                friendly_message="State 版本不兼容",
                suggestion="请使用 StateMigrator 迁移到最新版本。",
                category=ErrorCategory.STATE
            ),
            ErrorTemplate(
                pattern=r"timeout",
                friendly_message="操作超时",
                suggestion="请稍后重试，如果问题持续，请检查系统负载。",
                category=ErrorCategory.NETWORK
            ),
        ]
    
    def format(self, error: Exception or str, context: Optional[Dict] = None) -> Dict:
        """格式化错误消息。
        
        Args:
            error: 错误对象或错误消息字符串
            context: 错误上下文信息
            
        Returns:
            Dict: 包含 friendly_message, suggestion, category, original_message
        """
        error_message = str(error)
        
        for template in self.templates:
            if template.match(error_message):
                return {
                    "friendly_message": template.friendly_message,
                    "suggestion": template.suggestion,
                    "category": template.category.value,
                    "original_message": error_message,
                    "context": context or {}
                }
        
        return {
            "friendly_message": "发生了未知错误",
            "suggestion": "请检查错误信息并重试，或联系技术支持。",
            "category": ErrorCategory.UNKNOWN.value,
            "original_message": error_message,
            "context": context or {}
        }
    
    def format_simple(self, error: Exception or str) -> str:
        """简单格式化（返回用户友好消息）。"""
        result = self.format(error)
        return f"{result['friendly_message']}\n建议: {result['suggestion']}"
    
    def add_template(self, pattern: str, friendly_message: str, suggestion: str, category: ErrorCategory = ErrorCategory.UNKNOWN):
        """添加自定义错误模板。"""
        self.templates.append(ErrorTemplate(pattern, friendly_message, suggestion, category))
    
    def get_categories(self) -> List[str]:
        """获取所有错误类别。"""
        return [t.category.value for t in self.templates]


class UserFacingError(Exception):
    """用户友好错误。"""
    
    def __init__(self, message: str, suggestion: str = "", category: str = "unknown"):
        super().__init__(message)
        self.suggestion = suggestion
        self.category = category
    
    def __str__(self):
        result = super().__str__()
        if self.suggestion:
            result += f"\n建议: {self.suggestion}"
        return result


def format_git_error(error: Exception or str) -> Dict:
    """格式化 Git 错误。"""
    formatter = ErrorMessageFormatter()
    return formatter.format(error)


def format_yaml_error(error: Exception or str) -> Dict:
    """格式化 YAML 错误。"""
    formatter = ErrorMessageFormatter()
    result = formatter.format(error)
    result["friendly_message"] = f"YAML 错误: {result['friendly_message']}"
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    formatter = ErrorMessageFormatter()
    
    test_errors = [
        Exception("git fetch failed: connection refused"),
        Exception("File not found: /path/to/file.yaml"),
        Exception("Permission denied: cannot write to /data"),
        Exception("YAML parse error: mapping values"),
        Exception("Unknown error occurred"),
    ]
    
    print("错误消息格式化测试:\n")
    for error in test_errors:
        result = formatter.format(error)
        print(f"原文: {error}")
        print(f"友好: {result['friendly_message']}")
        print(f"建议: {result['suggestion']}")
        print(f"类别: {result['category']}")
        print("-" * 50)
