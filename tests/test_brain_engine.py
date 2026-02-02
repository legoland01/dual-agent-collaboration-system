"""BrainEngine 单元测试。"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.brain_engine import (
    BrainEngine, Rule, Condition, RuleSet,
    AgentType, ActionType, BrainEngineError, RuleLoadError, RuleExecutionError
)


class TestBrainEngineExceptions:
    """大脑引擎异常测试。"""

    def test_brain_engine_error(self):
        """测试大脑引擎异常。"""
        with pytest.raises(BrainEngineError):
            raise BrainEngineError("Test error")

    def test_rule_load_error(self):
        """测试规则加载异常。"""
        with pytest.raises(RuleLoadError):
            raise RuleLoadError("Failed to load rules")

    def test_rule_execution_error(self):
        """测试规则执行异常。"""
        with pytest.raises(RuleExecutionError):
            raise RuleExecutionError("Failed to execute rule")


class TestAgentType:
    """Agent类型枚举测试。"""

    def test_agent_type_values(self):
        """测试Agent类型值。"""
        assert AgentType.AGENT_1.value == "agent1"
        assert AgentType.AGENT_2.value == "agent2"


class TestActionType:
    """动作类型枚举测试。"""

    def test_action_type_values(self):
        """测试动作类型值。"""
        assert ActionType.CREATE_REQUIREMENTS.value == "create_requirements"
        assert ActionType.REVIEW_REQUIREMENTS.value == "review_requirements"
        assert ActionType.IMPLEMENT_CODE.value == "implement_code"


class TestCondition:
    """规则条件测试。"""

    def test_condition_phase_equals_true(self):
        """测试阶段相等条件（True）。"""
        condition = Condition("phase_equals", {"value": "development"})
        context = {"phase": "development"}
        assert condition.evaluate(context) is True

    def test_condition_phase_equals_false(self):
        """测试阶段相等条件（False）。"""
        condition = Condition("phase_equals", {"value": "development"})
        context = {"phase": "testing"}
        assert condition.evaluate(context) is False

    def test_condition_phase_in(self):
        """测试阶段列表条件。"""
        condition = Condition("phase_in", {"values": ["development", "testing"]})
        assert condition.evaluate({"phase": "development"}) is True
        assert condition.evaluate({"phase": "testing"}) is True
        assert condition.evaluate({"phase": "deployment"}) is False

    def test_condition_signoff_complete(self):
        """测试签署完成条件。"""
        condition = Condition("signoff_complete", {"stage": "requirements"})
        context = {
            "signoff": {
                "requirements": {
                    "pm_signoff": True,
                    "dev_signoff": True
                }
            }
        }
        assert condition.evaluate(context) is True

    def test_condition_signoff_incomplete(self):
        """测试签署未完成条件。"""
        condition = Condition("signoff_complete", {"stage": "requirements"})
        context = {
            "signoff": {
                "requirements": {
                    "pm_signoff": True,
                    "dev_signoff": False
                }
            }
        }
        assert condition.evaluate(context) is False

    def test_condition_no_pending_issues_true(self):
        """测试无待处理问题条件（True）。"""
        condition = Condition("no_pending_issues", {})
        assert condition.evaluate({"pending_issues": 0}) is True

    def test_condition_no_pending_issues_false(self):
        """测试无待处理问题条件（False）。"""
        condition = Condition("no_pending_issues", {})
        assert condition.evaluate({"pending_issues": 5}) is False

    def test_condition_file_exists(self):
        """测试文件存在条件。"""
        condition = Condition("file_exists", {"path": "requirements.txt"})
        context = {"file_exists": {"requirements.txt": True}}
        assert condition.evaluate(context) is True

    def test_condition_custom_function(self):
        """测试自定义条件。"""
        custom_func = lambda ctx: ctx.get("test_value") == 42
        condition = Condition("custom", {"function": custom_func})
        assert condition.evaluate({"test_value": 42}) is True
        assert condition.evaluate({"test_value": 10}) is False

    def test_condition_default(self):
        """测试默认条件（返回True）。"""
        condition = Condition("unknown_type", {})
        assert condition.evaluate({}) is True


class TestRule:
    """行为规则测试。"""

    @pytest.fixture
    def sample_rule(self):
        """创建示例规则。"""
        return Rule(
            id="test-rule",
            name="Test Rule",
            agent_type=AgentType.AGENT_1,
            conditions=[Condition("phase_equals", {"value": "development"})],
            action=ActionType.IMPLEMENT_CODE,
            priority=100,
            enabled=True,
            description="Test rule description"
        )

    def test_rule_matches_enabled(self, sample_rule):
        """测试规则匹配（启用状态）。"""
        context = {
            "agent_type": "agent1",
            "phase": "development"
        }
        assert sample_rule.matches(context) is True

    def test_rule_matches_disabled(self, sample_rule):
        """测试规则匹配（禁用状态）。"""
        sample_rule.enabled = False
        context = {
            "agent_type": "agent1",
            "phase": "development"
        }
        assert sample_rule.matches(context) is False

    def test_rule_matches_wrong_agent(self, sample_rule):
        """测试规则匹配（错误的Agent）。"""
        context = {
            "agent_type": "agent2",
            "phase": "development"
        }
        assert sample_rule.matches(context) is False

    def test_rule_matches_condition_failed(self, sample_rule):
        """测试规则匹配（条件不满足）。"""
        context = {
            "agent_type": "agent1",
            "phase": "testing"
        }
        assert sample_rule.matches(context) is False

    def test_rule_matches_no_conditions(self):
        """测试规则匹配（无条件）。"""
        rule = Rule(
            id="test-rule",
            name="Test Rule",
            agent_type=AgentType.AGENT_1,
            action=ActionType.WAIT
        )
        context = {"agent_type": "agent1"}
        assert rule.matches(context) is True


class TestRuleSet:
    """规则集测试。"""

    @pytest.fixture
    def rule_set(self):
        """创建规则集。"""
        return RuleSet(
            name="test-ruleset",
            version="1.0.0",
            rules=[
                Rule(id="r1", name="Rule 1", agent_type=AgentType.AGENT_1, action=ActionType.WAIT, priority=100),
                Rule(id="r2", name="Rule 2", agent_type=AgentType.AGENT_1, action=ActionType.WAIT, priority=50),
                Rule(id="r3", name="Rule 3", agent_type=AgentType.AGENT_2, action=ActionType.WAIT, priority=100),
            ]
        )

    def test_get_rules_for_agent(self, rule_set):
        """测试获取指定Agent的规则。"""
        agent1_rules = rule_set.get_rules_for_agent(AgentType.AGENT_1)
        assert len(agent1_rules) == 2
        
        agent2_rules = rule_set.get_rules_for_agent(AgentType.AGENT_2)
        assert len(agent2_rules) == 1

    def test_get_matching_rules(self, rule_set):
        """测试获取匹配的规则。"""
        context = {"agent_type": "agent1"}
        matching = rule_set.get_matching_rules(context)
        assert len(matching) == 2
        assert matching[0].priority == 100

    def test_get_matching_rules_sorted_by_priority(self, rule_set):
        """测试获取匹配的规则（按优先级排序）。"""
        context = {"agent_type": "agent1"}
        matching = rule_set.get_matching_rules(context)
        assert matching[0].priority >= matching[1].priority


class TestBrainEngine:
    """大脑引擎测试类。"""

    def test_init_default_rules(self):
        """测试初始化（加载默认规则）。"""
        engine = BrainEngine()
        assert "default_agent1" in engine.rule_sets
        assert "default_agent2" in engine.rule_sets

    def test_init_custom_rules_path(self):
        """测试初始化（自定义规则路径）。"""
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode='w', delete=False) as f:
            f.write("name: custom-rules\nversion: 1.0.0\nrules: []")
            f.flush()
            
            try:
                engine = BrainEngine(rules_path=f.name)
                assert "custom-rules" in engine.rule_sets
            finally:
                os.unlink(f.name)

    def test_init_nonexistent_rules_path(self):
        """测试初始化（不存在的规则路径）。"""
        engine = BrainEngine(rules_path="/nonexistent/path/rules.yaml")
        assert "default_agent1" in engine.rule_sets

    def test_load_rules(self):
        """测试加载规则。"""
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode='w', delete=False) as f:
            yaml_content = """
