"""
测试用例: BUG-20260219-009 - 验收流程自动触发signoff机制
"""

import pytest


class MockSignoffEngine:
    """模拟SignoffEngine用于测试"""
    
    STAGE_CONFIG = {
        'requirements': {'agent1_role': '产品经理', 'agent2_role': '开发'},
        'design': {'agent1_role': '产品经理', 'agent2_role': '开发'},
        'test': {'agent1_role': '产品经理', 'agent2_role': '开发'}
    }
    
    def __init__(self):
        self.state = {}
    
    def get_signoff_summary(self, stage):
        return self.state.get(stage, {
            'pm_signoff': False,
            'dev_signoff': False,
            'both_signed': False
        })
    
    def auto_trigger_signoff(self, stage, test_results):
        """测试通过后自动触发signoff流程"""
        if test_results.get('failed', 0) > 0:
            return {
                'triggered': False,
                'action': 'none',
                'message': f'测试有{test_results["failed"]}个失败，无法触发signoff'
            }
        
        if test_results.get('passed', 0) == 0:
            return {
                'triggered': False,
                'action': 'none',
                'message': '没有通过的测试'
            }
        
        coverage = test_results.get('coverage', 0)
        min_coverage = test_results.get('min_coverage', 80)
        
        if coverage < min_coverage:
            return {
                'triggered': False,
                'action': 'none',
                'message': f'代码覆盖率{coverage}%低于最低要求{min_coverage}%'
            }
        
        summary = self.get_signoff_summary(stage)
        if summary.get('both_signed'):
            return {
                'triggered': False,
                'action': 'none',
                'message': f'{stage}阶段已经完成签署'
            }
        
        pending_signers = []
        if not summary.get('pm_signoff'):
            pending_signers.append('agent1')
        if not summary.get('dev_signoff'):
            pending_signers.append('agent2')
        
        return {
            'triggered': True,
            'action': 'create_signoff_todo',
            'stage': stage,
            'pending_signers': pending_signers,
            'message': f'测试通过，准备签署{stage}阶段，待签署: {", ".join(pending_signers)}'
        }


class TestAutoSignoffTrigger:
    """测试自动触发signoff机制"""
    
    def setup_method(self):
        self.engine = MockSignoffEngine()
    
    def test_auto_trigger_all_passed(self):
        """TC-AUTO-001: 测试全部通过时触发signoff"""
        test_results = {'passed': 123, 'failed': 0, 'coverage': 93}
        
        result = self.engine.auto_trigger_signoff('requirements', test_results)
        
        assert result['triggered'] is True
        assert result['action'] == 'create_signoff_todo'
        assert 'agent1' in result['pending_signers']
        assert 'agent2' in result['pending_signers']
    
    def test_auto_trigger_with_failures(self):
        """TC-AUTO-002: 测试有失败时不触发signoff"""
        test_results = {'passed': 100, 'failed': 5, 'coverage': 90}
        
        result = self.engine.auto_trigger_signoff('design', test_results)
        
        assert result['triggered'] is False
        assert '5个失败' in result['message']
    
    def test_auto_trigger_coverage_too_low(self):
        """TC-AUTO-003: 覆盖率低于阈值时不触发"""
        test_results = {'passed': 100, 'failed': 0, 'coverage': 60}
        
        result = self.engine.auto_trigger_signoff('test', test_results)
        
        assert result['triggered'] is False
        assert '60%' in result['message']
        assert '80%' in result['message']
    
    def test_auto_trigger_already_signed(self):
        """TC-AUTO-004: 已签署时不触发"""
        self.engine.state['requirements'] = {
            'pm_signoff': True,
            'dev_signoff': True,
            'both_signed': True
        }
        
        test_results = {'passed': 100, 'failed': 0, 'coverage': 90}
        
        result = self.engine.auto_trigger_signoff('requirements', test_results)
        
        assert result['triggered'] is False
        assert 'completed' in result['message'].lower() or '完成' in result['message']
    
    def test_auto_trigger_partial_signoff(self):
        """TC-AUTO-005: 部分签署时只通知未签署者"""
        self.engine.state['design'] = {
            'pm_signoff': True,
            'dev_signoff': False,
            'both_signed': False
        }
        
        test_results = {'passed': 50, 'failed': 0, 'coverage': 85}
        
        result = self.engine.auto_trigger_signoff('design', test_results)
        
        assert result['triggered'] is True
        assert 'agent1' not in result['pending_signers']
        assert 'agent2' in result['pending_signers']
    
    def test_auto_trigger_no_passed(self):
        """TC-AUTO-006: 没有通过的测试时不触发"""
        test_results = {'passed': 0, 'failed': 10, 'coverage': 0}
        
        result = self.engine.auto_trigger_signoff('test', test_results)
        
        assert result['triggered'] is False
        assert 'failed' in result['message'].lower() or '0' in result['message']
    
    def test_auto_trigger_custom_min_coverage(self):
        """TC-AUTO-007: 自定义覆盖率阈值"""
        test_results = {'passed': 100, 'failed': 0, 'coverage': 75, 'min_coverage': 70}
        
        result = self.engine.auto_trigger_signoff('requirements', test_results)
        
        assert result['triggered'] is True


class TestSignoffWorkflow:
    """测试signoff工作流"""
    
    def test_requirements_signoff_flow(self):
        """TC-FLOW-001: requirements阶段signoff流程"""
        engine = MockSignoffEngine()
        
        # 1. 测试通过
        test_results = {'passed': 123, 'failed': 0, 'coverage': 93}
        result = engine.auto_trigger_signoff('requirements', test_results)
        
        assert result['triggered'] is True
        assert result['stage'] == 'requirements'
    
    def test_design_signoff_flow(self):
        """TC-FLOW-002: design阶段signoff流程"""
        engine = MockSignoffEngine()
        
        test_results = {'passed': 80, 'failed': 0, 'coverage': 88}
        result = engine.auto_trigger_signoff('design', test_results)
        
        assert result['triggered'] is True
        assert result['stage'] == 'design'
    
    def test_test_signoff_flow(self):
        """TC-FLOW-003: test阶段signoff流程"""
        engine = MockSignoffEngine()
        
        test_results = {'passed': 200, 'failed': 0, 'coverage': 95}
        result = engine.auto_trigger_signoff('test', test_results)
        
        assert result['triggered'] is True
        assert result['stage'] == 'test'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
