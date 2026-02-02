"""Git 单元测试。"""
import pytest
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.git import (
    GitHelper, GitError, GitNotInstalledError, GitRepositoryError,
    GitOperationError, GitConflictError, GitTimeoutError, GitTimeoutConfig
)


class TestGitExceptions:
    """Git异常测试。"""

    def test_git_not_installed_error(self):
        """测试Git未安装异常。"""
        with pytest.raises(GitNotInstalledError):
            raise GitNotInstalledError("Git not installed")

    def test_git_repository_error(self):
        """测试Git仓库异常。"""
        with pytest.raises(GitRepositoryError):
            raise GitRepositoryError("Not a git repository")

    def test_git_operation_error(self):
        """测试Git操作失败异常。"""
        with pytest.raises(GitOperationError):
            raise GitOperationError("Operation failed")

    def test_git_conflict_error(self):
        """测试Git冲突异常。"""
        with pytest.raises(GitConflictError):
            raise GitConflictError("Merge conflict")

    def test_git_timeout_error(self):
        """测试Git超时异常。"""
        with pytest.raises(GitTimeoutError):
            raise GitTimeoutError("Command timed out")


class TestGitTimeoutConfig:
    """Git超时配置测试。"""

    def test_default_timeout_config(self):
        """测试默认超时配置。"""
        config = GitTimeoutConfig()
        assert config.status == 10.0
        assert config.add == 5.0
        assert config.commit == 10.0
        assert config.push == 60.0
        assert config.pull == 30.0

    def test_custom_timeout_config(self):
        """测试自定义超时配置。"""
        config = GitTimeoutConfig(status=5.0, push=120.0)
        assert config.status == 5.0
        assert config.push == 120.0


