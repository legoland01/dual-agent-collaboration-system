"""包完整性测试。

测试用例：
- 必要文件检查
- 依赖验证
- 模块导入测试
"""
import pytest
import os
import sys
from pathlib import Path


class TestPackageCompleteness:
    """包完整性测试。"""
    
    REQUIRED_FILES = [
        "pyproject.toml",
        "README.md",
        "src/__init__.py",
        "src/cli/__init__.py",
        "src/core/__init__.py",
        "src/utils/__init__.py",
    ]
    
    REQUIRED_CORE_FILES = [
        "src/core/state_validator.py",
        "src/core/state_migrator.py",
        "src/core/exception_handler.py",
        "src/core/monitor.py",
        "src/core/git_workflow_enforcer.py",
    ]
    
    REQUIRED_CLI_FILES = [
        "src/cli/main.py",
    ]
    
    REQUIRED_DOCS = [
        "README.md",
    ]
    
    def test_required_package_files_exist(self):
        """测试必要包文件存在。"""
        for file_path in self.REQUIRED_FILES:
            assert os.path.exists(file_path), f"必要文件缺失: {file_path}"
    
    def test_required_core_files_exist(self):
        """测试核心模块文件存在。"""
        for file_path in self.REQUIRED_CORE_FILES:
            assert os.path.exists(file_path), f"核心模块文件缺失: {file_path}"
    
    def test_required_cli_files_exist(self):
        """测试 CLI 模块文件存在。"""
        for file_path in self.REQUIRED_CLI_FILES:
            assert os.path.exists(file_path), f"CLI 模块文件缺失: {file_path}"
    
    def test_required_docs_exist(self):
        """测试文档文件存在。"""
        for doc_path in self.REQUIRED_DOCS:
            assert os.path.exists(doc_path), f"文档文件缺失: {doc_path}"
    
    def test_src_init_files_exist(self):
        """测试所有 src 子目录的 __init__.py 存在。"""
        src_path = Path("src")
        if src_path.exists():
            for item in src_path.rglob("__init__.py"):
                assert item.exists(), f"__init__.py 缺失: {item}"
    
    def test_tests_directory_exists(self):
        """测试 tests 目录存在。"""
        assert os.path.exists("tests"), "tests 目录缺失"
    
    def test_tests_have_init(self):
        """测试 tests 目录有 __init__.py。"""
        tests_init = Path("tests/__init__.py")
        assert tests_init.exists(), "tests/__init__.py 缺失"


class TestModuleImports:
    """模块导入测试。"""
    
    def test_import_state_validator(self):
        """测试导入 state_validator 模块。"""
        from src.core.state_validator import StateValidator
        assert StateValidator is not None
    
    def test_import_state_migrator(self):
        """测试导入 state_migrator 模块。"""
        from src.core.state_migrator import StateMigrator
        assert StateMigrator is not None
    
    def test_import_exception_handler(self):
        """测试导入 exception_handler 模块。"""
        from src.core.exception_handler import ExceptionHandler
        assert ExceptionHandler is not None
    
    def test_import_monitor(self):
        """测试导入 monitor 模块。"""
        from src.core.monitor import ResourceMonitor, AlertLevel
        assert ResourceMonitor is not None
        assert AlertLevel is not None
    
    def test_import_git_workflow_enforcer(self):
        """测试导入 git_workflow_enforcer 模块。"""
        from src.core.git_workflow_enforcer import GitWorkflowEnforcer
        assert GitWorkflowEnforcer is not None
    
    def test_import_all_core_modules(self):
        """测试导入所有核心模块。"""
        from src.core import (
            state_validator,
            state_migrator,
            exception_handler,
            monitor,
            git_workflow_enforcer
        )
        assert state_validator is not None
        assert state_migrator is not None
        assert exception_handler is not None
        assert monitor is not None
        assert git_workflow_enforcer is not None


