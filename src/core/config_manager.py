from pathlib import Path
from typing import Dict, Optional
import yaml
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理"""
    
    def __init__(self, config_path: str = "config/notification.yaml"):
        self.config_path = config_path
        self._ensure_config()
    
    def _ensure_config(self):
        """确保配置文件存在"""
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        
        if not Path(self.config_path).exists():
            # 创建默认配置
            default_config = {
                'version': '1.0',
                'enabled': False,
                'opencode': {
                    'url': 'http://localhost:11411',
                    'api_key': ''
                },
                'listener': {
                    'interval': 5,
                    'auto_start': False
                },
                'rules': {
                    'notify_on_new': True,
                    'notify_on_update': False,
                    'notify_deferred_reminder': True
                }
            }
            self._save_config(default_config)
    
    def _load_config(self) -> dict:
        """加载配置"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _save_config(self, config: dict):
        """保存配置"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)
    
    def set(self, key: str, value: str) -> bool:
        """设置配置"""
        config = self._load_config()
        
        # 支持点号分隔的路径
        keys = key.split('.')
        
        # 逐层创建
        current = config
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            elif not isinstance(current[k], dict):
                # 如果键存在但不是字典，创建新的字典
                current[k] = {}
            current = current[k]
        
        # 设置值
        current[keys[-1]] = value
        
        self._save_config(config)
        logger.info(f"配置已设置: {key} = {value}")
        return True
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置"""
        config = self._load_config()
        
        keys = key.split('.')
        
        try:
            current = config
            for k in keys:
                current = current[k]
            return str(current) if current is not None else default
        except (KeyError, TypeError):
            return default
    
    def get_raw(self, key: str, default=None):
        """获取原始配置值"""
        config = self._load_config()
        
        keys = key.split('.')
        
        try:
            current = config
            for k in keys:
                current = current[k]
            return current if current is not None else default
        except (KeyError, TypeError):
            return default
    
    def list(self) -> dict:
        """列出所有配置"""
        return self._load_config()
    
    def delete(self, key: str) -> bool:
        """删除配置"""
        config = self._load_config()
        
        keys = key.split('.')
        
        try:
            current = config
            for k in keys[:-1]:
                current = current[k]
            
            if keys[-1] in current:
                del current[keys[-1]]
                self._save_config(config)
                logger.info(f"配置已删除: {key}")
                return True
        except (KeyError, TypeError):
            pass
        
        return False
    
    def reset(self) -> bool:
        """重置为默认配置"""
        default_config = {
            'version': '1.0',
            'enabled': False,
            'opencode': {
                'url': 'http://localhost:11411',
                'api_key': ''
            },
            'listener': {
                'interval': 5,
                'auto_start': False
            },
            'rules': {
                'notify_on_new': True,
                'notify_on_update': False,
                'notify_deferred_reminder': True
            }
        }
        self._save_config(default_config)
        logger.info("配置已重置")
        return True
