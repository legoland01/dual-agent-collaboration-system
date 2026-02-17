"""
Git同步管理模块

管理Git自动同步功能，支持配置和手动触发。
"""

import os
import subprocess
import yaml
from typing import List, Optional


class GitSync:
    """Git同步管理"""
    
    DEFAULT_CONFIG = {
        "enabled": False,
        "remotes": ["origin"],
        "retry": {
            "max_attempts": 3,
            "delay_seconds": 1
        }
    }
    
    def __init__(self, config_file: str = "config/git_sync.yaml"):
        """
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """
        加载配置
        
        Returns:
            配置字典
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or self.DEFAULT_CONFIG.copy()
            except Exception:
                pass
        
        return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.safe_dump(self.config, f)
    
    def sync(self, message: str, files: Optional[List[str]] = None) -> bool:
        """
        执行同步
        
        Args:
            message: 提交信息
            files: 要同步的文件列表
        
        Returns:
            是否成功
        """
        if not self.config.get("enabled", False):
            return True
        
        if not files:
            files = ["state/"]
        
        try:
            # git add
            for f in files:
                if os.path.exists(f):
                    subprocess.run(["git", "add", f], check=True, capture_output=True)
            
            # 检查是否有需要提交的内容
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True
            )
            if not result.stdout.strip():
                return True  # 没有变更，不需要commit
            
            # git commit
            subprocess.run(["git", "commit", "-m", message], check=True, capture_output=True)
            
            # git push
            remotes = self.config.get("remotes", ["origin"])
            for remote in remotes:
                self._push_with_retry(remote)
            
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _push_with_retry(self, remote: str) -> bool:
        """
        带重试的push
        
        Args:
            remote: 远程仓库名
        
        Returns:
            是否成功
        """
        max_attempts = self.config.get("retry", {}).get("max_attempts", 3)
        
        for attempt in range(max_attempts):
            try:
                subprocess.run(
                    ["git", "push", remote],
                    check=True,
                    capture_output=True
                )
                return True
            except subprocess.CalledProcessError:
                if attempt < max_attempts - 1:
                    import time
                    delay = self.config.get("retry", {}).get("delay_seconds", 1)
                    time.sleep(delay * (attempt + 1))  # 指数退避
        
        return False
    
    def enable(self):
        """启用同步"""
        self.config["enabled"] = True
        self._save_config()
    
    def disable(self):
        """禁用同步"""
        self.config["enabled"] = False
        self._save_config()
    
    def is_enabled(self) -> bool:
        """检查是否启用"""
        return self.config.get("enabled", False)
    
    def get_remotes(self) -> List[str]:
        """获取远程仓库列表"""
        return self.config.get("remotes", ["origin"])
    
    def add_remote(self, remote: str):
        """添加远程仓库"""
        remotes = self.get_remotes()
        if remote not in remotes:
            remotes.append(remote)
            self.config["remotes"] = remotes
            self._save_config()
    
    def remove_remote(self, remote: str):
        """移除远程仓库"""
        remotes = self.get_remotes()
        if remote in remotes:
            remotes.remove(remote)
            self.config["remotes"] = remotes
            self._save_config()
