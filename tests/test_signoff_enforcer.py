"""SignoffEnforcer 测试用例

FR-GIT-002: Git提交前强制验证签署是否完整
"""
import pytest
import tempfile
from pathlib import Path
from src.core.signoff_enforcer import SignoffEnforcer, SignoffNotFoundError, SignoffIncompleteError


class TestSignoffEnforcer:
    """SignoffEnforcer 测试类"""

    @pytest.fixture
    def temp_state_dir(self):
        """创建临时状态目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_dir = Path(tmpdir) / "state"
            state_dir.mkdir()
            yield state_dir

    @pytest.fixture
    def enforcer(self, temp_state_dir):
        """创建 SignoffEnforcer 实例"""
        return SignoffEnforcer(str(temp_state_dir))

    @pytest.fixture
    def doc_with_signoff(self, temp_state_dir):
        """创建带签署文件的文档"""
        doc = temp_state_dir / "test_doc.md"
        doc.write_text("# Test Document")
        signoff = temp_state_dir / "test_doc_signoff.md"
        signoff.write_text("## 签署\n\n| 角色 | 确认 |\n|------|------|\n| Agent 1 | ✅ |\n| Agent 2 | ✅ |")
        return doc

    @pytest.fixture
    def doc_without_signoff(self, temp_state_dir):
        """创建不带签署文件的文档"""
        doc = temp_state_dir / "test_doc.md"
        doc.write_text("# Test Document")
        return doc

    @pytest.fixture
    def doc_partial_signoff(self, temp_state_dir):
        """创建部分签署的文档"""
        doc = temp_state_dir / "test_doc.md"
        doc.write_text("# Test Document")
        signoff = temp_state_dir / "test_doc_signoff.md"
        signoff.write_text("## 签署\n\n| 角色 | 确认 |\n|------|------|\n| Agent 1 | ✅ |\n| Agent 2 | 待签署 |")
        return doc

    def test_check_signoff_status_not_found(self, enforcer, temp_state_dir):
        """TC-SIGNOFF-001: 文档不存在"""
        with pytest.raises(SignoffNotFoundError):
            enforcer.check_signoff_status(str(temp_state_dir / "nonexistent.md"))

    def test_check_signoff_status_no_signoff_file(self, enforcer, doc_without_signoff):
        """TC-SIGNOFF-002: 无签署文件"""
        status = enforcer.check_signoff_status(str(doc_without_signoff))
        assert status["complete"] == False
        assert "signoff文件不存在" in status["missing_signers"]

    def test_check_signoff_status_complete(self, enforcer, doc_with_signoff):
        """TC-SIGNOFF-003: 签署完整"""
        status = enforcer.check_signoff_status(str(doc_with_signoff))
        assert status["complete"] == True
        assert status["missing_signers"] == []

    def test_check_signoff_status_partial(self, enforcer, doc_partial_signoff):
        """TC-SIGNOFF-004: 部分签署"""
        status = enforcer.check_signoff_status(str(doc_partial_signoff))
        assert status["complete"] == False
        assert "Agent 2" in status["missing_signers"]

    def test_enforce_signoff_pass(self, enforcer, doc_with_signoff):
        """TC-SIGNOFF-005: 签署检查通过"""
        passed, msg = enforcer.enforce_signoff(str(doc_with_signoff))
        assert passed == True
        assert msg == "签署完整"

    def test_enforce_signoff_fail(self, enforcer, doc_without_signoff):
        """TC-SIGNOFF-006: 签署检查失败"""
        passed, msg = enforcer.enforce_signoff(str(doc_without_signoff))
        assert passed == False
        assert "signoff文件不存在" in msg

    def test_enforce_signoff_force(self, enforcer, doc_without_signoff):
        """TC-SIGNOFF-007: 强制跳过签署检查"""
        passed, msg = enforcer.enforce_signoff(str(doc_without_signoff), force=True)
        assert passed == False
        assert "警告" in msg
        assert "强制跳过签署检查" in msg

    def test_is_urgent_case_bug_fix(self, enforcer):
        """TC-SIGNOFF-008: Bug修复是紧急情况"""
        is_urgent, reason = enforcer.is_urgent_case("fix bug")
        assert is_urgent == True
        assert reason == "bug_fix"

    def test_is_urgent_case_security(self, enforcer):
        """TC-SIGNOFF-009: 安全补丁是紧急情况"""
        is_urgent, reason = enforcer.is_urgent_case("security patch")
        assert is_urgent == True
        assert reason == "security_patch"

    def test_is_urgent_case_hot_fix(self, enforcer):
        """TC-SIGNOFF-010: 热修复是紧急情况"""
        is_urgent, reason = enforcer.is_urgent_case("hot fix")
        assert is_urgent == True
        assert reason == "bug_fix"

    def test_is_urgent_case_docs(self, enforcer):
        """TC-SIGNOFF-011: 文档更正不是紧急情况"""
        is_urgent, reason = enforcer.is_urgent_case("documentation update")
        assert is_urgent == False
        assert reason == "非紧急情况"

    def test_is_urgent_case_feature(self, enforcer):
        """TC-SIGNOFF-012: 功能增强不是紧急情况"""
        is_urgent, reason = enforcer.is_urgent_case("new feature")
        assert is_urgent == False
        assert reason == "feature"

    def test_log_force_commit(self, enforcer, temp_state_dir):
        """TC-SIGNOFF-013: 记录强制提交日志"""
        doc_path = temp_state_dir / "test.md"
        doc_path.write_text("test")
        enforcer.log_force_commit(str(doc_path), "测试原因")

        log_file = temp_state_dir / "force_commit_log.yaml"
        assert log_file.exists()

    def test_urgent_case_examples(self, enforcer):
        """TC-SIGNOFF-014: 紧急情况示例"""
        for case, config in SignoffEnforcer.URGENT_CASES.items():
            assert "examples" in config
            assert "allow_force" in config
            assert isinstance(config["examples"], list)
            assert isinstance(config["allow_force"], bool)
