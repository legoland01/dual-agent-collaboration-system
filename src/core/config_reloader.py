"""配置热重载模块。

功能：
1. 监控配置文件变化
2. 自动重新加载配置
3. 配置验证和回滚
"""
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import yaml


logger = logging.getLogger(__name__)


class ConfigReloadError(Exception):
    """配置重载错误。"""
    pass


class ConfigValidationError(ConfigReloadError):
    """配置验证错误。"""
    pass


class ConfigReloader:
    """配置热重载器。"""
    
    def __init__(
        self,
        config_paths: Dict[str, str],
        reload_callback: Callable[[str, Dict], None] = None,
        validation_schema: Optional[Dict] = None
    ):
        """初始化。
        
        Args:
            config_paths: 配置路径映射 {name: path}
            reload_callback: 重载回调函数 (config_name, config_data)
            validation_schema: 配置验证 schema
        """
        self.config_paths = config_paths
        self.reload_callback = reload_callback
        self.validation_schema = validation_schema
        self.configs: Dict[str, Dict] = {}
        self.mtimes: Dict[str, float] = {}
        self._stop_event = threading.Event()
        self._monitor_thread: Optional[threading.Thread] = None
        self._last_check: float = 0
    
    def load_all(self) -> Dict[str, Dict]:
        """加载所有配置文件。"""
        for name, path in self.config_paths.items():
            self.configs[name] = self._load_config(path)
            self.mtimes[name] = Path(path).stat().st_mtime
        
        logger.info(f"已加载 {len(self.configs)} 个配置文件: {list(self.configs.keys())}")
        return self.configs
    
    def get(self, config_name: str) -> Optional[Dict]:
        """获取指定配置。"""
        return self.configs.get(config_name)
    
    def _load_config(self, path: str) -> Dict:
        """加载单个配置文件。"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"加载配置文件失败: {path}, {e}")
            raise ConfigReloadError(f"加载配置文件失败: {path}")
    
    def _validate_config(self, config: Dict, config_name: str) -> bool:
        """验证配置。"""
        if self.validation_schema and config_name in self.validation_schema:
            schema = self.validation_schema[config_name]
            required_fields = schema.get("required", [])
            for field in required_fields:
                if field not in config:
                    logger.error(f"配置验证失败: 缺少必要字段 {field}")
                    return False
        return True
    
    def start_monitoring(self, interval: int = 60):
        """开始监控配置变化。
        
        Args:
            interval: 检查间隔（秒），默认 60 秒
        """
        if self._monitor_thread is not None and self._monitor_thread.is_alive():
            logger.warning("监控已在运行")
            return
        
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
        logger.info(f"配置监控已启动，间隔 {interval} 秒")
    
    def stop_monitoring(self):
        """停止监控。"""
        self._stop_event.set()
        if self._monitor_thread is not None:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
        logger.info("配置监控已停止")
    
    def _monitor_loop(self, interval: int):
        """监控循环。"""
        while not self._stop_event.is_set():
            try:
                self._check_changes()
            except Exception as e:
                logger.error(f"配置检查失败: {e}")
            
            self._stop_event.wait(timeout=interval)
    
    def _check_changes(self):
        """检查配置变化。"""
        for name, path in self.config_paths.items():
            try:
                current_mtime = Path(path).stat().st_mtime
                
                if current_mtime > self.mtimes[name]:
                    logger.info(f"检测到配置变化: {name}")
                    
                    new_config = self._load_config(path)
                    
                    if self._validate_config(new_config, name):
                        old_config = self.configs[name]
                        self.configs[name] = new_config
                        self.mtimes[name] = current_mtime
                        
                        if self.reload_callback:
                            self.reload_callback(name, new_config)
                        
                        logger.info(f"配置已重新加载: {name}")
                    else:
                        logger.error(f"配置验证失败: {name}")
                        
            except Exception as e:
                logger.error(f"检查配置变化失败 {name}: {e}")
    
    def reload_config(self, config_name: str) -> bool:
        """手动重新加载指定配置。"""
        if config_name not in self.config_paths:
            logger.error(f"未知配置: {config_name}")
            return False
        
        try:
            path = self.config_paths[config_name]
            new_config = self._load_config(path)
            
            if self._validate_config(new_config, config_name):
                self.configs[config_name] = new_config
                self.mtimes[config_name] = Path(path).stat().st_mtime
                
                if self.reload_callback:
                    self.reload_callback(config_name, new_config)
                
                logger.info(f"配置已重新加载: {config_name}")
                return True
            else:
                logger.error(f"配置验证失败: {config_name}")
                return False
                
        except Exception as e:
            logger.error(f"重新加载配置失败: {config_name}, {e}")
            return False
    
    def add_config(self, name: str, path: str):
        """添加新配置。"""
        if name in self.config_paths:
            logger.warning(f"配置已存在，将被覆盖: {name}")
        
        self.config_paths[name] = path
        config = self._load_config(path)
        self.configs[name] = config
        self.mtimes[name] = Path(path).stat().st_mtime
        logger.info(f"已添加配置: {name}")
    
    def remove_config(self, name: str):
        """移除配置。"""
        if name in self.config_paths:
            del self.config_paths[name]
            self.configs.pop(name, None)
            self.mtimes.pop(name, None)
            logger.info(f"已移除配置: {name}")
    
    def get_status(self) -> Dict:
        """获取状态。"""
        return {
            "monitoring": self._monitor_thread is not None and self._monitor_thread.is_alive(),
            "configs": list(self.configs.keys()),
            "config_count": len(self.configs)
        }


class ConfigManager:
    """配置管理器（简化版，无需监控）。"""
    
    def __init__(self, config_path: str):
        """初始化。
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = self._load()
    
    def _load(self) -> Dict:
        """加载配置。"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值。"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值。"""
        self.config[key] = value
    
    def save(self):
        """保存配置。"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)
    
    def reload(self):
        """重新加载配置。"""
        self.config = self._load()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    reloader = ConfigReloader(
        config_paths={
            "project": "state/project_state.yaml",
            "settings": "config/settings.yaml"
        }
    )
    
    print("加载配置:")
    configs = reloader.load_all()
    print(f"  {list(configs.keys())}")
    
    print("\n状态:")
    print(f"  {reloader.get_status()}")
