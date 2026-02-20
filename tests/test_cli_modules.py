"""CLI模块测试"""

import pytest
import click
from click.testing import CliRunner
import tempfile
import os
from pathlib import Path
import json


class TestBugCommands:
    """Bug命令测试"""

    def test_bug_group(self):
        """测试bug命令组"""
        from src.cli.bug_commands import bug_group
        assert bug_group.name == "bug"

    def test_bug_link_command(self):
        """测试bug link命令"""
        from src.cli.bug_commands import bug_link
        runner = CliRunner()
        result = runner.invoke(bug_link, ["BUG-001", "test_file.py"])
        assert result.exit_code == 0

    def test_bug_list_command(self):
        """测试bug list命令"""
        from src.cli.bug_commands import bug_list
        runner = CliRunner()
        result = runner.invoke(bug_list)
        assert result.exit_code == 0

    def test_bug_list_unlinked(self):
        """测试bug list --unlinked命令"""
        from src.cli.bug_commands import bug_list
        runner = CliRunner()
        result = runner.invoke(bug_list, ["--unlinked"])
        assert result.exit_code == 0

    def test_bug_suggest_command(self):
        """测试bug suggest命令"""
        from src.cli.bug_commands import bug_suggest
        runner = CliRunner()
        result = runner.invoke(bug_suggest, ["--description", "test bug"])
        assert result.exit_code == 0

    def test_bug_suggest_no_params(self):
        """测试bug suggest无参数"""
        from src.cli.bug_commands import bug_suggest
        runner = CliRunner()
        result = runner.invoke(bug_suggest)
        assert "请提供" in result.output or result.exit_code == 0


class TestCheckCommands:
    """Check命令测试"""

    def test_check_group(self):
        """测试check命令组"""
        from src.cli.check_commands import check_group
        assert check_group.name is not None


class TestConfigCommands:
    """Config命令测试"""

    def test_config_command(self):
        """测试config命令"""
        from src.cli.config_commands import config
        assert config.name == "config"


class TestRequirementsCommands:
    """Requirements命令测试"""

    def test_requirements_command(self):
        """测试requirements命令"""
        from src.cli.requirements_commands import requirements_group
        assert requirements_group.name is not None


class TestAutoUpgrade:
    """自动升级模块测试"""

    def test_get_installed_version(self):
        """测试获取已安装版本"""
        from src.cli.auto_upgrade import get_installed_version
        result = get_installed_version()
        assert isinstance(result, str)

    def test_get_latest_version_from_pypi(self):
        """测试从PyPI获取最新版本"""
        from src.cli.auto_upgrade import get_latest_version_from_pypi
        result = get_latest_version_from_pypi()
        assert result is None or isinstance(result, str)

    def test_should_upgrade(self):
        """测试是否应该升级"""
        from src.cli.auto_upgrade import should_upgrade
        result = should_upgrade()
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_check_only(self):
        """测试仅检查版本"""
        from src.cli.auto_upgrade import check_only
        result = check_only()
        assert isinstance(result, tuple)
        assert len(result) == 3


class TestTodoCommands:
    """TODO命令测试"""

    def test_todo_group(self):
        """测试todo命令组"""
        from src.cli.todo_commands import todo_group
        assert todo_group.name == "todo"

    def test_todo_list(self):
        """测试todo list命令"""
        from src.cli.todo_commands import todo_list_command
        runner = CliRunner()
        result = runner.invoke(todo_list_command, ["--help"])
        assert result.exit_code == 0


class TestAgentCommands:
    """Agent命令测试"""

    def test_agent_command(self):
        """测试agent命令"""
        from src.cli.agent_commands import agent_group
        assert agent_group.name is not None
