"""v2.2.7 黑盒测试：CLI命令测试

覆盖 skill test、skill coverage、webhook init/start/stop/status 命令。
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from pathlib import Path


class TestSkillTestCommand:
    """skill test 命令测试"""

    def test_skill_test_help(self):
        """测试 help 输出"""
        from src.cli.skill_commands import skill_test

        runner = CliRunner()
        result = runner.invoke(skill_test, ['--help'])
        assert result.exit_code == 0
        assert '--skill' in result.output
        assert '--verbose' in result.output


class TestSkillCoverageCommand:
    """skill coverage 命令测试"""

    def test_skill_coverage_help(self):
        """测试 help 输出"""
        from src.cli.skill_commands import skill_coverage

        runner = CliRunner()
        result = runner.invoke(skill_coverage, ['--help'])
        assert result.exit_code == 0
        assert '--skill' in result.output
        assert '--threshold' in result.output


class TestWebhookInitCommand:
    """webhook init 命令测试"""

    def test_webhook_init_help(self):
        """测试 help 输出"""
        from src.cli.webhook_commands import webhook_init

        runner = CliRunner()
        result = runner.invoke(webhook_init, ['--help'])
        assert result.exit_code == 0
        assert '--force' in result.output


class TestWebhookStartCommand:
    """webhook start 命令测试"""

    def test_webhook_start_help(self):
        """测试 help 输出"""
        from src.cli.webhook_commands import webhook_start

        runner = CliRunner()
        result = runner.invoke(webhook_start, ['--help'])
        assert result.exit_code == 0
        assert '--port' in result.output


class TestWebhookStopCommand:
    """webhook stop 命令测试"""

    def test_webhook_stop_help(self):
        """测试 help 输出"""
        from src.cli.webhook_commands import webhook_stop

        runner = CliRunner()
        result = runner.invoke(webhook_stop, ['--help'])
        assert result.exit_code == 0
        assert '--help' in result.output


class TestWebhookStatusCommand:
    """webhook status 命令测试"""

    def test_webhook_status_help(self):
        """测试 help 输出"""
        from src.cli.webhook_commands import webhook_status

        runner = CliRunner()
        result = runner.invoke(webhook_status, ['--help'])
        assert result.exit_code == 0
        assert '--help' in result.output


class TestSkillEnforcerIntegration:
    """BUG-20260210-001 修复验证"""

    def test_todowrite_auto_check_skill(self):
        """验证 todowrite 命令自动检查Skill"""
        from src.cli.enhanced_commands import todowrite_command
        from src.core.skill_enforcer import SkillEnforcer
        from src.core.auto_checker import AutoChecker
        from click.testing import CliRunner
        from unittest.mock import patch, MagicMock

        with patch.object(SkillEnforcer, 'check_before_action') as mock_check:
            with patch.object(AutoChecker, 'check_all') as mock_checker:
                mock_check.return_value = {
                    "missing": [],
                    "suggestions": []
                }
                mock_checker.return_value = {
                    "valid": True,
                    "warnings": [],
                    "errors": []
                }

                runner = CliRunner()
                result = runner.invoke(todowrite_command, [
                    '--content', '测试任务',
                    '--test-mode'
                ])

                mock_check.assert_called_with("todowrite")

    def test_signoff_auto_check_skill(self):
        """验证 signoff 命令自动检查Skill"""
        from src.cli.main import main as cli_main
        from src.core.skill_enforcer import SkillEnforcer
        from click.testing import CliRunner
        from unittest.mock import patch, MagicMock

        with patch.object(SkillEnforcer, 'check_before_action') as mock_check:
            with patch('src.cli.main.StateManager') as mock_state:
                mock_check.return_value = {
                    "missing": [],
                    "suggestions": []
                }

                mock_state_instance = MagicMock()
                mock_state_instance.get_active_agent.return_value = 1
                mock_state.return_value = mock_state_instance

                runner = CliRunner()
                result = runner.invoke(cli_main, [
                    'signoff', 'requirements',
                    '--auto-check'
                ])

                mock_check.assert_called_with("signoff")

    def test_advance_auto_check_skill(self):
        """验证 advance 命令自动检查Skill"""
        from src.cli.main import main as cli_main
        from src.core.skill_enforcer import SkillEnforcer
        from click.testing import CliRunner
        from unittest.mock import patch, MagicMock

        with patch.object(SkillEnforcer, 'check_before_action') as mock_check:
            with patch('src.cli.main.PhaseAdvanceEngine') as mock_engine:
                mock_check.return_value = {
                    "missing": [],
                    "suggestions": []
                }

                mock_engine_instance = MagicMock()
                mock_engine_instance.check_and_advance.return_value = {
                    "advanced": False,
                    "reason": "未满足推进条件"
                }
                mock_engine.return_value = mock_engine_instance

                runner = CliRunner()
                result = runner.invoke(cli_main, [
                    'advance', '--check',
                    '--auto-check'
                ])

                mock_check.assert_called_with("phase_advance")


class TestEventListenerCrashRecovery:
    """EventListener 崩溃恢复测试"""

    def test_crash_recovery_policy_class_attributes(self):
        """测试崩溃恢复策略类属性"""
        from src.core.event_listener import CrashRecoveryPolicy

        assert CrashRecoveryPolicy.MAX_RETRIES == 3
        assert CrashRecoveryPolicy.BACKOFF_INTERVALS == [60, 300, 900]

    def test_crash_recovery_instance(self):
        """测试崩溃恢复实例"""
        from src.core.event_listener import EventListener, CrashRecoveryPolicy
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            listener = EventListener(str(Path(tmp)))
            policy = listener.crash_recovery
            assert isinstance(policy, CrashRecoveryPolicy)
            assert policy.retry_count == 0
            assert policy.should_retry() == True
            assert policy.get_backoff_interval() == 60  # 第一次重试

    def test_crash_recovery_retry_count(self):
        """测试崩溃恢复重试计数"""
        from src.core.event_listener import CrashRecoveryPolicy

        policy = CrashRecoveryPolicy()
        assert policy.retry_count == 0
        
        policy.record_retry()
        assert policy.retry_count == 1
        assert policy.should_retry() == True
        
        policy.record_retry()
        assert policy.retry_count == 2
        
        policy.record_retry()
        assert policy.retry_count == 3
        assert policy.should_retry() == False  # 已达到最大重试次数

    def test_crash_recovery_backoff_intervals(self):
        """测试崩溃恢复退避间隔"""
        from src.core.event_listener import CrashRecoveryPolicy

        policy = CrashRecoveryPolicy()
        
        assert policy.get_backoff_interval() == 60   # 第1次: 1分钟
        policy.record_retry()
        assert policy.get_backoff_interval() == 300  # 第2次: 5分钟
        policy.record_retry()
        assert policy.get_backoff_interval() == 900  # 第3次: 15分钟
        policy.record_retry()
        assert policy.get_backoff_interval() == 900  # 第4次+: 还是15分钟


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
