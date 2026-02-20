"""测试BUG-20260219-010: 测试通过后自动触发signoff的CLI集成"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner


class TestTodoCompleteWithSignoff:
    """测试todo complete命令与signoff集成"""

    def test_complete_with_signoff_flag(self):
        """测试带--signoff选项的todo complete"""
        from src.cli.todo_commands import todo_complete_command
        
        runner = CliRunner()
        
        with patch('src.core.todo_sync_manager.TodoSyncManager') as mock_sync:
            mock_instance = Mock()
            mock_instance.update_todo.return_value = True
            mock_sync.return_value = mock_instance
            
            with patch('src.core.state_manager.StateManager'):
                with patch('src.core.workflow.WorkflowEngine'):
                    with patch('src.core.signoff.SignoffEngine') as mock_signoff:
                        mock_signoff_instance = Mock()
                        mock_signoff_instance.auto_trigger_signoff.return_value = {
                            "triggered": True,
                            "action": "create_signoff_todo",
                            "message": "测试通过，准备签署test阶段"
                        }
                        mock_signoff_instance.create_signoff_todo_from_test.return_value = {
                            "created": True,
                            "message": "已创建signoff TODO"
                        }
                        mock_signoff.return_value = mock_signoff_instance
                        
                        result = runner.invoke(
                            todo_complete_command, 
                            ['TODO-1-001', '--signoff', '--test-results', '{"passed":10,"failed":0,"coverage":93}']
                        )
                        
                        assert '✅ TODO TODO-1-001 已标记为完成' in result.output
                        assert '🔔 自动触发signoff' in result.output

    def test_complete_without_signoff(self):
        """测试不带--signoff选项的todo complete"""
        from src.cli.todo_commands import todo_complete_command
        
        runner = CliRunner()
        
        with patch('src.core.todo_sync_manager.TodoSyncManager') as mock_sync:
            mock_instance = Mock()
            mock_instance.update_todo.return_value = True
            mock_sync.return_value = mock_instance
            
            result = runner.invoke(
                todo_complete_command, 
                ['TODO-1-001']
            )
            
            assert '✅ TODO TODO-1-001 已标记为完成' in result.output

    def test_complete_with_invalid_json(self):
        """测试带无效JSON的todo complete"""
        from src.cli.todo_commands import todo_complete_command
        
        runner = CliRunner()
        
        with patch('src.core.todo_sync_manager.TodoSyncManager') as mock_sync:
            mock_instance = Mock()
            mock_instance.update_todo.return_value = True
            mock_sync.return_value = mock_instance
            
            result = runner.invoke(
                todo_complete_command, 
                ['TODO-1-001', '--signoff', '--test-results', 'invalid-json']
            )
            
            assert '✅ TODO TODO-1-001 已标记为完成' in result.output

    def test_complete_without_test_results(self):
        """测试带--signoff但没有--test-results"""
        from src.cli.todo_commands import todo_complete_command
        
        runner = CliRunner()
        
        with patch('src.core.todo_sync_manager.TodoSyncManager') as mock_sync:
            mock_instance = Mock()
            mock_instance.update_todo.return_value = True
            mock_sync.return_value = mock_instance
            
            result = runner.invoke(
                todo_complete_command, 
                ['TODO-1-001', '--signoff']
            )
            
            assert '✅ TODO TODO-1-001 已标记为完成' in result.output
            assert '请同时提供 --test-results' in result.output


class TestAutoTriggerSignoffLogic:
    """测试自动触发signoff的业务逻辑"""

    def test_auto_trigger_with_low_coverage(self):
        """测试覆盖率过低时不触发signoff"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        
        state_manager.get_state.return_value = {
            "v2.3": {"signoffs": {"test": {"pm_signoff": None, "dev_signoff": None}}}
        }
        
        engine = SignoffEngine(state_manager, workflow_engine)
        
        test_results = {"passed": 10, "failed": 0, "coverage": 50}
        result = engine.auto_trigger_signoff("test", test_results)
        
        assert result["triggered"] == False
        assert "覆盖率" in result["message"]

    def test_auto_trigger_with_failures(self):
        """测试有失败测试时不触发signoff"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        
        engine = SignoffEngine(state_manager, workflow_engine)
        
        test_results = {"passed": 9, "failed": 1, "coverage": 93}
        result = engine.auto_trigger_signoff("test", test_results)
        
        assert result["triggered"] == False
        assert "失败" in result["message"]

    def test_auto_trigger_no_passed_tests(self):
        """测试没有通过的测试时不触发signoff"""
        from src.core.signoff import SignoffEngine
        
        state_manager = Mock()
        workflow_engine = Mock()
        
        engine = SignoffEngine(state_manager, workflow_engine)
        
        test_results = {"passed": 0, "failed": 0, "coverage": 0}
        result = engine.auto_trigger_signoff("test", test_results)
        
        assert result["triggered"] == False
        assert "没有通过的测试" in result["message"]