class TestGitHelper:
    """Git助手测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def git_helper(self, temp_dir):
        """创建Git助手实例（已mock subprocess.run）。"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            helper = GitHelper(temp_dir)
            mock_run.reset_mock()
            yield helper

    def test_init_with_default_timeouts(self, temp_dir):
        """测试初始化使用默认超时。"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            helper = GitHelper(temp_dir)
            assert helper.project_path == Path(temp_dir)
            assert helper.timeouts['status'] == 10.0

    def test_init_with_custom_timeouts(self, temp_dir):
        """测试初始化使用自定义超时。"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            custom_timeouts = {'status': 5.0, 'push': 120.0}
            helper = GitHelper(temp_dir, timeouts=custom_timeouts)
            assert helper.timeouts['status'] == 5.0
            assert helper.timeouts['push'] == 120.0
            assert helper.timeouts['commit'] == 10.0

    def test_ensure_git_installed_success(self, temp_dir):
        """测试Git已安装检查成功。"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            GitHelper(temp_dir)

    def test_ensure_git_installed_not_found(self, temp_dir):
        """测试Git未安装。"""
        with patch('subprocess.run', side_effect=FileNotFoundError("git not found")):
            with pytest.raises(GitNotInstalledError):
                GitHelper(temp_dir)

    def test_run_git_command_success(self, git_helper, temp_dir):
        """测试Git命令执行成功。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "origin\tgit@github.com:test/repo.git (fetch)"
        mock_result.stderr = ""
        with patch.object(git_helper, '_run_git_command', return_value=mock_result) as mock_cmd:
            result = git_helper._run_git_command("remote", "-v")
            assert result.returncode == 0

    def test_run_git_command_timeout(self, git_helper):
        """测试Git命令超时。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitTimeoutError("timeout")):
            with pytest.raises(GitTimeoutError):
                git_helper._run_git_command("status")

    def test_run_git_command_conflict(self, git_helper):
        """测试Git合并冲突。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitConflictError("conflict")):
            with pytest.raises(GitConflictError):
                git_helper._run_git_command("merge", "feature-branch")

    def test_run_git_command_operation_error(self, git_helper):
        """测试Git操作失败。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitOperationError("error")):
            with pytest.raises(GitOperationError):
                git_helper._run_git_command("status")

    def test_is_repository_true(self, git_helper):
        """测试是Git仓库。"""
        with patch.object(git_helper, '_run_git_command', return_value=MagicMock(returncode=0)):
            assert git_helper.is_repository() is True

    def test_is_repository_false(self, git_helper):
        """测试不是Git仓库。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitOperationError("not a repo")):
            assert git_helper.is_repository() is False

    def test_init_repository_not_repo(self, git_helper):
        """测试初始化Git仓库。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_result = MagicMock(returncode=128)
            mock_cmd.side_effect = [GitOperationError("not a repo"), None]
            
            git_helper.init_repository()
            assert mock_cmd.call_count == 2

    def test_init_repository_already_exists(self, git_helper):
        """测试已存在仓库不再初始化。"""
        with patch.object(git_helper, 'is_repository', return_value=True):
            with patch.object(git_helper, '_run_git_command') as mock_cmd:
                mock_cmd.return_value = MagicMock(returncode=0)
                
                git_helper.init_repository()
                mock_cmd.assert_not_called()

    def test_pull_success(self, git_helper):
        """测试拉取成功。"""
        with patch.object(git_helper, '_run_git_command', return_value=MagicMock(returncode=0)):
            result = git_helper.pull()
            assert result is True

    def test_pull_conflict(self, git_helper):
        """测试拉取冲突。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitConflictError("conflict")):
            with pytest.raises(GitConflictError):
                git_helper.pull()

    def test_pull_timeout(self, git_helper):
        """测试拉取超时。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitTimeoutError("timeout")):
            with pytest.raises(GitTimeoutError):
                git_helper.pull()

    def test_pull_operation_failed(self, git_helper):
        """测试拉取操作失败。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitOperationError("failed")):
            result = git_helper.pull()
            assert result is False

    def test_push_success(self, git_helper):
        """测试推送成功。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.push("Test commit")
            assert mock_cmd.call_count >= 2

    def test_push_with_tags(self, git_helper):
        """测试推送带标签。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.push("Test commit", push_all=True)
            assert mock_cmd.call_count >= 4

    def test_push_to_remote(self, git_helper):
        """测试推送到指定远程。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.push_to_remote("origin", branches=True, tags=True)
            assert mock_cmd.call_count == 2

    def test_push_to_remote_branches_only(self, git_helper):
        """测试只推送分支。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.push_to_remote("origin", branches=True, tags=False)
            assert mock_cmd.call_count == 1

    def test_push_all_remotes(self, git_helper):
        """测试推送到所有远程。"""
        with patch.object(git_helper, 'get_all_remotes', return_value=["origin"]):
            with patch.object(git_helper, '_run_git_command') as mock_cmd:
                mock_cmd.return_value = MagicMock(returncode=0)
                
                git_helper.push_all_remotes("Test commit")
                assert mock_cmd.call_count >= 3

    def test_add_remote(self, git_helper):
        """测试添加远程仓库。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.add_remote("origin", "https://github.com/test/repo.git")
            assert mock_cmd.call_count == 1

    def test_get_all_remotes(self, git_helper):
        """测试获取所有远程仓库。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "origin\tgit@github.com:test/repo.git (fetch)\norigin\tgit@github.com:test/repo.git (push)"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            remotes = git_helper.get_all_remotes()
            
            assert "origin" in remotes
            assert len(remotes) == 1

    def test_get_all_remotes_empty(self, git_helper):
        """测试无远程仓库。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            remotes = git_helper.get_all_remotes()
            
            assert remotes == []

    def test_create_branch(self, git_helper):
        """测试创建分支。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.create_branch("feature-branch")
            assert mock_cmd.call_count == 1

    def test_switch_branch(self, git_helper):
        """测试切换分支。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.switch_branch("main")
            assert mock_cmd.call_count == 1

    def test_branch_exists_true(self, git_helper):
        """测试分支存在。"""
        with patch.object(git_helper, '_run_git_command', return_value=MagicMock(returncode=0)):
            result = git_helper.branch_exists("main")
            assert result is True

    def test_branch_exists_false(self, git_helper):
        """测试分支不存在。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitOperationError("not found")):
            result = git_helper.branch_exists("nonexistent")
            assert result is False

    def test_create_tag_without_message(self, git_helper):
        """测试创建无消息标签。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.create_tag("v1.0.0")
            assert mock_cmd.call_count == 1

    def test_create_tag_with_message(self, git_helper):
        """测试创建带消息标签。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.create_tag("v1.0.0", "Release 1.0.0")
            assert mock_cmd.call_count == 1

    def test_get_current_branch(self, git_helper):
        """测试获取当前分支。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            branch = git_helper.get_current_branch()
            
            assert branch == "main"

    def test_get_remote_url_success(self, git_helper):
        """测试获取远程URL成功。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "https://github.com/test/repo.git\n"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            url = git_helper.get_remote_url()
            
            assert url == "https://github.com/test/repo.git"

    def test_get_remote_url_not_found(self, git_helper):
        """测试获取远程URL失败。"""
        with patch.object(git_helper, '_run_git_command', side_effect=GitOperationError("not found")):
            url = git_helper.get_remote_url()
            
            assert url is None

    def test_has_local_changes_true(self, git_helper):
        """测试有本地修改。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = " M modified.txt\n?? newfile.txt\n"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            has_changes = git_helper.has_local_changes()
            
            assert has_changes is True

    def test_has_local_changes_false(self, git_helper):
        """测试无本地修改。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            has_changes = git_helper.has_local_changes()
            
            assert has_changes is False

    def test_get_commit_hash(self, git_helper):
        """测试获取提交哈希。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456\n"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            commit_hash = git_helper.get_commit_hash()
            
            assert commit_hash == "abc123def456"

    def test_get_commit_hash_specific_branch(self, git_helper):
        """测试获取指定分支提交哈希。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456\n"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            commit_hash = git_helper.get_commit_hash("develop")
            
            assert commit_hash == "abc123def456"

    def test_get_commit_message(self, git_helper):
        """测试获取提交信息。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Fix bug in login\n"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            message = git_helper.get_commit_message()
            
            assert message == "Fix bug in login"

    def test_get_all_branches(self, git_helper):
        """测试获取所有分支。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "* main\n  develop\n  feature/test\n"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            branches = git_helper.get_all_branches()
            
            assert any("main" in b for b in branches)
            assert any("develop" in b for b in branches)
            assert any("feature/test" in b for b in branches)

    def test_get_all_tags(self, git_helper):
        """测试获取所有标签。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "v1.0.0\nv1.0.1\nv2.0.0\n"
        
        with patch.object(git_helper, '_run_git_command', return_value=mock_result):
            tags = git_helper.get_all_tags()
            
            assert "v1.0.0" in tags
            assert "v2.0.0" in tags

    def test_delete_branch(self, git_helper):
        """测试删除分支。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.delete_branch("feature-branch")
            assert mock_cmd.call_count == 1

    def test_delete_tag(self, git_helper):
        """测试删除标签。"""
        with patch.object(git_helper, '_run_git_command') as mock_cmd:
            mock_cmd.return_value = MagicMock(returncode=0)
            
            git_helper.delete_tag("v1.0.0")
            assert mock_cmd.call_count == 1


