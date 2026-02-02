"""AutoRetry 单元测试。"""
import pytest
import time
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.auto_retry import (
    AutoRetry, AutoRetryConfig, RetryableError, NonRetryableError
)


class TestAutoRetryConfig:
    """智能重试配置测试。"""

    def test_default_config(self):
        """测试默认配置。"""
        config = AutoRetryConfig()
        assert config.max_retries == 10
        assert config.retry_interval == 30
        assert config.exponential_backoff is True
        assert config.max_interval == 300
        assert config.verbose is True

    def test_custom_config(self):
        """测试自定义配置。"""
        config = AutoRetryConfig(
            max_retries=5,
            retry_interval=10,
            exponential_backoff=False,
            max_interval=60
        )
        assert config.max_retries == 5
        assert config.retry_interval == 10
        assert config.exponential_backoff is False
        assert config.max_interval == 60


class TestRetryableError:
    """可重试错误测试。"""

    def test_retryable_error(self):
        """测试可重试错误。"""
        with pytest.raises(RetryableError):
            raise RetryableError("Connection error")


class TestNonRetryableError:
    """不可重试错误测试。"""

    def test_non_retryable_error(self):
        """测试不可重试错误。"""
        with pytest.raises(NonRetryableError):
            raise NonRetryableError("Authentication failed")


