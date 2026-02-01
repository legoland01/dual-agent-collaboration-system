"""Git监控器单元测试。"""
import pytest
import tempfile
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock


sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.git_monitor import (
    GitMonitor, GitConfig, GitMonitorError, GitNotInstalledError,
    NotRepositoryError, NetworkError, ChangeType, CommitInfo, ChangeInfo, GitEvent
)


class TestGitConfig:
    """Git配置测试类。"""
    
    def test_default_config(self):
        """测试默认配置。"""
        config = GitConfig()
        
        assert config.polling_interval == 30
        assert config.max_polling_interval == 300
        assert config.enable_exponential_backoff == True
        assert config.enable_webhook == False
    
    def test_custom_config(self):
        """测试自定义配置。"""
        config = GitConfig(
            polling_interval=60,
            max_polling_interval=600,
            enable_webhook=True,
            webhook_url="http://example.com/webhook"
        )
        
        assert config.polling_interval == 60
        assert config.max_polling_interval == 600
        assert config.enable_webhook == True
        assert config.webhook_url == "http://example.com/webhook"
    
    def test_polling_interval_bounds(self):
        """测试轮询间隔边界。"""
        config = GitConfig(polling_interval=5)
        assert config.polling_interval == 10
        
        config = GitConfig(polling_interval=1000)
        assert config.polling_interval == 1000


class TestGitMonitor:
    """Git监控器测试类。"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def git_monitor(self, temp_dir):
        """创建Git监控器实例（已mock git命令）。"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "true"
            mock_run.return_value = mock_result
            
            config = GitConfig(polling_interval=30)
            return GitMonitor(temp_dir, config)
    
    def test_initialization(self, git_monitor):
        """测试初始化。"""
        assert git_monitor._running == False
        assert git_monitor._current_poll_interval == 30
        assert isinstance(git_monitor.config, GitConfig)
    
    def test_get_current_branch(self, git_monitor):
        """测试获取当前分支。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            branch = git_monitor.get_current_branch()
            assert branch == "main"
    
    def test_get_commit_hash(self, git_monitor):
        """测试获取提交哈希。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456789012345678901234567890\n"
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            commit_hash = git_monitor.get_commit_hash()
            assert commit_hash is not None
            assert len(commit_hash) >= 36
    
    def test_get_commit_info(self, git_monitor):
        """测试获取提交信息。"""
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('args', [])
            mock_result = MagicMock()
            mock_result.returncode = 0
            if 'rev-parse' in cmd and 'HEAD' in cmd:
                mock_result.stdout = "abc123def456789012345678901234567890\n"
            elif 'rev-parse' in cmd and len(cmd) > 2:
                mock_result.stdout = "abc123def456789012345678901234567890\n"
            elif 'log' in cmd:
                mock_result.stdout = "abc123def456789012345678901234567890|Test|test@test.com|2024-01-01|Test commit"
            elif 'show' in cmd:
                mock_result.stdout = "M\ttest.py\n"
            elif 'rev-list' in cmd and '--parents' in cmd:
                mock_result.stdout = "abc123def456789012345678901234567890 parent123\n"
            return mock_result
        
        with patch.object(git_monitor, '_run_git_command', side_effect=mock_run_side_effect):
            commit_info = git_monitor.get_commit_info("abc123")
            
            assert commit_info is not None
            assert commit_info.hash == "abc123def456789012345678901234567890"
    
    def test_get_new_commits_empty(self, git_monitor):
        """测试获取新提交（无新提交）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            commits = git_monitor.get_new_commits()
            assert len(commits) == 0
    
    def test_detect_changes_empty(self, git_monitor):
        """测试检测变更（无变更）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            with patch.object(git_monitor, 'get_new_commits', return_value=[]):
                events = git_monitor.detect_changes()
                assert len(events) == 0
    
    def test_detect_state_file_changes_no_file(self, git_monitor):
        """测试检测状态文件变更（文件不存在）。"""
        result = git_monitor.detect_state_file_changes()
        assert result["has_changes"] == False
        assert "不存在" in result["reason"]
    
    def test_get_status_summary(self, git_monitor):
        """测试获取监控状态摘要。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            summary = git_monitor.get_status_summary()
            
            assert "project_path" in summary
            assert "current_branch" in summary
            assert "polling_interval" in summary
            assert "is_running" in summary
            assert "config" in summary
    
    def test_reset_processed_commits(self, git_monitor):
        """测试重置已处理提交。"""
        git_monitor._processed_commits.add("abc123")
        git_monitor._last_commit = "abc123"
        
        git_monitor.reset_processed_commits()
        
        assert len(git_monitor._processed_commits) == 0
        assert git_monitor._last_commit is None
    
    def test_add_callback(self, git_monitor):
        """测试添加回调函数。"""
        callback = MagicMock()
        git_monitor.add_callback(callback)
        
        assert callback in git_monitor._callbacks
    
    def test_get_status_summary_remote_url(self, git_monitor):
        """测试获取远程URL（可能为None）。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "main\n"
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            summary = git_monitor.get_status_summary()
            assert "remote_url" in summary


