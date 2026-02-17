"""
v2.3.1 单元测试

测试TODO编号优化、来源标签、模板系统、Agent注册表、Git同步、ACK确认、合规检查功能
"""

import os
import sys
import tempfile
import shutil
import pytest
from pathlib import Path

# 添加src到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.todo_id_generator import TodoIdGenerator
from src.core.source_tag import SourceTag
from src.core.todo_template import TodoTemplate
from src.core.agent_registry import AgentRegistry
from src.core.git_sync import GitSync
from src.core.ack_confirm import ACKConfirm
from src.core.compliance_checker import ComplianceChecker


class TestTodoIdGenerator:
    """TodoIdGenerator测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def generator(self, temp_dir):
        """创建生成器实例"""
        state_file = os.path.join(temp_dir, "project_state.yaml")
        return TodoIdGenerator(state_file=state_file)
    
    def test_generate_new_format(self, generator, temp_dir):
        """TC-TODO-001: 生成新格式TODO编号"""
        result = generator.generate("1", "2")
        assert result == "TODO-1to2-001"
        assert "1to2" in result
    
    def test_generate_increment(self, generator, temp_dir):
        """TC-TODO-002: 编号自增"""
        id1 = generator.generate("1", "2")
        id2 = generator.generate("1", "2")
        assert id1 != id2
        assert "001" in id1
        assert "002" in id2
    
    def test_generate_different_receiver(self, generator, temp_dir):
        """TC-TODO-003: 不同接收者独立编号"""
        id1 = generator.generate("1", "2")
        id2 = generator.generate("1", "1")
        assert id1 != id2
        assert "1to2" in id1
        assert "1to1" in id2
    
    def test_parse_new_format(self, generator):
        """TC-TODO-004: 解析新格式编号"""
        result = generator.parse("TODO-1to2-003")
        assert result["creator"] == "1"
        assert result["receiver"] == "2"
        assert result["seq"] == 3
        assert result["is_legacy"] is False
    
    def test_parse_legacy_format(self, generator):
        """TC-TODO-005: 解析旧格式编号"""
        result = generator.parse("TODO-1-005")
        assert result["creator"] == "1"
        assert result["receiver"] == "1"
        assert result["seq"] == 5
        assert result["is_legacy"] is True
    
    def test_is_legacy_format(self, generator):
        """TC-TODO-006: 判断是否为旧格式"""
        assert generator.is_legacy_format("TODO-1-001") is True
        assert generator.is_legacy_format("TODO-1to2-001") is False
        assert generator.is_legacy_format("INVALID") is False


class TestSourceTag:
    """SourceTag测试类"""
    
    @pytest.fixture
    def source_tag(self):
        """创建SourceTag实例"""
        return SourceTag()
    
    def test_validate_valid_source(self, source_tag):
        """TC-SOURCE-001: 验证有效来源"""
        assert source_tag.validate("BUG") is True
        assert source_tag.validate("REQUIREMENT") is True
        assert source_tag.validate("FEEDBACK") is True
        assert source_tag.validate("MANUAL") is True
    
    def test_validate_invalid_source(self, source_tag):
        """TC-SOURCE-002: 验证无效来源"""
        assert source_tag.validate("INVALID") is False
        assert source_tag.validate("") is False
    
    def test_get_source_from_context_bug(self, source_tag):
        """TC-SOURCE-003: 从上下文推断BUG来源"""
        assert source_tag.get_source_from_context("修复BUG-001") == "BUG"
        assert source_tag.get_source_from_context("fix error") == "BUG"
    
    def test_get_source_from_context_requirement(self, source_tag):
        """TC-SOURCE-004: 从上下文推断REQUIREMENT来源"""
        assert source_tag.get_source_from_context("实现需求") == "REQUIREMENT"
        assert source_tag.get_source_from_context("implement feature") == "REQUIREMENT"
    
    def test_get_source_from_context_feedback(self, source_tag):
        """TC-SOURCE-005: 从上下文推断FEEDBACK来源"""
        assert source_tag.get_source_from_context("用户反馈") == "FEEDBACK"
        assert source_tag.get_source_from_context("feedback") == "FEEDBACK"
    
    def test_get_source_from_context_manual(self, source_tag):
        """TC-SOURCE-006: 默认推断为MANUAL"""
        assert source_tag.get_source_from_context("其他内容") == "MANUAL"
    
    def test_normalize(self, source_tag):
        """TC-SOURCE-007: 标准化来源名称"""
        assert source_tag.normalize("bug") == "BUG"
        assert source_tag.normalize("BUG") == "BUG"
        assert source_tag.normalize("invalid") == "MANUAL"


class TestTodoTemplate:
    """TodoTemplate测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def template(self, temp_dir):
        """创建Template实例"""
        config_file = os.path.join(temp_dir, "templates.yaml")
        return TodoTemplate(config_file=config_file)
    
    def test_get_template(self, template):
        """TC-TEMPLATE-001: 获取模板"""
        tmpl = template.get_template("BUG_FIX")
        assert tmpl is not None
        assert "required_fields" in tmpl
    
    def test_list_templates(self, template):
        """TC-TEMPLATE-002: 列出所有模板"""
        templates = template.list_templates()
        assert "REQUIREMENT" in templates
        assert "BUG_FIX" in templates
        assert "MANUAL" in templates
    
    def test_apply_template(self, template):
        """TC-TEMPLATE-003: 应用模板"""
        result = template.apply("BUG_FIX", {"content": "test"})
        assert "content" in result
    
    def test_validate_required_fields(self, template):
        """TC-TEMPLATE-004: 验证必填字段"""
        valid, missing = template.validate_required_fields("BUG_FIX", {"bug_id": "123", "root_cause": "cause"})
        assert valid is True
        assert len(missing) == 0
    
    def test_validate_required_fields_missing(self, template):
        """TC-TEMPLATE-005: 验证必填字段缺失"""
        valid, missing = template.validate_required_fields("BUG_FIX", {"bug_id": "123"})
        assert valid is False
        assert "root_cause" in missing