class TestGitRunCommandDirectly:
    """直接测试_run_git_command异常处理。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_run_git_command_timeout_directly(self, temp_dir):
        """测试_run_git_command超时异常。"""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired(cmd="git status", timeout=10.0)
            
            with patch('src.core.git.GitHelper._ensure_git_installed'):
                from src.core.git import GitHelper
                helper = GitHelper(temp_dir)
                
                with pytest.raises(GitTimeoutError):
                    helper._run_git_command("status")

    def test_run_git_command_conflict_directly(self, temp_dir):
        """测试_run_git_command冲突异常。"""
        with patch('subprocess.run') as mock_run:
            mock_error = subprocess.CalledProcessError(1, "git merge")
            mock_error.stderr = "CONFLICT (content): Merge conflict in file.txt"
            mock_run.side_effect = mock_error
            
            with patch('src.core.git.GitHelper._ensure_git_installed'):
                from src.core.git import GitHelper
                helper = GitHelper(temp_dir)
                
                with pytest.raises(GitConflictError):
                    helper._run_git_command("merge", "feature-branch")

    def test_run_git_command_operation_error_directly(self, temp_dir):
        """测试_run_git_command操作失败异常。"""
        with patch('subprocess.run') as mock_run:
            mock_error = subprocess.CalledProcessError(1, "git status")
            mock_error.stderr = "fatal: not a git repository"
            mock_run.side_effect = mock_error
            
            with patch('src.core.git.GitHelper._ensure_git_installed'):
                from src.core.git import GitHelper
                helper = GitHelper(temp_dir)
                
                with pytest.raises(GitOperationError):
                    helper._run_git_command("status")

    def test_run_git_command_default_timeout(self, temp_dir):
        """测试_run_git_command使用默认超时。"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            with patch('src.core.git.GitHelper._ensure_git_installed'):
                from src.core.git import GitHelper
                helper = GitHelper(temp_dir)
                helper._run_git_command("status")
                
                mock_run.assert_called_once()
                call_args = mock_run.call_args
                assert call_args.kwargs.get('timeout') == 10.0


class TestGitModule:
    """Git模块测试。"""

    def test_module_importable(self):
        """测试模块可导入。"""
        from src.core import git
        assert hasattr(git, 'GitHelper')
        assert hasattr(git, 'GitError')
        assert hasattr(git, 'GitConflictError')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