class TestGitMonitorEdgeCases:
    """Git监控器边界情况测试类。"""
    
    def test_not_git_repository(self):
        """测试非Git仓库。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('subprocess.run') as mock_run:
                def side_effect(*args, **kwargs):
                    cmd = args[0] if args else kwargs.get('args', [])
                    if cmd[0] == 'git' and cmd[1] == '--version':
                        mock_result = MagicMock()
                        mock_result.returncode = 0
                        return mock_result
                    elif 'rev-parse' in cmd:
                        raise subprocess.CalledProcessError(128, "git")
                    return MagicMock()
                
                mock_run.side_effect = side_effect
                with pytest.raises(NotRepositoryError):
                    GitMonitor(tmpdir)
    
    def test_git_not_installed(self):
        """测试Git未安装。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('subprocess.run', side_effect=FileNotFoundError("git not found")):
                with pytest.raises(GitNotInstalledError):
                    GitMonitor(tmpdir)


class TestCommitInfo:
    """提交信息测试类。"""
    
    def test_commit_info_creation(self):
        """测试提交信息创建。"""
        commit = CommitInfo(
            hash="abc123def456",
            short_hash="abc123d",
            message="Test commit",
            author="Test User",
            timestamp="2024-01-01 00:00:00"
        )
        
        assert commit.hash == "abc123def456"
        assert commit.short_hash == "abc123d"
        assert commit.message == "Test commit"
        assert len(commit.files) == 0


class TestChangeInfo:
    """变更信息测试类。"""
    
    def test_change_info_added(self):
        """测试新增文件变更。"""
        change = ChangeInfo(
            file_path="src/main.py",
            change_type=ChangeType.ADDED
        )
        
        assert change.file_path == "src/main.py"
        assert change.change_type == ChangeType.ADDED
    
    def test_change_info_modified(self):
        """测试修改文件变更。"""
        change = ChangeInfo(
            file_path="src/main.py",
            change_type=ChangeType.MODIFIED
        )
        
        assert change.change_type == ChangeType.MODIFIED
    
    def test_change_info_deleted(self):
        """测试删除文件变更。"""
        change = ChangeInfo(
            file_path="src/main.py",
            change_type=ChangeType.DELETED
        )
        
        assert change.change_type == ChangeType.DELETED


class TestGitEvent:
    """Git事件测试类。"""
    
    def test_git_event_creation(self):
        """测试Git事件创建。"""
        commit = CommitInfo(
            hash="abc123",
            short_hash="abc123",
            message="Test",
            author="Test",
            timestamp="2024-01-01"
        )
        
        event = GitEvent(
            event_type="new_commit",
            commit=commit,
            branch="main"
        )
        
        assert event.event_type == "new_commit"
        assert event.commit == commit
        assert event.branch == "main"
        assert len(event.changes) == 0


class TestChangeType:
    """变更类型测试类。"""
    
    def test_change_type_values(self):
        """测试变更类型枚举值。"""
        assert ChangeType.ADDED.value == "added"
        assert ChangeType.MODIFIED.value == "modified"
        assert ChangeType.DELETED.value == "deleted"
        assert ChangeType.RENAMED.value == "renamed"


