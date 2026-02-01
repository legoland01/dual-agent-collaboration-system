"""GitWorkflowEnforcer 单元测试。"""
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.git_workflow_enforcer import (
    GitWorkflowEnforcer, WorkflowViolation
)


class TestWorkflowViolation:
    """工作流违规测试。"""

    def test_workflow_violation_creation(self):
        """测试创建工作流违规。"""
        violation = WorkflowViolation(
            agent_id="agent1",
            action="READ_FILE",
            reason="本地文件与Git HEAD不一致",
            suggestion="请先执行 'git pull' 获取最新版本"
        )
        assert violation.agent_id == "agent1"
        assert violation.action == "READ_FILE"
        assert violation.reason == "本地文件与Git HEAD不一致"

    def test_workflow_violation_to_dict(self):
        """测试工作流违规转换为字典。"""
        violation = WorkflowViolation(
            agent_id="agent1",
            action="READ_FILE",
            reason="Test reason",
            suggestion="Test suggestion"
        )
        result = violation.to_dict()
        
        assert result["agent_id"] == "agent1"
        assert result["action"] == "READ_FILE"
        assert result["reason"] == "Test reason"
        assert result["suggestion"] == "Test suggestion"


class TestGitWorkflowEnforcer:
    """Git工作流强制执行器测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def enforcer(self, temp_dir):
        """创建执行器实例。"""
        return GitWorkflowEnforcer(project_path=temp_dir)

    def test_init_default_path(self):
        """测试默认路径初始化。"""
        enforcer = GitWorkflowEnforcer()
        assert enforcer.project_path == Path(".")

    def test_init_custom_path(self, temp_dir):
        """测试自定义路径初始化。"""
        enforcer = GitWorkflowEnforcer(project_path=temp_dir)
        assert enforcer.project_path == Path(temp_dir)

    def test_is_git_repository_true(self, temp_dir):
        """测试是Git仓库。"""
        enforcer = GitWorkflowEnforcer(project_path=temp_dir)
        git_dir = Path(temp_dir) / ".git"
        git_dir.mkdir()
        
        assert enforcer.is_git_repository() is True

    def test_is_git_repository_false(self, temp_dir):
        """测试不是Git仓库。"""
        enforcer = GitWorkflowEnforcer(project_path=temp_dir)
        
        assert enforcer.is_git_repository() is False

    def test_get_git_root_success(self, temp_dir):
        """测试获取Git根目录成功。"""
        enforcer = GitWorkflowEnforcer(project_path=temp_dir)
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/path/to/repo\n"
        
        with patch('subprocess.run', return_value=mock_result):
            root = enforcer.get_git_root()
            
            assert root == Path("/path/to/repo")

    def test_get_git_root_failure(self, temp_dir):
        """测试获取Git根目录失败。"""
        enforcer = GitWorkflowEnforcer(project_path=temp_dir)
        
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        
        with patch('subprocess.run', return_value=mock_result):
            root = enforcer.get_git_root()
            
            assert root is None

    def test_get_git_root_timeout(self, temp_dir):
        """测试获取Git根目录超时。"""
        enforcer = GitWorkflowEnforcer(project_path=temp_dir)
        
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5)):
            root = enforcer.get_git_root()
            
            assert root is None

    def test_verify_git_pull_file_not_exists(self, enforcer):
        """测试验证Git拉取（文件不存在）。"""
        result = enforcer.verify_git_pull("agent1", "nonexistent.txt")
        
        assert result[0] is True
        assert result[1] is None

    def test_verify_git_pull_file_not_in_git(self, enforcer, temp_dir):
        """测试验证Git拉取（文件不在Git中）。"""
        file_path = Path(temp_dir) / "new_file.txt"
        file_path.write_text("new content")
        
        with patch.object(enforcer, '_git_show', return_value=None):
            result = enforcer.verify_git_pull("agent1", "new_file.txt")
            
            assert result[0] is True
            assert result[1] is None

    def test_verify_git_pull_content_match(self, enforcer, temp_dir):
        """测试验证Git拉取（内容匹配）。"""
        file_path = Path(temp_dir) / "test.txt"
        file_path.write_text("same content")
        
        with patch.object(enforcer, '_git_show', return_value="same content"):
            result = enforcer.verify_git_pull("agent1", "test.txt")
            
            assert result[0] is True
            assert result[1] is None

    def test_verify_git_pull_content_mismatch(self, enforcer, temp_dir):
        """测试验证Git拉取（内容不匹配）。"""
        file_path = Path(temp_dir) / "test.txt"
        file_path.write_text("local content")
        
        with patch.object(enforcer, '_git_show', return_value="git content"):
            result = enforcer.verify_git_pull("agent1", "test.txt")
            
            assert result[0] is False
            assert result[1] is not None
            assert result[1].agent_id == "agent1"
            assert result[1].action == "READ_FILE"

    def test_verify_git_status_clean(self, enforcer):
        """测试验证Git状态（干净）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        
        with patch('subprocess.run', return_value=mock_result):
            result = enforcer.verify_git_status("agent1")
            
            assert result[0] is True
            assert result[1] is None

    def test_verify_git_status_dirty(self, enforcer):
        """测试验证Git状态（有更改）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = " M modified.txt\n"
        
        with patch('subprocess.run', return_value=mock_result):
            result = enforcer.verify_git_status("agent1")
            
            assert result[0] is False
            assert result[1] is not None
            assert result[1].agent_id == "agent1"
            assert result[1].action == "GIT_STATUS"

    def test_verify_git_status_timeout(self, enforcer):
        """测试验证Git状态（超时）。"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5)):
            result = enforcer.verify_git_status("agent1")
            
            assert result[0] is False
            assert result[1] is not None
            assert result[1].reason == "Git 命令超时"

    def test_enforce_git_operation_required(self, enforcer):
        """测试强制执行必需Git操作。"""
        with patch.object(enforcer, '_run_git_pull', return_value=(True, None)):
            result = enforcer.enforce_git_operation("agent1", "READ_REQUIREMENTS")
            
            assert result[0] is True

    def test_enforce_git_operation_not_required(self, enforcer):
        """测试强制执行非必需Git操作。"""
        result = enforcer.enforce_git_operation("agent1", "WRITE_FILE")
        
        assert result[0] is True
        assert result[1] is None

    def test_enforce_git_operation_pull_failed(self, enforcer):
        """测试强制执行Git操作（拉取失败）。"""
        with patch.object(enforcer, '_run_git_pull', return_value=(False, "network error")):
            result = enforcer.enforce_git_operation("agent1", "READ_REQUIREMENTS")
            
            assert result[0] is False
            assert result[1] is not None
            assert "Git pull 失败" in result[1].reason

    def test_required_git_operations(self, enforcer):
        """测试必需的Git操作列表。"""
        assert "READ_REQUIREMENTS" in enforcer.REQUIRED_GIT_OPERATIONS
        assert "READ_DESIGN" in enforcer.REQUIRED_GIT_OPERATIONS
        assert "READ_TEST_REPORT" in enforcer.REQUIRED_GIT_OPERATIONS
        assert "READ_SIGNOFF" in enforcer.REQUIRED_GIT_OPERATIONS
        assert "READ_CODE" in enforcer.REQUIRED_GIT_OPERATIONS

    def test_run_git_pull_success(self, enforcer):
        """测试运行Git拉取成功。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            success, error = enforcer._run_git_pull()
            
            assert success is True
            assert error is None

    def test_run_git_pull_failure(self, enforcer):
        """测试运行Git拉取失败。"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "error: could not pull"
        
        with patch('subprocess.run', return_value=mock_result):
            success, error = enforcer._run_git_pull()
            
            assert success is False
            assert error is not None

    def test_run_git_pull_timeout(self, enforcer):
        """测试运行Git拉取超时。"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git pull", timeout=30)):
            success, error = enforcer._run_git_pull()
            
            assert success is False
            assert error is not None

    def test_git_show_success(self, enforcer):
        """测试Git显示文件成功。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "file content\n"
        
        with patch('subprocess.run', return_value=mock_result):
            content = enforcer._git_show("test.txt")
            
            assert content == "file content\n"

    def test_git_show_file_not_in_repo(self, enforcer):
        """测试Git显示文件（文件不在仓库中）。"""
        mock_result = MagicMock()
        mock_result.returncode = 128
        mock_result.stderr = "pathspec 'test.txt' did not match any"
        
        with patch('subprocess.run', return_value=mock_result):
            content = enforcer._git_show("test.txt")
            
            assert content is None

    def test_git_show_timeout(self, enforcer):
        """测试Git显示文件超时。"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5)):
            content = enforcer._git_show("test.txt")
            
            assert content is None

    def test_read_local_file(self, enforcer, temp_dir):
        """测试读取本地文件。"""
        file_path = Path(temp_dir) / "test.txt"
        file_path.write_text("test content")
        
        content = enforcer._read_local_file(str(file_path))
        
        assert content == "test content"

    def test_read_local_file_io_error(self, enforcer):
        """测试读取本地文件IO错误。"""
        content = enforcer._read_local_file("/nonexistent/path/file.txt")
        
        assert content == ""

    def test_read_local_file_unicode_error(self, enforcer, temp_dir):
        """测试读取本地文件编码错误。"""
        file_path = Path(temp_dir) / "binary.bin"
        file_path.write_bytes(b'\x80\x81\x82\x83')
        
        content = enforcer._read_local_file(str(file_path))
        
        assert content == ""

    def test_check_file_in_git_success(self, enforcer):
        """测试检查文件在Git中（成功）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        
        with patch('subprocess.run', return_value=mock_result):
            result = enforcer.check_file_in_git("test.txt")
            
            assert result is True

    def test_check_file_in_git_not_in_git(self, enforcer):
        """测试检查文件不在Git中。"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        
        with patch('subprocess.run', return_value=mock_result):
            result = enforcer.check_file_in_git("nonexistent.txt")
            
            assert result is False

    def test_check_file_in_git_timeout(self, enforcer):
        """测试检查文件在Git中（超时）。"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5)):
            result = enforcer.check_file_in_git("test.txt")
            
            assert result is False

    def test_check_file_in_git_file_not_found(self, enforcer):
        """测试检查文件在Git中（Git未安装）。"""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            result = enforcer.check_file_in_git("test.txt")
            
            assert result is False

    def test_get_file_version_success(self, enforcer):
        """测试获取文件版本（成功）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456\n"
        
        with patch('subprocess.run', return_value=mock_result):
            version = enforcer.get_file_version("test.txt")
            
            assert version == "abc123def456"

    def test_get_file_version_not_tracked(self, enforcer):
        """测试获取文件版本（文件未跟踪）。"""
        mock_result = MagicMock()
        mock_result.returncode = 128
        
        with patch('subprocess.run', return_value=mock_result):
            version = enforcer.get_file_version("nonexistent.txt")
            
            assert version is None

    def test_get_file_version_timeout(self, enforcer):
        """测试获取文件版本（超时）。"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5)):
            version = enforcer.get_file_version("test.txt")
            
            assert version is None

    def test_get_file_version_file_not_found(self, enforcer):
        """测试获取文件版本（Git未安装）。"""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            version = enforcer.get_file_version("test.txt")
            
            assert version is None

    def test_get_commit_info_success(self, enforcer):
        """测试获取提交信息（成功）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123\nJohn Doe\njohn@example.com\n2024-01-01\nTest commit message"
        
        with patch('subprocess.run', return_value=mock_result):
            info = enforcer.get_commit_info("abc123")
            
            assert info["hash"] == "abc123"
            assert info["author"] == "John Doe"
            assert info["email"] == "john@example.com"
            assert info["date"] == "2024-01-01"
            assert info["message"] == "Test commit message"

    def test_get_commit_info_default_head(self, enforcer):
        """测试获取提交信息（默认HEAD）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "def456\nJane Doe\njane@example.com\n2024-02-01\nAnother commit"
        
        with patch('subprocess.run', return_value=mock_result):
            info = enforcer.get_commit_info()
            
            assert info["hash"] == "def456"
            assert info["author"] == "Jane Doe"

    def test_get_commit_info_partial_output(self, enforcer):
        """测试获取提交信息（部分输出）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123\n"
        
        with patch('subprocess.run', return_value=mock_result):
            info = enforcer.get_commit_info("abc123")
            
            assert info["hash"] == "abc123"
            assert info["author"] == ""
            assert info["email"] == ""
            assert info["date"] == ""
            assert info["message"] == ""

    def test_get_commit_info_failure(self, enforcer):
        """测试获取提交信息（失败）。"""
        mock_result = MagicMock()
        mock_result.returncode = 128
        
        with patch('subprocess.run', return_value=mock_result):
            info = enforcer.get_commit_info("invalidhash")
            
            assert info == {}

    def test_get_commit_info_timeout(self, enforcer):
        """测试获取提交信息（超时）。"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5)):
            info = enforcer.get_commit_info("abc123")
            
            assert info == {}

    def test_get_commit_info_file_not_found(self, enforcer):
        """测试获取提交信息（Git未安装）。"""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            info = enforcer.get_commit_info("abc123")
            
            assert info == {}

    def test_git_show_file_not_found(self, enforcer):
        """测试Git显示文件（Git未安装）。"""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            content = enforcer._git_show("test.txt")
            
            assert content is None