class TestCoreModuleFunctionality:
    """核心模块功能测试。"""
    
    def test_state_validator_initialization(self):
        """测试 StateValidator 初始化。"""
        from src.core.state_validator import StateValidator
        validator = StateValidator()
        assert validator is not None
        assert hasattr(validator, 'validate')
        assert hasattr(validator, 'is_valid')
    
    def test_state_migrator_initialization(self):
        """测试 StateMigrator 初始化。"""
        from src.core.state_migrator import StateMigrator
        migrator = StateMigrator("state/project_state.yaml")
        assert migrator is not None
        assert hasattr(migrator, 'migrate')
    
    def test_exception_handler_initialization(self):
        """测试 ExceptionHandler 初始化。"""
        from src.core.exception_handler import ExceptionHandler
        handler = ExceptionHandler(agent_id="test")
        assert handler is not None
        assert hasattr(handler, 'handle_exception')
    
    def test_monitor_initialization(self):
        """测试 ResourceMonitor 初始化。"""
        from src.core.monitor import ResourceMonitor
        monitor = ResourceMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'get_current_stats')
        assert hasattr(monitor, 'check_thresholds')
    
    def test_git_workflow_enforcer_initialization(self):
        """测试 GitWorkflowEnforcer 初始化。"""
        from src.core.git_workflow_enforcer import GitWorkflowEnforcer
        enforcer = GitWorkflowEnforcer()
        assert enforcer is not None
        assert hasattr(enforcer, 'verify_git_pull')


class TestDependencyValidation:
    """依赖验证测试。"""
    
    def test_click_available(self):
        """测试 click 依赖可用。"""
        import click
        assert click is not None
    
    def test_pyyaml_available(self):
        """测试 pyyaml 依赖可用。"""
        import yaml
        assert yaml is not None
    
    def test_jinja2_available(self):
        """测试 jinja2 依赖可用。"""
        import jinja2
        assert jinja2 is not None
    
    def test_rich_available(self):
        """测试 rich 依赖可用。"""
        import rich
        assert rich is not None
    
    def test_inquirer_available(self):
        """测试 inquirer 依赖可用。"""
        import inquirer
        assert inquirer is not None
    
    def test_psutil_available(self):
        """测试 psutil 依赖可用（用于监控）。"""
        import psutil
        assert psutil is not None


class TestProjectStructure:
    """项目结构测试。"""
    
    def test_project_has_readme(self):
        """测试项目有 README。"""
        readme = Path("README.md")
        assert readme.exists()
        assert readme.stat().st_size > 0
    
    def test_project_has_license(self):
        """测试项目有 LICENSE（推荐但不强制）。"""
        license_file = Path("LICENSE")
        if license_file.exists():
            assert license_file.stat().st_size > 0
    
    def test_project_has_gitignore(self):
        """测试项目有 .gitignore。"""
        gitignore = Path(".gitignore")
        assert gitignore.exists()
    
    def test_pyproject_is_valid(self):
        """测试 pyproject.toml 有效。"""
        import tomli
        with open("pyproject.toml", "rb") as f:
            data = tomli.load(f)
        assert "project" in data
        assert "tool" in data
    
    def test_src_directory_structure(self):
        """测试 src 目录结构。"""
        src = Path("src")
        assert src.exists()
        assert src.is_dir()
        
        expected_dirs = ["cli", "core", "utils"]
        for dir_name in expected_dirs:
            dir_path = src / dir_name
            assert dir_path.exists(), f"目录缺失: src/{dir_name}"
            assert dir_path.is_dir()


class TestStateDirectory:
    """状态目录测试。"""
    
    def test_state_directory_exists(self):
        """测试 state 目录存在。"""
        state_dir = Path("state")
        if state_dir.exists():
            assert state_dir.is_dir()
    
    def test_project_state_template_exists(self):
        """测试项目状态模板存在。"""
        state_file = Path("state/project_state.yaml")
        if state_file.exists():
            assert state_file.stat().st_size > 0


class TestScriptsDirectory:
    """脚本目录测试。"""
    
    def test_scripts_directory_exists(self):
        """测试 scripts 目录存在。"""
        scripts_dir = Path("scripts")
        if scripts_dir.exists():
            assert scripts_dir.is_dir()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
