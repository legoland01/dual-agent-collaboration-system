"""自动升级功能测试"""
import subprocess
import sys
from unittest.mock import patch, MagicMock
import pytest


class TestAutoUpgrade:
    """自动升级功能测试"""

    def test_get_installed_version(self):
        """测试获取当前安装版本"""
        from src.cli.auto_upgrade import get_installed_version

        result = get_installed_version()
        assert result is not None
        assert isinstance(result, str)

    @patch('urllib.request.urlopen')
    def test_get_latest_version_from_pypi(self, mock_urlopen):
        """测试从 PyPI 获取最新版本"""
        from src.cli.auto_upgrade import get_latest_version_from_pypi

        mock_response = MagicMock()
        mock_response.read.return_value = b'{"info": {"version": "2.2.12.2"}}'
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        result = get_latest_version_from_pypi()
        assert result == "2.2.12.2"

    @patch('urllib.request.urlopen')
    def test_get_latest_version_network_error(self, mock_urlopen):
        """测试网络错误时返回 None"""
        from src.cli.auto_upgrade import get_latest_version_from_pypi

        mock_urlopen.side_effect = Exception("Network error")

        result = get_latest_version_from_pypi()
        assert result is None

    def test_should_upgrade_already_latest(self):
        """测试当前已是最新版本，不需要升级"""
        from src.cli.auto_upgrade import should_upgrade

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="Version: 2.2.12.2")

            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = b'{"info": {"version": "2.2.12.2"}}'
                mock_response.__enter__ = MagicMock(return_value=mock_response)
                mock_response.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = mock_response

                needs, current, latest = should_upgrade()
                assert needs is False
                assert current == "2.2.12.2"
                assert latest == "2.2.12.2"

    def test_should_upgrade_need_upgrade(self):
        """测试当前版本低于 PyPI 版本，需要升级"""
        from src.cli.auto_upgrade import should_upgrade

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="Version: 2.2.12.1")

            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = b'{"info": {"version": "2.2.12.2"}}'
                mock_response.__enter__ = MagicMock(return_value=mock_response)
                mock_response.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = mock_response

                needs, current, latest = should_upgrade()
                assert needs is True
                assert current == "2.2.12.1"
                assert latest == "2.2.12.2"

    def test_should_upgrade_dev_version(self):
        """测试当前是开发版本，应该升级到正式版本"""
        from src.cli.auto_upgrade import should_upgrade

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="Version: 0.0.0.dev0")

            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = b'{"info": {"version": "2.2.12.2"}}'
                mock_response.__enter__ = MagicMock(return_value=mock_response)
                mock_response.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = mock_response

                needs, current, latest = should_upgrade()
                # 开发版应该升级到正式版本
                assert needs is True

    def test_check_and_upgrade_already_latest(self):
        """测试已是最新版本时，不执行升级"""
        from src.cli.auto_upgrade import check_and_upgrade

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="Version: 2.2.12.2")

            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = b'{"info": {"version": "2.2.12.2"}}'
                mock_response.__enter__ = MagicMock(return_value=mock_response)
                mock_response.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = mock_response

                # 已是最新版本，不触发升级
                check_and_upgrade()
                # 验证 pip install 没有被调用
                for call in mock_run.call_args_list:
                    if 'install' in str(call):
                        pytest.fail("pip install should not be called when already latest")

    @patch('subprocess.run')
    def test_check_and_upgrade_success(self, mock_run):
        """测试升级成功"""
        from src.cli.auto_upgrade import check_and_upgrade

        mock_subprocess = MagicMock()
        mock_subprocess.return_value = MagicMock(stdout="Version: 2.2.12.1")
        mock_subprocess2 = MagicMock()
        mock_subprocess2.return_value = MagicMock(returncode=0, stdout="")

        mock_run.side_effect = [
            mock_subprocess.return_value,
            mock_subprocess2.return_value,
        ]

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"info": {"version": "2.2.12.2"}}'
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            with pytest.raises(SystemExit) as exc_info:
                check_and_upgrade()

            assert exc_info.value.code == 0

    @patch('subprocess.run')
    def test_check_and_upgrade_failure(self, mock_run):
        """测试升级失败"""
        from src.cli.auto_upgrade import check_and_upgrade

        mock_subprocess = MagicMock()
        mock_subprocess.return_value = MagicMock(stdout="Version: 2.2.12.1")
        mock_subprocess2 = MagicMock()
        mock_subprocess2.return_value = MagicMock(returncode=1, stderr="Permission denied")

        mock_run.side_effect = [
            mock_subprocess.return_value,
            mock_subprocess2.return_value,
        ]

        with patch('urllib.request.urlopen') as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = b'{"info": {"version": "2.2.12.2"}}'
            mock_response.__enter__ = MagicMock(return_value=mock_response)
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response

            check_and_upgrade()

    def test_check_only(self):
        """测试仅检测版本"""
        from src.cli.auto_upgrade import check_only

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="Version: 2.2.12.1")

            with patch('urllib.request.urlopen') as mock_urlopen:
                mock_response = MagicMock()
                mock_response.read.return_value = b'{"info": {"version": "2.2.12.2"}}'
                mock_response.__enter__ = MagicMock(return_value=mock_response)
                mock_response.__exit__ = MagicMock(return_value=False)
                mock_urlopen.return_value = mock_response

                needs, current, latest = check_only()
                assert needs is True
                assert current == "2.2.12.1"
                assert latest == "2.2.12.2"