class TestGitConfigChecker:
    """Git配置检查器测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def checker(self, temp_dir):
        """创建检查器实例。"""
        from src.core.git_workflow_enforcer import GitConfigChecker
        return GitConfigChecker(project_path=temp_dir)

    def test_init_default_path(self):
        """测试默认路径初始化。"""
        from src.core.git_workflow_enforcer import GitConfigChecker
        checker = GitConfigChecker()
        assert checker.project_path == Path(".")

    def test_init_custom_path(self, temp_dir):
        """测试自定义路径初始化。"""
        from src.core.git_workflow_enforcer import GitConfigChecker
        checker = GitConfigChecker(project_path=temp_dir)
        assert checker.project_path == Path(temp_dir)

    def test_check_git_installed_true(self, checker):
        """测试Git已安装。"""
        mock_result = MagicMock()
        
        with patch('subprocess.run', return_value=mock_result):
            result = checker.check_git_installed()
            
            assert result is True

    def test_check_git_installed_false(self, checker):
        """测试Git未安装。"""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            result = checker.check_git_installed()
            
            assert result is False

    def test_check_git_configured_true(self, checker):
        """测试Git已配置。"""
        mock_result = MagicMock()
        mock_result.stdout = "user.name=Test User\nuser.email=test@example.com\n"
        
        with patch('subprocess.run', return_value=mock_result):
            configured, message = checker.check_git_configured()
            
            assert configured is True
            assert message == "Git 已配置用户信息"

    def test_check_git_configured_false_no_name(self, checker):
        """测试Git未配置（缺少用户名）。"""
        mock_result = MagicMock()
        mock_result.stdout = "user.email=test@example.com\n"
        
        with patch('subprocess.run', return_value=mock_result):
            configured, message = checker.check_git_configured()
            
            assert configured is False
            assert "user.name/user.email" in message

    def test_check_git_configured_false_no_email(self, checker):
        """测试Git未配置（缺少邮箱）。"""
        mock_result = MagicMock()
        mock_result.stdout = "user.name=Test User\n"
        
        with patch('subprocess.run', return_value=mock_result):
            configured, message = checker.check_git_configured()
            
            assert configured is False
            assert "user.name/user.email" in message

    def test_check_git_configured_not_installed(self, checker):
        """测试Git未安装。"""
        with patch('subprocess.run', side_effect=FileNotFoundError):
            configured, message = checker.check_git_configured()
            
            assert configured is False
            assert message == "Git 未安装"

    def test_check_remote_configured_true(self, checker):
        """测试远程仓库已配置。"""
        mock_result = MagicMock()
        mock_result.stdout = "origin  https://github.com/user/repo.git (fetch)\n"
        
        with patch('subprocess.run', return_value=mock_result):
            configured, message = checker.check_remote_configured()
            
            assert configured is True
            assert "已配置" in message

    def test_check_remote_configured_false(self, checker):
        """测试远程仓库未配置。"""
        mock_result = MagicMock()
        mock_result.stdout = ""
        
        with patch('subprocess.run', return_value=mock_result):
            configured, message = checker.check_remote_configured()
            
            assert configured is False
            assert message == "未配置远程仓库"

    def test_check_remote_configured_timeout(self, checker):
        """测试远程仓库检查超时。"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git", timeout=5)):
            configured, message = checker.check_remote_configured()
            
            assert configured is False
            assert message == "Git 命令超时"

    def test_get_full_status(self, checker, temp_dir):
        """测试获取完整Git状态。"""
        with patch.object(checker, 'check_git_installed', return_value=True):
            with patch.object(checker, 'check_git_configured', return_value=(True, "Configured")):
                with patch.object(checker, 'check_remote_configured', return_value=(True, "Remote configured")):
                    status = checker.get_full_status()
                    
                    assert status["git_installed"] is True
                    assert status["git_configured"] is True
                    assert status["remote_configured"] is True
                    assert status["is_repository"] is False
                    assert status["git_root"] is None


class TestGitWorkflowEnforcerModule:
    """Git工作流强制执行器模块测试。"""

    def test_module_importable(self):
        """测试模块可导入。"""
        from src.core import git_workflow_enforcer
        assert hasattr(git_workflow_enforcer, 'GitWorkflowEnforcer')
        assert hasattr(git_workflow_enforcer, 'WorkflowViolation')
        assert hasattr(git_workflow_enforcer, 'GitConfigChecker')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
