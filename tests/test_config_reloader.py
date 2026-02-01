"""ConfigReloader 单元测试。

测试用例：
- 配置加载
- 配置监控
- 配置重载
"""
import pytest
import tempfile
import os
from pathlib import Path


class TestConfigReloader:
    """ConfigReloader 测试。"""

    def test_initialization(self):
        """测试初始化。"""
        from src.core.config_reloader import ConfigReloader
        
        reloader = ConfigReloader(config_paths={"test": "config.yaml"})
        assert reloader is not None
        assert reloader.config_paths == {"test": "config.yaml"}
        assert reloader.configs == {}
        assert reloader.mtimes == {}

    def test_load_single_config(self, tmp_path):
        """测试加载单个配置。"""
        from src.core.config_reloader import ConfigReloader
        
        config_file = tmp_path / "app.yaml"
        config_file.write_text("name: test_app\nversion: 1.0.0")
        
        reloader = ConfigReloader(config_paths={"app": str(config_file)})
        configs = reloader.load_all()
        
        assert "app" in configs
        assert configs["app"]["name"] == "test_app"
        assert configs["app"]["version"] == "1.0.0"

    def test_load_multiple_configs(self, tmp_path):
        """测试加载多个配置。"""
        from src.core.config_reloader import ConfigReloader
        
        config1 = tmp_path / "app.yaml"
        config1.write_text("name: app1")
        
        config2 = tmp_path / "db.yaml"
        config2.write_text("host: localhost\nport: 5432")
        
        reloader = ConfigReloader(config_paths={
            "app": str(config1),
            "db": str(config2)
        })
        configs = reloader.load_all()
        
        assert len(configs) == 2
        assert configs["app"]["name"] == "app1"
        assert configs["db"]["host"] == "localhost"

    def test_get_config(self, tmp_path):
        """测试获取配置。"""
        from src.core.config_reloader import ConfigReloader
        
        config_file = tmp_path / "test.yaml"
        config_file.write_text("key: value\ndebug: true")
        
        reloader = ConfigReloader(config_paths={"test": str(config_file)})
        reloader.load_all()
        
        config = reloader.get("test")
        assert config["key"] == "value"
        assert config["debug"] is True

    def test_get_nonexistent_config(self, tmp_path):
        """测试获取不存在的配置。"""
        from src.core.config_reloader import ConfigReloader
        
        reloader = ConfigReloader(config_paths={})
        reloader.load_all()
        
        config = reloader.get("nonexistent")
        assert config is None

    def test_add_config(self, tmp_path):
        """测试添加配置。"""
        from src.core.config_reloader import ConfigReloader
        
        reloader = ConfigReloader(config_paths={})
        
        config_file = tmp_path / "new.yaml"
        config_file.write_text("id: 123")
        reloader.add_config("new", str(config_file))
        
        assert "new" in reloader.configs
        assert reloader.get("new")["id"] == 123

    def test_remove_config(self, tmp_path):
        """测试移除配置。"""
        from src.core.config_reloader import ConfigReloader
        
        config_file = tmp_path / "test.yaml"
        config_file.write_text("test: value")
        
        reloader = ConfigReloader(config_paths={"test": str(config_file)})
        reloader.load_all()
        
        reloader.remove_config("test")
        assert reloader.get("test") is None

    def test_get_status(self, tmp_path):
        """测试获取状态。"""
        from src.core.config_reloader import ConfigReloader
        
        config_file = tmp_path / "test.yaml"
        config_file.write_text("test: value")
        
        reloader = ConfigReloader(config_paths={"test": str(config_file)})
        reloader.load_all()
        
        status = reloader.get_status()
        assert status["monitoring"] is False
        assert status["config_count"] == 1

    def test_reload_config(self, tmp_path):
        """测试重新加载配置。"""
        from src.core.config_reloader import ConfigReloader
        
        config_file = tmp_path / "test.yaml"
        config_file.write_text("version: 1.0.0")
        
        reloader = ConfigReloader(config_paths={"test": str(config_file)})
        reloader.load_all()
        
        config_file.write_text("version: 2.0.0")
        result = reloader.reload_config("test")
        
        assert result is True
        assert reloader.get("test")["version"] == "2.0.0"

    def test_reload_nonexistent_config(self):
        """测试重新加载不存在的配置。"""
        from src.core.config_reloader import ConfigReloader
        
        reloader = ConfigReloader(config_paths={})
        
        result = reloader.reload_config("nonexistent")
        assert result is False


class TestConfigManager:
    """ConfigManager 测试。"""

    def test_initialization(self, tmp_path):
        """测试初始化。"""
        from src.core.config_reloader import ConfigManager
        
        config_file = tmp_path / "settings.yaml"
        config_file.write_text("debug: true")
        
        manager = ConfigManager(str(config_file))
        assert manager is not None

    def test_get_value(self, tmp_path):
        """测试获取值。"""
        from src.core.config_reloader import ConfigManager
        
        config_file = tmp_path / "settings.yaml"
        config_file.write_text("name: test\ncount: 42")
        
        manager = ConfigManager(str(config_file))
        assert manager.get("name") == "test"
        assert manager.get("count") == 42

    def test_get_default(self, tmp_path):
        """测试获取默认值。"""
        from src.core.config_reloader import ConfigManager
        
        config_file = tmp_path / "settings.yaml"
        config_file.write_text("key: value")
        
        manager = ConfigManager(str(config_file))
        assert manager.get("nonexistent", "default") == "default"

    def test_set_value(self, tmp_path):
        """测试设置值。"""
        from src.core.config_reloader import ConfigManager
        
        config_file = tmp_path / "settings.yaml"
        config_file.write_text("")
        
        manager = ConfigManager(str(config_file))
        manager.set("new_key", "new_value")
        
        assert manager.get("new_key") == "new_value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
