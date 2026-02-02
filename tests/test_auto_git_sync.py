"""AutoGitSync 单元测试。"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.auto_git_sync import AutoGitSyncEngine


class TestAutoGitSyncEngine:
    """自动Git同步引擎测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sync_engine(self, temp_dir):
        """创建同步引擎实例。"""
        return AutoGitSyncEngine(temp_dir)

    def test_init(self, sync_engine, temp_dir):
        """测试初始化。"""
        assert sync_engine.project_path == Path(temp_dir)

    def test_detect_changes_with_changes(self, sync_engine):
        """测试检测有变更的文件。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = " M modified.txt\n?? newfile.txt\n"
        
        with patch('subprocess.run', return_value=mock_result):
            changes = sync_engine.detect_changes()
            
            assert len(changes) == 2
            assert "newfile.txt" in changes

    def test_detect_changes_no_changes(self, sync_engine):
        """测试检测无变更。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        
        with patch('subprocess.run', return_value=mock_result):
            changes = sync_engine.detect_changes()
            
            assert changes == []

    def test_auto_add_no_changes(self, sync_engine):
        """测试无变更时自动添加。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        
        with patch('subprocess.run', return_value=mock_result):
            result = sync_engine.auto_add()
            
            assert result["added"] == []
            assert result["message"] == "无变更"

    def test_auto_add_with_changes(self, sync_engine):
        """测试有变更时自动添加。"""
        def mock_run_side_effect(cmd, **kwargs):
            if cmd[-1] == '--porcelain':
                mock_result = MagicMock()
                mock_result.returncode = 0
                mock_result.stdout = " M file1.txt\n M file2.txt\n"
                return mock_result
            return MagicMock()
        
        with patch('subprocess.run', side_effect=mock_run_side_effect):
            result = sync_engine.auto_add()
            
            assert len(result["added"]) == 2
            assert "已添加 2 个文件" in result["message"]

    def test_auto_commit_success(self, sync_engine):
        """测试自动提交成功。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "[main abc1234] 自动提交\n"
        
        with patch('subprocess.run', return_value=mock_result):
            result = sync_engine.auto_commit("Test commit")
            
            assert result["success"] is True

    def test_auto_commit_failure(self, sync_engine):
        """测试自动提交失败。"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "nothing to commit"
        
        with patch('subprocess.run', return_value=mock_result):
            result = sync_engine.auto_commit()
            
            assert result["success"] is False

    def test_auto_push_success(self, sync_engine):
        """测试自动推送成功。"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "To github.com:repo.git\n   abc1234..def5678  main -> main\n"
        
        with patch('subprocess.run', return_value=mock_result):
            result = sync_engine.auto_push()
            
            assert result["success"] is True

    def test_auto_push_failure(self, sync_engine):
        """测试自动推送失败。"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = "error: failed to push some refs"
        
        with patch('subprocess.run', return_value=mock_result):
            result = sync_engine.auto_push()
            
            assert result["success"] is False

    def test_sync_all(self, sync_engine):
        """测试完整同步流程。"""
        def mock_run_side_effect(cmd, **kwargs):
            mock_result = MagicMock()
            mock_result.returncode = 0
            if cmd[-1] == '--porcelain':
                mock_result.stdout = " M file.txt\n"
            elif cmd[0] == 'commit':
                mock_result.stdout = "[main abc1234] 自动同步变更\n"
            elif cmd[0] == 'push':
                mock_result.stdout = ""
            else:
                mock_result.stdout = ""
            return mock_result
        
        with patch('subprocess.run', side_effect=mock_run_side_effect):
            result = sync_engine.sync_all()
            
            assert "add" in result
            assert "commit" in result
            assert "push" in result


class TestAutoGitSyncModule:
    """自动Git同步模块测试。"""

    def test_module_importable(self):
        """测试模块可导入。"""
        from src.core import auto_git_sync
        assert hasattr(auto_git_sync, 'AutoGitSyncEngine')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