name: loaded-rules
version: 2.0.0
rules:
  - id: loaded-rule
    name: Loaded Rule
    agent_type: agent1
    action: wait
    priority: 50
"""
            f.write(yaml_content)
            f.flush()
            
            try:
                engine = BrainEngine()
                rule_set = engine.load_rules(f.name)
                assert rule_set.name == "loaded-rules"
                assert len(rule_set.rules) == 1
            finally:
                os.unlink(f.name)

    def test_load_rules_nonexistent_file(self):
        """测试加载规则（文件不存在）。"""
        engine = BrainEngine()
        rule_set = engine.load_rules("/nonexistent/rules.yaml")
        assert rule_set is not None

    def test_get_action_agent1(self):
        """测试获取动作（Agent1）。"""
        engine = BrainEngine()
        action, rule = engine.get_action("agent1", "project_init")
        assert action == ActionType.CREATE_REQUIREMENTS

    def test_get_action_agent2(self):
        """测试获取动作（Agent2）。"""
        engine = BrainEngine()
        action, rule = engine.get_action("agent2", "requirements_draft")
        assert action == ActionType.REVIEW_REQUIREMENTS

    def test_get_action_no_match(self):
        """测试获取动作（无匹配规则）。"""
        engine = BrainEngine()
        action, rule = engine.get_action("agent1", "completed")
        assert action == ActionType.WAIT

    def test_get_action_with_signoff(self):
        """测试获取动作（带签署条件）。"""
        engine = BrainEngine()
        signoff = {
            "requirements": {
                "pm_signoff": True,
                "dev_signoff": True
            }
        }
        action, rule = engine.get_action("agent1", "requirements_review", signoff=signoff)
        assert action == ActionType.SIGNOFF_REQUIREMENTS

    def test_update_context(self):
        """测试更新上下文。"""
        engine = BrainEngine()
        engine.update_context(phase="development", test="value")
        assert engine.current_context["phase"] == "development"
        assert engine.current_context["test"] == "value"

    def test_get_action_with_context(self):
        """测试获取动作（使用上下文）。"""
        engine = BrainEngine()
        engine.update_context(agent_type="agent1", phase="project_init")
        action, rule = engine.get_action(
            engine.current_context.get("agent_type", "agent1"),
            engine.current_context.get("phase", "project_init")
        )
        assert action == ActionType.CREATE_REQUIREMENTS


class TestBrainEngineModule:
    """大脑引擎模块测试。"""

    def test_module_importable(self):
        """测试模块可导入。"""
        from src.core import brain_engine
        assert hasattr(brain_engine, 'BrainEngine')
        assert hasattr(brain_engine, 'Rule')
        assert hasattr(brain_engine, 'Condition')


class TestBrainEngineEdgeCases:
    """大脑引擎边缘情况测试。"""

    def test_load_rules_file_not_exists(self):
        """测试加载不存在的规则文件。"""
        engine = BrainEngine()
        rule_set = engine.load_rules("/nonexistent/rules.yaml")
        assert rule_set is not None

    def test_load_rules_empty_file(self):
        """测试加载空规则文件。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            f.flush()
            
            engine = BrainEngine()
            with pytest.raises(RuleLoadError):
                engine.load_rules(f.name)
            
            import os
            os.unlink(f.name)

    def test_load_rules_invalid_yaml(self):
        """测试加载无效YAML规则文件。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content [")
            f.flush()
            
            engine = BrainEngine()
            with pytest.raises(RuleLoadError):
                engine.load_rules(f.name)
            
            import os
            os.unlink(f.name)

    def test_load_rules_valid_file(self):
        """测试加载有效规则文件。"""
        rules_content = """
