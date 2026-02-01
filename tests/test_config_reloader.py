"""ConfigReloader 单元测试。"""
import pytest
import tempfile
import time
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config_reloader import (
    ConfigReloader, ConfigReloadError, ConfigValidationError
)


class TestConfigReloadError:
    """配置重载错误测试。"""

    def test_config_reload_error(self):
        """测试配置重载错误。"""
        with pytest.raises(ConfigReloadError):
            raise ConfigReloadError("Reload failed")

    def test_config_validation_error(self):
        """测试配置验证错误。"""
        with pytest.raises(ConfigValidationError):
            raise ConfigValidationError("Validation failed")


class TestConfigReloader:
    """配置热重载器测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def config_file(self, temp_dir):
        """创建临时配置文件。"""
        config_path = Path(temp_dir) / "test_config.yaml"
        config_data = {
            "setting1": "value1",
            "setting2": 42,
            "nested": {
                "key": "value"
            }
        }
        config_path.write_text(yaml.dump(config_data))
        return str(config_path)

    @pytest.fixture
    def reloader(self, config_file):
        """创建配置重载器。"""
        return ConfigReloader(
            config_paths={"test": config_file}
        )

    def test_init(self, reloader):
        """测试初始化。"""
        assert "test" in reloader.config_paths
        assert reloader.reload_callback is None
        assert reloader.configs == {}

    def test_init_with_callback(self):
        """测试带回调的初始化。"""
        callback = MagicMock()
        reloader = ConfigReloader(
            config_paths={},
            reload_callback=callback
        )
        assert reloader.reload_callback == callback

    def test_init_with_validation_schema(self):
        """测试带验证schema的初始化。"""
        schema = {
            "test": {
                "required": ["setting1"],
                "types": {"setting2": int}
            }
        }
        reloader = ConfigReloader(
            config_paths={},
            validation_schema=schema
        )
        assert reloader.validation_schema == schema

    def test_load_all(self, reloader, config_file):
        """测试加载所有配置。"""
        configs = reloader.load_all()
        
        assert "test" in configs
        assert configs["test"]["setting1"] == "value1"
        assert configs["test"]["setting2"] == 42

    def test_get(self, reloader, config_file):
        """测试获取配置。"""
        reloader.load_all()
        config = reloader.get("test")
        
        assert config is not None
        assert config["setting1"] == "value1"

    def test_get_nonexistent(self, reloader):
        """测试获取不存在的配置。"""
        config = reloader.get("nonexistent")
        assert config is None

    def test_load_config_success(self, config_file):
        """测试加载配置成功。"""
        reloader = ConfigReloader(config_paths={})
        config = reloader._load_config(config_file)
        
        assert config["setting1"] == "value1"

    def test_load_config_file_not_found(self, temp_dir):
        """测试加载配置（文件不存在）。"""
        reloader = ConfigReloader(config_paths={})
        
        with pytest.raises(ConfigReloadError):
            reloader._load_config("/nonexistent/path/config.yaml")

    def test_load_config_invalid_yaml(self, temp_dir):
        """测试加载配置（无效YAML）。"""
        config_path = Path(temp_dir) / "invalid.yaml"
        config_path.write_text("invalid: yaml: content: [")
        
        reloader = ConfigReloader(config_paths={})
        
        with pytest.raises(ConfigReloadError):
            reloader._load_config(str(config_path))

    def test_validate_config_success(self, reloader, config_file):
        """测试验证配置成功。"""
        reloader.validation_schema = {
            "test": {
                "required": ["setting1"],
                "types": {"setting2": int}
            }
        }
        
        config = {"setting1": "value", "setting2": 42}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_validate_config_missing_required(self, reloader):
        """测试验证配置（缺少必需字段）。"""
        reloader.validation_schema = {
            "test": {
                "required": ["required_field"],
                "types": {}
            }
        }
        
        config = {"other_field": "value"}
        result = reloader._validate_config(config, "test")
        assert result is False

    def test_validate_config_type_mismatch(self, reloader):
        """测试验证配置（类型不匹配）。"""
        reloader.validation_schema = {
            "test": {
                "required": [],
                "types": {"number": int}
            }
        }
        
        config = {"number": "not a number"}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_reload_config(self, reloader, config_file):
        """测试重载配置。"""
        reloader.load_all()
        original_setting = reloader.get("test").get("setting1")
        
        result = reloader.reload_config("test")
        
        assert result is True
        assert reloader.get("test").get("setting1") == original_setting

    def test_reload_config_validation_failed(self, reloader, config_file):
        """测试重载配置（验证失败）。"""
        reloader.load_all()
        reloader.validation_schema = {
            "test": {
                "required": ["required_field"],
                "types": {}
            }
        }
        
        result = reloader.reload_config("test")
        
        assert result is False

    def test_stop(self, reloader):
        """测试停止监控。"""
        reloader._stop_event.set()
        assert reloader._stop_event.is_set()


class TestConfigReloaderModule:
    """配置热重载器模块测试。"""

    def test_module_importable(self):
        """测试模块可导入。"""
        from src.core import config_reloader
        assert hasattr(config_reloader, 'ConfigReloader')
        assert hasattr(config_reloader, 'ConfigReloadError')


class TestConfigReloaderEdgeCases:
    """配置热重载器边缘情况测试。"""

    def test_validate_config_no_schema(self):
        """测试无schema时的验证。"""
        reloader = ConfigReloader(config_paths={})
        config = {"test": "value"}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_validate_config_empty_schema(self):
        """测试空schema验证。"""
        reloader = ConfigReloader(config_paths={})
        reloader.validation_schema = {}
        
        config = {"any": "value"}
        result = reloader._validate_config(config, "unknown_config")
        assert result is True

    def test_reload_config_not_loaded(self):
        """测试重载未加载的配置。"""
        reloader = ConfigReloader(config_paths={})
        
        result = reloader.reload_config("nonexistent")
        assert result is False

    def test_validate_config_wrong_type(self):
        """测试验证配置（类型错误）。"""
        reloader = ConfigReloader(config_paths={})
        reloader.validation_schema = {
            "test": {
                "required": [],
                "types": {"count": int}
            }
        }
        
        config = {"count": "not_an_integer"}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_validate_config_all_fields_present(self):
        """测试验证配置（所有字段都存在）。"""
        reloader = ConfigReloader(config_paths={})
        reloader.validation_schema = {
            "test": {
                "required": ["field1", "field2"],
                "types": {}
            }
        }
        
        config = {"field1": "value1", "field2": "value2"}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_validate_config_multiple_missing_required(self):
        """测试验证配置（多个必需字段缺失）。"""
        reloader = ConfigReloader(config_paths={})
        reloader.validation_schema = {
            "test": {
                "required": ["field1", "field2", "field3"],
                "types": {}
            }
        }
        
        config = {"field1": "value"}
        result = reloader._validate_config(config, "test")
        assert result is False

    def test_validate_empty_config(self):
        """测试验证空配置。"""
        reloader = ConfigReloader(config_paths={})
        reloader.validation_schema = {
            "test": {
                "required": [],
                "types": {}
            }
        }
        
        config = {}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_validate_config_special_characters(self):
        """测试验证配置（特殊字符）。"""
        reloader = ConfigReloader(config_paths={})
        reloader.validation_schema = {
            "test": {
                "required": ["name"],
                "types": {}
            }
        }
        
        config = {"name": "Test_123-abc@example.com"}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_validate_config_with_types_dict(self):
        """测试验证配置（字典类型）。"""
        reloader = ConfigReloader(config_paths={})
        reloader.validation_schema = {
            "test": {
                "required": [],
                "types": {"data": dict}
            }
        }
        
        config = {"data": {"key": "value"}}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_validate_config_with_types_list(self):
        """测试验证配置（列表类型）。"""
        reloader = ConfigReloader(config_paths={})
        reloader.validation_schema = {
            "test": {
                "required": [],
                "types": {"items": list}
            }
        }
        
        config = {"items": [1, 2, 3]}
        result = reloader._validate_config(config, "test")
        assert result is True

    def test_start_stop_monitoring(self):
        """测试启动和停止监控。"""
        reloader = ConfigReloader(config_paths={})
        
        reloader.start_monitoring(interval=1)
        assert reloader._monitor_thread is not None
        assert reloader._monitor_thread.is_alive()
        
        reloader.stop_monitoring()
        assert reloader._monitor_thread is None

    def test_start_monitoring_already_running(self):
        """测试监控已在运行时启动。"""
        reloader = ConfigReloader(config_paths={})
        reloader.start_monitoring(interval=1)
        
        reloader.start_monitoring(interval=1)
        
        reloader.stop_monitoring()


class TestConfigReloaderAdditional:
    """配置热重载器附加测试。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_check_changes_detects_modification(self, temp_dir):
        """测试检查变化（检测到修改）。"""
        config_path = Path(temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump({"key": "value1"}))
        
        callback = MagicMock()
        reloader = ConfigReloader(
            config_paths={"test": str(config_path)},
            reload_callback=callback
        )
        reloader.load_all()
        
        original_mtime = reloader.mtimes["test"]
        time.sleep(0.1)
        
        config_path.write_text(yaml.dump({"key": "value2"}))
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_mtime = original_mtime + 1
            reloader._check_changes()
        
        assert reloader.configs["test"]["key"] == "value2"
        callback.assert_called_once()

    def test_check_changes_validation_failed(self, temp_dir):
        """测试检查变化（验证失败）。"""
        config_path = Path(temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump({"key": "value"}))
        
        callback = MagicMock()
        reloader = ConfigReloader(
            config_paths={"test": str(config_path)},
            reload_callback=callback,
            validation_schema={"test": {"required": ["required_field"]}}
        )
        reloader.load_all()
        
        with patch('pathlib.Path.stat') as mock_stat:
            mock_stat.return_value.st_mtime = reloader.mtimes["test"] + 1
            reloader._check_changes()
        
        callback.assert_not_called()

    def test_check_changes_exception_handling(self, temp_dir):
        """测试检查变化（异常处理）。"""
        reloader = ConfigReloader(config_paths={})
        
        with patch.object(reloader, 'config_paths', {"test": "/nonexistent.yaml"}):
            reloader._check_changes()

    def test_add_config(self, temp_dir):
        """测试添加配置。"""
        config_path = Path(temp_dir) / "new.yaml"
        config_path.write_text(yaml.dump({"new_key": "new_value"}))
        
        reloader = ConfigReloader(config_paths={})
        reloader.add_config("new", str(config_path))
        
        assert "new" in reloader.config_paths
        assert "new" in reloader.configs
        assert reloader.configs["new"]["new_key"] == "new_value"

    def test_add_config_overwrite(self, temp_dir):
        """测试覆盖添加配置。"""
        config_path1 = Path(temp_dir) / "config1.yaml"
        config_path1.write_text(yaml.dump({"key": "value1"}))
        
        config_path2 = Path(temp_dir) / "config2.yaml"
        config_path2.write_text(yaml.dump({"key": "value2"}))
        
        reloader = ConfigReloader(config_paths={"test": str(config_path1)})
        reloader.load_all()
        
        reloader.add_config("test", str(config_path2))
        
        assert reloader.configs["test"]["key"] == "value2"

    def test_remove_config(self, temp_dir):
        """测试移除配置。"""
        config_path = Path(temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump({"key": "value"}))
        
        reloader = ConfigReloader(config_paths={"test": str(config_path)})
        reloader.load_all()
        
        reloader.remove_config("test")
        
        assert "test" not in reloader.config_paths
        assert "test" not in reloader.configs
        assert "test" not in reloader.mtimes

    def test_remove_config_nonexistent(self, temp_dir):
        """测试移除不存在的配置。"""
        reloader = ConfigReloader(config_paths={})
        reloader.remove_config("nonexistent")

    def test_get_status_not_monitoring(self, temp_dir):
        """测试获取状态（未监控）。"""
        config_path = Path(temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump({"key": "value"}))
        
        reloader = ConfigReloader(config_paths={"test": str(config_path)})
        reloader.load_all()
        
        status = reloader.get_status()
        
        assert status["monitoring"] is False
        assert "test" in status["configs"]
        assert status["config_count"] == 1

    def test_get_status_with_monitoring(self, temp_dir):
        """测试获取状态（监控中）。"""
        config_path = Path(temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump({"key": "value"}))
        
        reloader = ConfigReloader(config_paths={"test": str(config_path)})
        reloader.load_all()
        reloader.start_monitoring(interval=60)
        
        try:
            status = reloader.get_status()
            
            assert status["monitoring"] is True
            assert "test" in status["configs"]
            assert status["config_count"] == 1
        finally:
            reloader.stop_monitoring()

    def test_reload_config_with_callback(self, temp_dir):
        """测试重载配置（带回调）。"""
        config_path = Path(temp_dir) / "test.yaml"
        config_path.write_text(yaml.dump({"key": "value1"}))
        
        callback = MagicMock()
        reloader = ConfigReloader(
            config_paths={"test": str(config_path)},
            reload_callback=callback
        )
        reloader.load_all()
        
        config_path.write_text(yaml.dump({"key": "value2"}))
        
        result = reloader.reload_config("test")
        
        assert result is True
        callback.assert_called_once_with("test", reloader.configs["test"])

    def test_reload_config_exception(self, temp_dir):
        """测试重载配置（异常）。"""
        reloader = ConfigReloader(config_paths={"test": "/nonexistent.yaml"})
        
        result = reloader.reload_config("test")
        assert result is False


