"""
v2.2.12 部署自动化模块测试

测试用例：
- TC-001: VersionManager 版本号管理
- TC-002: PackageBuilder 包构建
- TC-003: PyPIUploader PyPI上传
- TC-004: GitPusher Git推送
- TC-005: DeployVerifier 验证器
- TC-006: StateUpdater 状态更新
- TC-007: DeploymentOrchestrator 编排器
"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestVersionManager:
    """VersionManager 测试"""

    @pytest.fixture
    def version_manager(self):
        """创建 VersionManager 实例（使用实际 pyproject.toml）"""
        from src.core.version_manager import VersionManager
        return VersionManager()

    def test_tc_001_get_current_version(self, version_manager):
        """
        TC-001: 读取当前版本号
        """
        version = version_manager.get_current_version()
        # 从pyproject.toml动态读取当前版本
        import re
        with open("pyproject.toml", "r") as f:
            content = f.read()
            match = re.search(r'version = "([^"]+)"', content)
            if match:
                expected_version = match.group(1)
                assert version == expected_version
            else:
                # 如果解析失败，只要version非空即可
                assert version and "." in version

    def test_tc_002_update_version(self, version_manager):
        """
        TC-002: 更新版本号
        """
        import re
        with open("pyproject.toml", "r") as f:
            content = f.read()
            match = re.search(r'version = "([^"]+)"', content)
            original_version = match.group(1) if match else "2.3.0"
        
        success = version_manager.update_version("99.99.99")
        assert success is True
        version = version_manager.get_current_version()
        assert version == "99.99.99"
        version_manager.update_version(original_version)

    def test_tc_003_validate_version_valid(self, version_manager):
        """
        TC-003: 验证有效版本号
        """
        is_valid, msg = version_manager.validate_version("2.2.12")
        assert is_valid is True
        assert msg == ""

    def test_tc_004_validate_version_invalid(self, version_manager):
        """
        TC-004: 验证无效版本号
        """
        is_valid, msg = version_manager.validate_version("invalid")
        assert is_valid is False
        assert "x.y.z" in msg


class TestPackageBuilder:
    """PackageBuilder 测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        if os.path.exists(temp):
            shutil.rmtree(temp)

    @pytest.fixture
    def package_builder(self, temp_dir):
        """创建 PackageBuilder 实例"""
        from src.core.package_builder import PackageBuilder
        return PackageBuilder(dist_dir=os.path.join(temp_dir, "dist"))

    def test_tc_005_clean_dist(self, package_builder, temp_dir):
        """
        TC-005: 清理构建目录
        """
        dist_path = os.path.join(temp_dir, "dist")
        os.makedirs(dist_path, exist_ok=True)
        with open(os.path.join(dist_path, "test.txt"), 'w') as f:
            f.write("test")

        success = package_builder.clean()
        assert success is True
        assert not os.path.exists(dist_path)

    def test_tc_006_verify_build_empty(self, package_builder):
        """
        TC-006: 验证空构建目录
        """
        success, artifacts = package_builder.verify_build()
        assert success is False
        assert len(artifacts) == 0


class TestPyPIUploader:
    """PyPIUploader 测试"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录"""
        temp = tempfile.mkdtemp()
        yield temp
        if os.path.exists(temp):
            shutil.rmtree(temp)

    @pytest.fixture
    def pypi_uploader(self, temp_dir):
        """创建 PyPIUploader 实例"""
        from src.core.pypi_uploader import PyPIUploader
        dist_path = os.path.join(temp_dir, "dist")
        os.makedirs(dist_path, exist_ok=True)
        return PyPIUploader(dist_dir=dist_path)

    def test_tc_007_upload_dry_run(self, pypi_uploader):
        """
        TC-007: dry-run 模式上传
        """
        success, msg = pypi_uploader.upload(dry_run=True)
        assert success is True
        assert "预览模式" in msg

    def test_tc_008_upload_empty_dist(self, pypi_uploader):
        """
        TC-008: 空目录上传失败
        """
        with pytest.raises(Exception):
            pypi_uploader.upload(dry_run=False)