name: test_rules
version: 1.0.0
rules:
  - id: test-rule
    name: Test Rule
    agent_type: agent1
    conditions:
      - type: phase_equals
        params:
          value: development
    action: implement_code
    priority: 100
    enabled: true
    description: Test rule
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(rules_content)
            f.flush()
            
            engine = BrainEngine()
            rule_set = engine.load_rules(f.name)
            assert rule_set is not None
            assert len(rule_set.rules) == 1
            assert rule_set.name == "test_rules"
            
            import os
            os.unlink(f.name)

    def test_condition_phase_equals_missing_value(self):
        """测试阶段相等条件（缺少值参数）。"""
        condition = Condition("phase_equals", {})
        assert condition.evaluate({"phase": "development"}) is False

    def test_condition_phase_in_missing_values(self):
        """测试阶段列表条件（缺少值列表参数）。"""
        condition = Condition("phase_in", {})
        assert condition.evaluate({"phase": "development"}) is False

    def test_condition_signoff_complete_missing_stage(self):
        """测试签署完成条件（缺少阶段参数）。"""
        condition = Condition("signoff_complete", {})
        assert condition.evaluate({}) is False

    def test_condition_file_exists_missing_path(self):
        """测试文件存在条件（缺少路径参数）。"""
        condition = Condition("file_exists", {})
        assert condition.evaluate({}) is False

    def test_init_with_existing_rules_path(self):
        """测试初始化（规则文件已存在）。"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("name: test\nversion: 1.0.0\nrules: []")
            f.flush()
            
            engine = BrainEngine(rules_path=f.name)
            assert "test" in engine.rule_sets
            
            import os
            os.unlink(f.name)

    def test_brain_engine_with_custom_rules_path(self):
        """测试大脑引擎（自定义规则路径）。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            rules_file = Path(tmpdir) / "custom_rules.yaml"
            rules_file.write_text("name: custom\nversion: 1.0.0\nrules: []")
            
            engine = BrainEngine(rules_path=str(rules_file))
            assert "custom" in engine.rule_sets


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