class TestConfigManager:
    """配置管理器测试类。"""

    @pytest.fixture
    def temp_dir(self):
        """创建临时目录。"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def config_file(self, temp_dir):
        """创建临时配置文件。"""
        config_path = Path(temp_dir) / "settings.yaml"
        config_data = {
            "database": {"host": "localhost", "port": 5432},
            "debug": True
        }
        config_path.write_text(yaml.dump(config_data))
        return str(config_path)

    def test_init_existing_file(self, config_file):
        """测试初始化（文件存在）。"""
        from src.core.config_reloader import ConfigManager
        manager = ConfigManager(config_file)
        
        assert manager.config["database"]["host"] == "localhost"
        assert manager.config["debug"] is True

    def test_init_nonexistent_file(self, temp_dir):
        """测试初始化（文件不存在）。"""
        from src.core.config_reloader import ConfigManager
        manager = ConfigManager("/nonexistent/settings.yaml")
        
        assert manager.config == {}

    def test_get(self, config_file):
        """测试获取配置值。"""
        from src.core.config_reloader import ConfigManager
        manager = ConfigManager(config_file)
        
        assert manager.get("database.host") is None
        assert manager.get("database") == {"host": "localhost", "port": 5432}
        assert manager.get("debug") is True
        assert manager.get("debug", False) is True

    def test_get_with_default(self, config_file):
        """测试获取配置值（带默认值）。"""
        from src.core.config_reloader import ConfigManager
        manager = ConfigManager(config_file)
        
        assert manager.get("nonexistent", "default") == "default"
        assert manager.get("debug", False) is True

    def test_set(self, config_file):
        """测试设置配置值。"""
        from src.core.config_reloader import ConfigManager
        manager = ConfigManager(config_file)
        
        manager.set("new_key", "new_value")
        assert manager.config["new_key"] == "new_value"

    def test_save(self, temp_dir, config_file):
        """测试保存配置。"""
        from src.core.config_reloader import ConfigManager
        manager = ConfigManager(config_file)
        
        manager.set("new_key", "new_value")
        manager.save()
        
        new_manager = ConfigManager(config_file)
        assert new_manager.config["new_key"] == "new_value"

    def test_reload(self, temp_dir, config_file):
        """测试重新加载配置。"""
        from src.core.config_reloader import ConfigManager
        manager = ConfigManager(config_file)
        
        original_value = manager.config.get("debug")
        manager.set("debug", not original_value)
        
        manager.reload()
        
        assert manager.config["debug"] == original_value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