class TestAutoRetry:
    """智能重试器测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def mock_git_helper(self):
        """Mock GitHelper。"""
        with patch('src.core.auto_retry.GitHelper'):
            mock_helper = MagicMock()
            mock_helper.get_all_remotes.return_value = ["origin"]
            yield mock_helper

    @pytest.fixture
    def auto_retry(self, temp_dir, mock_git_helper):
        """创建智能重试器实例。"""
        with patch('src.core.auto_retry.GitHelper', return_value=mock_git_helper):
            return AutoRetry(temp_dir)

    def test_init(self, auto_retry, temp_dir):
        """测试初始化。"""
        assert auto_retry.project_path == Path(temp_dir)
        assert auto_retry.config.max_retries == 10

    def test_should_retry_connection_error(self, auto_retry):
        """测试可重试错误（连接错误）。"""
        error = Exception("Connection reset by peer")
        assert auto_retry._should_retry(error) is True

    def test_should_retry_timeout(self, auto_retry):
        """测试可重试错误（超时）。"""
        error = Exception("Connection timed out")
        assert auto_retry._should_retry(error) is True

    def test_should_retry_http_5xx(self, auto_retry):
        """测试可重试错误（HTTP 5xx）。"""
        error = Exception("HTTP 500 Internal Server Error")
        assert auto_retry._should_retry(error) is True

    def test_should_not_retry_auth_error(self, auto_retry):
        """测试不可重试错误（认证失败）。"""
        error = Exception("Authentication failed")
        assert auto_retry._should_retry(error) is False

    def test_should_not_retry_permission_denied(self, auto_retry):
        """测试不可重试错误（权限拒绝）。"""
        error = Exception("Permission denied")
        assert auto_retry._should_retry(error) is False

    def test_should_not_retry_401(self, auto_retry):
        """测试不可重试错误（401）。"""
        error = Exception("HTTP 401 Unauthorized")
        assert auto_retry._should_retry(error) is False

    def test_should_not_retry_403(self, auto_retry):
        """测试不可重试错误（403）。"""
        error = Exception("HTTP 403 Forbidden")
        assert auto_retry._should_retry(error) is False

    def test_should_retry_unknown(self, auto_retry):
        """测试未知错误（默认不可重试）。"""
        error = Exception("Some unknown error")
        assert auto_retry._should_retry(error) is False

    def test_calculate_delay_exponential_backoff(self, auto_retry):
        """测试指数退避延迟计算。"""
        auto_retry.config.exponential_backoff = True
        auto_retry.config.retry_interval = 30
        auto_retry.config.max_interval = 300
        
        assert auto_retry._calculate_delay(0) == 30
        assert auto_retry._calculate_delay(1) == 60
        assert auto_retry._calculate_delay(2) == 120
        assert auto_retry._calculate_delay(3) == 240
        assert auto_retry._calculate_delay(4) == 300  # Max capped

    def test_calculate_delay_no_backoff(self, auto_retry):
        """测试固定延迟计算。"""
        auto_retry.config.exponential_backoff = False
        auto_retry.config.retry_interval = 30
        
        assert auto_retry._calculate_delay(0) == 30
        assert auto_retry._calculate_delay(5) == 30

    def test_push_with_retry_success_first_try(self, auto_retry, mock_git_helper):
        """测试推送成功（第一次尝试）。"""
        mock_git_helper._run_git_command.return_value = MagicMock()
        
        result = auto_retry.push_with_retry("Test commit")
        
        assert result["success"] is True
        assert result["attempts"] == 1
        assert "origin" in result["remotes"]

    def test_push_with_retry_success_after_retry(self, auto_retry, mock_git_helper):
        """测试推送成功（重试后）。"""
        from src.core.git import GitOperationError
        call_count = [0]
        
        def run_command(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise GitOperationError("Connection reset")
            return MagicMock()
        
        mock_git_helper._run_git_command.side_effect = run_command
        auto_retry.config.verbose = False
        auto_retry.config.max_retries = 3
        
        with patch('time.sleep'):
            result = auto_retry.push_with_retry("Test commit")
        
        assert result["success"] is True
        assert result["attempts"] == 2

    def test_push_with_retry_non_retryable_error(self, auto_retry, mock_git_helper):
        """测试推送不可重试错误。"""
        from src.core.git import GitOperationError
        mock_git_helper._run_git_command.side_effect = GitOperationError("Authentication failed")
        
        result = auto_retry.push_with_retry("Test commit")
        
        assert result["success"] is False
        assert result["attempts"] == 1

    def test_push_with_retry_max_retries_exceeded(self, auto_retry, mock_git_helper):
        """测试推送超过最大重试次数。"""
        from src.core.git import GitOperationError
        mock_git_helper._run_git_command.side_effect = GitOperationError("Connection reset")
        auto_retry.config.max_retries = 2
        auto_retry.config.verbose = False
        
        with patch('time.sleep'):
            result = auto_retry.push_with_retry("Test commit")
        
        assert result["success"] is False
        assert result["attempts"] == 2

    def test_push_with_retry_custom_remotes(self, auto_retry, mock_git_helper):
        """测试推送到指定远程。"""
        mock_git_helper._run_git_command.return_value = MagicMock()
        
        result = auto_retry.push_with_retry("Test commit", remotes=["origin", "backup"])
        
        assert result["success"] is True
        assert len(result["remotes"]) == 2

    def test_pull_with_retry_success_first_try(self, auto_retry, mock_git_helper):
        """测试拉取成功（第一次尝试）。"""
        mock_git_helper._run_git_command.return_value = MagicMock()
        
        result = auto_retry.pull_with_retry()
        
        assert result["success"] is True
        assert result["attempts"] == 1

    def test_pull_with_retry_success_after_retry(self, auto_retry, mock_git_helper):
        """测试拉取成功（重试后）。"""
        from src.core.git import GitOperationError
        call_count = [0]
        
        def run_command(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise GitOperationError("Connection timed out")
            return MagicMock()
        
        mock_git_helper._run_git_command.side_effect = run_command
        auto_retry.config.verbose = False
        auto_retry.config.max_retries = 3
        
        with patch('time.sleep'):
            result = auto_retry.pull_with_retry()
        
        assert result["success"] is True
        assert result["attempts"] == 2

    def test_pull_with_retry_non_retryable_error(self, auto_retry, mock_git_helper):
        """测试拉取不可重试错误。"""
        from src.core.git import GitOperationError
        mock_git_helper._run_git_command.side_effect = GitOperationError("Permission denied")
        
        result = auto_retry.pull_with_retry()
        
        assert result["success"] is False
        assert result["attempts"] == 1

    def test_pull_with_retry_max_retries_exceeded(self, auto_retry, mock_git_helper):
        """测试拉取超过最大重试次数。"""
        from src.core.git import GitOperationError
        mock_git_helper._run_git_command.side_effect = GitOperationError("Connection reset")
        auto_retry.config.max_retries = 2
        auto_retry.config.verbose = False
        
        with patch('time.sleep'):
            result = auto_retry.pull_with_retry()
        
        assert result["success"] is False
        assert result["attempts"] == 2

    def test_load_state_no_file(self, auto_retry):
        """测试加载状态（文件不存在）。"""
        state = auto_retry._load_state()
        assert state == {}

    def test_save_state(self, auto_retry, temp_dir):
        """测试保存状态。"""
        with patch('src.core.auto_retry.save_yaml') as mock_save:
            auto_retry._save_state({"test": "value"})
            mock_save.assert_called_once()


class TestAutoRetryModule:
    """智能重试模块测试。"""

    def test_module_importable(self):
        """测试模块可导入。"""
        from src.core import auto_retry
        assert hasattr(auto_retry, 'AutoRetry')
        assert hasattr(auto_retry, 'AutoRetryConfig')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