class TestAgentRegistry:
    """AgentRegistry测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def registry(self, temp_dir):
        """创建Registry实例"""
        state_file = os.path.join(temp_dir, "project_state.yaml")
        return AgentRegistry(state_file=state_file)
    
    def test_register_agent(self, registry):
        """TC-AGENT-001: 注册Agent"""
        result = registry.register("agent1", "DEVELOPMENT_LEAD", "internal")
        assert result is True
        agent = registry.get_agent("agent1")
        assert agent is not None
        assert agent["role"] == "DEVELOPMENT_LEAD"
    
    def test_register_invalid_role(self, registry):
        """TC-AGENT-002: 注册无效角色"""
        result = registry.register("agent1", "INVALID_ROLE", "internal")
        assert result is False
    
    def test_list_agents(self, registry):
        """TC-AGENT-003: 列出所有Agent"""
        registry.register("agent1", "DEVELOPMENT_LEAD")
        registry.register("agent2", "PRODUCT_MANAGER")
        agents = registry.list_agents()
        assert len(agents) == 2
    
    def test_can_unregister_no_todos(self, registry):
        """TC-AGENT-004: 无pending TODO时可以注销"""
        registry.register("agent1", "DEVELOPMENT_LEAD")
        assert registry.can_unregister("agent1") is True
    
    def test_can_unregister_with_pending_todos(self, temp_dir):
        """TC-AGENT-005: 有pending TODO时不能注销"""
        state_file = os.path.join(temp_dir, "project_state.yaml")
        registry = AgentRegistry(state_file=state_file)
        registry.register("agent1", "DEVELOPMENT_LEAD")
        
        # 写入一个有pending TODO的状态
        import yaml
        with open(state_file, 'w') as f:
            yaml.safe_dump({
                "agents": {"agent1": {"id": "agent1", "role": "DEVELOPMENT_LEAD"}},
                "todos": [{"id": "TODO-1-001", "receiver": "agent1", "status": "pending"}]
            }, f)
        
        # 重新创建registry实例
        registry = AgentRegistry(state_file=state_file)
        assert registry.can_unregister("agent1") is False


class TestComplianceChecker:
    """ComplianceChecker测试类"""
    
    @pytest.fixture
    def checker(self):
        """创建Checker实例"""
        return ComplianceChecker(current_agent="1")
    
    def test_check_new_format_valid(self, checker):
        """TC-COMP-001: 检查新格式编号有效"""
        valid, msg = checker.check_todo_create({"id": "TODO-1to2-001"})
        assert valid is True
        assert msg == ""
    
    def test_check_legacy_format_valid(self, checker):
        """TC-COMP-002: 检查旧格式编号有效"""
        valid, msg = checker.check_todo_create({"id": "TODO-1-001"})
        assert valid is True
    
    def test_check_invalid_format(self, checker):
        """TC-COMP-003: 检查无效格式"""
        valid, msg = checker.check_todo_create({"id": "INVALID"})
        assert valid is False
        assert "无效" in msg
    
    def test_check_creator_receiver_rule(self, checker):
        """TC-COMP-004: 检查创建者/接收者规则"""
        # Agent1只能创建给自己或Agent2
        checker1 = ComplianceChecker(current_agent="1")
        valid, _ = checker1.check_todo_create({"id": "TODO-1to2-001"})
        assert valid is True
        
        # Agent1不能创建给Agent3
        valid, msg = checker1.check_todo_create({"id": "TODO-1to3-001"})
        assert valid is False
    
    def test_validate_source(self, checker):
        """TC-COMP-005: 验证来源"""
        valid, _ = checker.validate_source("BUG")
        assert valid is True
        
        valid, _ = checker.validate_source("INVALID")
        assert valid is False
    
    def test_validate_role(self, checker):
        """TC-COMP-006: 验证角色"""
        valid, _ = checker.validate_role("DEVELOPMENT_LEAD")
        assert valid is True
        
        valid, _ = checker.validate_role("INVALID")
        assert valid is False


class TestGitSync:
    """GitSync测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def git_sync(self, temp_dir):
        """创建GitSync实例"""
        config_file = os.path.join(temp_dir, "git_sync.yaml")
        return GitSync(config_file=config_file)
    
    def test_default_config(self, git_sync):
        """TC-GIT-001: 默认配置"""
        assert git_sync.is_enabled() is False
        assert "origin" in git_sync.get_remotes()
    
    def test_enable_disable(self, git_sync):
        """TC-GIT-002: 启用/禁用同步"""
        git_sync.enable()
        assert git_sync.is_enabled() is True
        
        git_sync.disable()
        assert git_sync.is_enabled() is False
    
    def test_add_remove_remote(self, git_sync):
        """TC-GIT-003: 添加/移除远程仓库"""
        git_sync.add_remote("backup")
        assert "backup" in git_sync.get_remotes()
        
        git_sync.remove_remote("backup")
        assert "backup" not in git_sync.get_remotes()


class TestACKConfirm:
    """ACKConfirm测试类"""
    
    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def ack_confirm(self, temp_dir):
        """创建ACKConfirm实例"""
        state_file = os.path.join(temp_dir, "project_state.yaml")
        return ACKConfirm(state_file=state_file)
    
    def test_is_acknowledged_no_todo(self, ack_confirm):
        """TC-ACK-001: 查询不存在的TODO"""
        assert ack_confirm.is_acknowledged("TODO-1-001") is False
    
    def test_get_ack_status_not_found(self, ack_confirm):
        """TC-ACK-002: 获取不存在的TODO状态"""
        status = ack_confirm.get_ack_status("TODO-1-001")
        assert status["acknowledged"] is False
        assert status["status"] == "not_found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