class TestGitMonitorMoreCoverage:
    """Git监控器更多覆盖率测试。"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def git_monitor(self, temp_dir):
        """创建Git监控器实例（已mock git命令）。"""
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "true"
            mock_run.return_value = mock_result
            
            config = GitConfig(polling_interval=30)
            return GitMonitor(temp_dir, config)
    
    def test_run_git_command_timeout(self, git_monitor):
        """测试Git命令超时。"""
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired(cmd="git", timeout=30)):
            with pytest.raises(NetworkError):
                git_monitor._run_git_command("status")
    
    def test_run_git_command_network_error_with_retry(self, git_monitor):
        """测试Git命令网络错误（重试后失败）。"""
        with patch('subprocess.run') as mock_run:
            def side_effect(*args, **kwargs):
                cmd = args[0] if args else kwargs.get('args', [])
                if 'could not read' in str(cmd):
                    raise subprocess.CalledProcessError(128, cmd, stderr="could not read")
                return MagicMock(returncode=0)
            
            mock_run.side_effect = side_effect
            result = git_monitor._run_git_command("fetch", retries=3)
            assert result.returncode == 0
    
    def test_get_remote_url_failure(self, git_monitor):
        """测试获取远程URL失败。"""
        with patch.object(git_monitor, '_run_git_command', side_effect=GitMonitorError("Failed")):
            url = git_monitor.get_remote_url()
            assert url is None
    
    def test_get_new_commits_with_data(self, git_monitor):
        """测试获取新提交（有数据）。"""
        git_monitor._last_commit = None
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            commits = git_monitor.get_new_commits(since_ref="HEAD")
            
            assert commits == []
    
    def test_detect_changes_with_commits(self, git_monitor):
        """测试检测变更（有提交）。"""
        commit = CommitInfo(
            hash="abc123",
            short_hash="abc123",
            message="Test",
            author="Test",
            timestamp="2024-01-01",
            files=[{"path": "test.py", "type": "modified"}]
        )
        
        with patch.object(git_monitor, '_run_git_command') as mock_cmd:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "main\n"
            mock_cmd.return_value = mock_result
            
            with patch.object(git_monitor, 'get_new_commits', return_value=[commit]):
                events = git_monitor.detect_changes()
                
                assert len(events) == 1
                assert events[0].event_type == "new_commit"
    
    def test_detect_state_file_changes_with_changes(self, git_monitor):
        """测试检测状态文件变更（有变更）。"""
        state_file = git_monitor.project_path / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.touch()
        
        commit = CommitInfo(
            hash="abc123",
            short_hash="abc123",
            message="Test",
            author="Test",
            timestamp="2024-01-01",
            files=[{"path": "state/project_state.yaml", "type": "modified"}]
        )
        
        event = GitEvent(
            event_type="new_commit",
            commit=commit,
            changes=[ChangeInfo("state/project_state.yaml", ChangeType.MODIFIED)],
            branch="main"
        )
        
        with patch.object(git_monitor, 'detect_changes', return_value=[event]):
            result = git_monitor.detect_state_file_changes()
            
            assert result["has_changes"] is True
            assert result["commit"] == "abc123"
    
    def test_parse_change_type_all_types(self, git_monitor):
        """测试解析所有变更类型。"""
        assert git_monitor._parse_change_type("A") == ChangeType.ADDED
        assert git_monitor._parse_change_type("M") == ChangeType.MODIFIED
        assert git_monitor._parse_change_type("D") == ChangeType.DELETED
        assert git_monitor._parse_change_type("R") == ChangeType.RENAMED
        assert git_monitor._parse_change_type("") == ChangeType.MODIFIED
        assert git_monitor._parse_change_type("X") == ChangeType.MODIFIED
    
    def test_add_multiple_callbacks(self, git_monitor):
        """测试添加多个回调函数。"""
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        git_monitor.add_callback(callback1)
        git_monitor.add_callback(callback2)
        
        assert callback1 in git_monitor._callbacks
        assert callback2 in git_monitor._callbacks
        assert len(git_monitor._callbacks) == 2

    def test_notify_callbacks(self, git_monitor):
        """测试通知回调函数。"""
        callback = MagicMock()
        git_monitor.add_callback(callback)
        
        commit = CommitInfo(
            hash="abc123",
            short_hash="abc123",
            message="Test",
            author="Test",
            timestamp="2024-01-01"
        )
        event = GitEvent(event_type="new_commit", commit=commit, branch="main")
        
        git_monitor._notify_callbacks([event])
        
        callback.assert_called_once_with([event])

    def test_notify_callbacks_exception(self, git_monitor):
        """测试通知回调函数（异常）。"""
        callback = MagicMock(side_effect=Exception("Callback failed"))
        git_monitor.add_callback(callback)
        
        commit = CommitInfo(
            hash="abc123",
            short_hash="abc123",
            message="Test",
            author="Test",
            timestamp="2024-01-01"
        )
        event = GitEvent(event_type="new_commit", commit=commit, branch="main")
        
        git_monitor._notify_callbacks([event])

    def test_adjust_polling_interval_with_changes(self, git_monitor):
        """测试调整轮询间隔（有变更）。"""
        git_monitor._current_poll_interval = 120
        
        git_monitor._adjust_polling_interval(has_changes=True)
        
        assert git_monitor._current_poll_interval == 30

    def test_adjust_polling_interval_no_changes(self, git_monitor):
        """测试调整轮询间隔（无变更）。"""
        git_monitor._current_poll_interval = 30
        
        git_monitor._adjust_polling_interval(has_changes=False)
        
        assert git_monitor._current_poll_interval == 60

    def test_adjust_polling_interval_max_limit(self, git_monitor):
        """测试调整轮询间隔（达到最大限制）。"""
        git_monitor._current_poll_interval = 150
        
        git_monitor._adjust_polling_interval(has_changes=False)
        
        assert git_monitor._current_poll_interval == 300

    def test_adjust_polling_interval_disabled(self, git_monitor):
        """测试调整轮询间隔（禁用）。"""
        git_monitor.config.enable_exponential_backoff = False
        git_monitor._current_poll_interval = 120
        
        git_monitor._adjust_polling_interval(has_changes=False)
        
        assert git_monitor._current_poll_interval == 30

    def test_start_monitoring(self, git_monitor):
        """测试开始监控。"""
        git_monitor.start_monitoring()
        
        assert git_monitor._running is True
        assert git_monitor._monitor_thread is not None
        
        git_monitor.stop_monitoring()

    def test_start_monitoring_with_callback(self, git_monitor):
        """测试开始监控（带回调）。"""
        callback = MagicMock()
        git_monitor.start_monitoring(callback)
        
        assert callback in git_monitor._callbacks
        assert git_monitor._running is True
        
        git_monitor.stop_monitoring()

    def test_start_monitoring_already_running(self, git_monitor):
        """测试开始监控（已在运行）。"""
        git_monitor._running = True
        
        git_monitor.start_monitoring()
        
        assert git_monitor._monitor_thread is None

    def test_stop_monitoring(self, git_monitor):
        """测试停止监控。"""
        git_monitor._running = True
        git_monitor._monitor_thread = MagicMock()
        git_monitor._monitor_thread.is_alive.return_value = False
        
        git_monitor.stop_monitoring()
        
        assert git_monitor._running is False
        assert git_monitor._monitor_thread is None

    def test_fetch_remote_failure(self, git_monitor):
        """测试拉取远程失败。"""
        with patch.object(git_monitor, '_run_git_command', side_effect=GitMonitorError("Failed")):
            result = git_monitor.fetch_remote()
            assert result is False

    def test_get_commit_hash_failure(self, git_monitor):
        """测试获取提交哈希失败。"""
        with patch.object(git_monitor, '_run_git_command', side_effect=GitMonitorError("Failed")):
            result = git_monitor.get_commit_hash()
            assert result is None

    def test_get_commit_info_partial(self, git_monitor):
        """测试获取提交信息（部分输出）。"""
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('args', [])
            mock_result = MagicMock()
            mock_result.returncode = 0
            if 'rev-parse' in cmd:
                mock_result.stdout = "abc123\n"
            elif 'log' in cmd:
                mock_result.stdout = "abc123"  # Missing fields
            elif 'show' in cmd:
                mock_result.stdout = ""
            elif 'rev-list' in cmd and '--parents' in cmd:
                mock_result.stdout = "abc123"
            return mock_result
        
        with patch.object(git_monitor, '_run_git_command', side_effect=mock_run_side_effect):
            commit_info = git_monitor.get_commit_info("abc123")
            
            assert commit_info is not None
            assert commit_info.hash == "abc123"

    def test_get_commit_info_failure(self, git_monitor):
        """测试获取提交信息失败。"""
        with patch.object(git_monitor, '_run_git_command', side_effect=GitMonitorError("Failed")):
            commit_info = git_monitor.get_commit_info("abc123")
            assert commit_info is None

    def test_get_new_commits_with_processed(self, git_monitor):
        """测试获取新提交（已处理）。"""
        git_monitor._processed_commits.add("abc123")
        
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123\n"
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            with patch.object(git_monitor, 'get_commit_info', return_value=None):
                commits = git_monitor.get_new_commits()
                
                assert len(commits) == 0

    def test_get_new_commits_with_multiple(self, git_monitor):
        """测试获取新提交（多个）。"""
        def mock_run_side_effect(*args, **kwargs):
            cmd = args[0] if args else kwargs.get('args', [])
            mock_result = MagicMock()
            mock_result.returncode = 0
            if 'rev-list' in cmd:
                mock_result.stdout = "abc123\ndef456\n"
            elif 'rev-parse' in cmd:
                mock_result.stdout = "abc123\n"
            elif 'log' in cmd:
                mock_result.stdout = "abc123|Test|test@test.com|2024-01-01|Test commit"
            elif 'show' in cmd:
                mock_result.stdout = "M\ttest.py\n"
            elif 'rev-list' in cmd and '--parents' in cmd:
                mock_result.stdout = "abc123"
            return mock_result
        
        with patch.object(git_monitor, '_run_git_command', side_effect=mock_run_side_effect):
            commits = git_monitor.get_new_commits()
            
            assert len(commits) == 2

    def test_check_remote_connection_success(self, git_monitor):
        """测试检查远程连接成功。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        
        with patch.object(git_monitor, '_run_git_command', return_value=mock_result):
            result = git_monitor.check_remote_connection()
            assert result is True

    def test_check_remote_connection_failure(self, git_monitor):
        """测试检查远程连接失败。"""
        with patch.object(git_monitor, '_run_git_command', side_effect=GitMonitorError("Failed")):
            result = git_monitor.check_remote_connection()
            assert result is False

    def test_detect_state_file_changes_no_changes(self, git_monitor):
        """测试检测状态文件变更（无变更）。"""
        state_file = git_monitor.project_path / "state" / "project_state.yaml"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        state_file.touch()
        
        event = GitEvent(
            event_type="new_commit",
            commit=None,
            changes=[ChangeInfo("other.py", ChangeType.MODIFIED)],
            branch="main"
        )
        
        with patch.object(git_monitor, 'detect_changes', return_value=[event]):
            result = git_monitor.detect_state_file_changes()
            
            assert result["has_changes"] is False

    def test_monitor_loop_exception(self, git_monitor):
        """测试监控循环异常处理。"""
        call_count = 0
        
        def mock_time():
            nonlocal call_count
            call_count += 1
            if call_count > 2:
                git_monitor._running = False
            return 100 + call_count
        
        git_monitor._running = True
        git_monitor._last_poll_time = 0
        
        with patch.object(git_monitor, 'detect_changes', side_effect=Exception("Error")):
            with patch('time.time', side_effect=mock_time):
                with patch('time.sleep'):
                    git_monitor._monitor_loop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])