class TestGitPusher:
    """GitPusher 测试"""

    @pytest.fixture
    def git_pusher(self):
        """创建 GitPusher 实例"""
        from src.core.git_pusher import GitPusher
        return GitPusher(project_dir=".")

    def test_tc_009_get_remote_url(self, git_pusher):
        """
        TC-009: 获取远程仓库URL
        """
        url = git_pusher.get_remote_url()
        assert url is not None
        assert "gitee.com" in url or "github.com" in url

    def test_tc_010_create_tag_dry_run(self, git_pusher):
        """
        TC-010: dry-run 模式创建标签
        """
        success, msg = git_pusher.create_tag("99.99.99", dry_run=True)
        assert success is True
        assert "预览模式" in msg


class TestDeployVerifier:
    """DeployVerifier 测试"""

    @pytest.fixture
    def verifier(self):
        """创建 DeployVerifier 实例"""
        from src.core.deploy_verifier import DeployVerifier
        return DeployVerifier()

    def test_tc_011_verify_pypi_not_exists(self, verifier):
        """
        TC-011: 验证不存在的包版本
        """
        success, result = verifier.verify_pypi("99.99.99")
        assert success is False


class TestStateUpdater:
    """StateUpdater 测试"""

    @pytest.fixture
    def temp_state_file(self):
        """创建临时状态文件"""
        temp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp.write("version: test\n")
        temp.close()
        yield temp.name
        if os.path.exists(temp.name):
            os.remove(temp.name)

    @pytest.fixture
    def state_updater(self, temp_state_file):
        """创建 StateUpdater 实例"""
        from src.core.state_updater import StateUpdater
        return StateUpdater(state_file=temp_state_file)

    def test_tc_012_update_deployment_status(self, state_updater):
        """
        TC-012: 更新部署状态
        """
        success = state_updater.update_deployment_status(
            version="99.99.99",
            pypi_url="https://pypi.org/test/99.99.99",
            git_tag="v99.99.99",
            agent_id="2"
        )
        assert success is True

    def test_tc_013_get_version_status(self, state_updater):
        """
        TC-013: 获取版本状态
        """
        state_updater.update_deployment_status(
            version="99.99.99",
            pypi_url="https://pypi.org/test/99.99.99",
            git_tag="v99.99.99",
            agent_id="2"
        )
        status = state_updater.get_version_status("99.99.99")
        assert status is not None
        assert status.get("version") == "99.99.99"


class TestDeploymentOrchestrator:
    """DeploymentOrchestrator 测试"""

    def test_tc_014_orchestrator_init(self):
        """
        TC-014: 编排器初始化
        """
        from src.core.deployment_orchestrator import DeploymentOrchestrator

        orchestrator = DeploymentOrchestrator(dry_run=True, verbose=True)
        assert orchestrator.dry_run is True
        assert orchestrator.verbose is True
        assert len(orchestrator.steps) == 0

    def test_tc_015_add_step(self):
        """
        TC-015: 添加步骤
        """
        from src.core.deployment_orchestrator import DeploymentOrchestrator

        orchestrator = DeploymentOrchestrator()

        def dummy_step():
            return "test"

        orchestrator.add_step("test_step", "测试步骤", dummy_step)
        assert len(orchestrator.steps) == 1
        assert orchestrator.steps[0].name == "test_step"

    def test_tc_016_dry_run_execute(self):
        """
        TC-016: dry-run 模式执行
        """
        from src.core.deployment_orchestrator import DeploymentOrchestrator

        orchestrator = DeploymentOrchestrator(dry_run=True)

        def dummy_step():
            return "test"

        orchestrator.add_step("test_step", "测试步骤", dummy_step)
        result = orchestrator.run(verify_only=False)
        assert len(orchestrator.results) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
