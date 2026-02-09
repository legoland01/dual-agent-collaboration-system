"""文件Owner管理模块。"""
import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime


class FileOwnerError(Exception):
    """文件Owner异常基类。"""
    pass


class FileOwnerNotFoundError(FileOwnerError):
    """文件Owner未找到异常。"""
    pass


class PermissionDeniedError(FileOwnerError):
    """权限拒绝异常。"""
    pass


class FileOwnerManager:
    """文件Owner管理器。"""
    
    OWNER_FILE = ".file_owners.yaml"
    
    def __init__(self, project_path: str):
        """初始化文件Owner管理器。"""
        self.project_path = Path(project_path)
        self.owner_file = self.project_path / self.OWNER_FILE
    
    def _load_owners(self) -> dict:
        """加载Owner记录。"""
        import yaml
        if self.owner_file.exists():
            with open(self.owner_file) as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _save_owners(self, owners: dict):
        """保存Owner记录。"""
        import yaml
        with open(self.owner_file, 'w') as f:
            yaml.dump(owners, f, allow_unicode=True)
    
    def get_file_owner(self, file_path: str) -> Optional[str]:
        """
        获取文件的Owner。
        
        Args:
            file_path: 文件路径（相对路径）
            
        Returns:
            Agent ID of the file owner, or None if not tracked
        """
        owners = self._load_owners()
        return owners.get(file_path, {}).get("owner")
    
    def get_file_owner_info(self, file_path: str) -> dict:
        """
        获取文件的Owner详细信息。
        
        Args:
            file_path: 文件路径（相对路径）
            
        Returns:
            Owner info dict, or empty dict if not tracked
        """
        owners = self._load_owners()
        return owners.get(file_path, {})
    
    def record_file_creation(self, file_path: str, creator_agent: str) -> bool:
        """
        记录文件创建者。
        
        Args:
            file_path: 文件路径（相对路径）
            creator_agent: 创建者Agent ID
            
        Returns:
            是否记录成功
        """
        owners = self._load_owners()
        
        # 如果文件已有Owner，不覆盖
        if file_path in owners:
            return False
        
        owners[file_path] = {
            "owner": creator_agent,
            "created_at": datetime.now().isoformat(),
            "created_by": creator_agent
        }
        
        self._save_owners(owners)
        return True
    
    def transfer_owner(self, file_path: str, from_agent: str, to_agent: str) -> bool:
        """
        转移文件Owner（签署后调用）。
        
        Args:
            file_path: 文件路径
            from_agent: 原Owner
            to_agent: 新Owner
            
        Returns:
            是否转移成功
        """
        owners = self._load_owners()
        
        if file_path not in owners:
            return False
        
        current_owner = owners[file_path].get("owner")
        if current_owner != from_agent:
            return False
        
        owners[file_path]["owner"] = to_agent
        owners[file_path]["transferred_at"] = datetime.now().isoformat()
        owners[file_path]["transferred_from"] = from_agent
        
        self._save_owners(owners)
        return True
    
    def can_modify(self, file_path: str, agent_id: str) -> Tuple[bool, str]:
        """
        检查Agent是否可以修改文件。
        
        Args:
            file_path: 文件路径
            agent_id: Agent ID
            
        Returns:
            (是否允许修改, 拒绝原因)
        """
        owners = self._load_owners()
        
        # 如果文件不在Owner记录中，允许修改（兼容旧文件）
        if file_path not in owners:
            return True, ""
        
        owner = owners[file_path].get("owner")
        if owner == agent_id:
            return True, ""
        
        return False, f"文件Owner是 {owner}，{agent_id} 无权修改"
    
    def check_role_boundary(self, file_path: str, agent_id: str, action: str) -> Tuple[bool, str]:
        """
        检查角色边界。
        
        Args:
            file_path: 文件路径
            agent_id: Agent ID
            action: 操作类型 (edit, write, delete)
            
        Returns:
            (是否允许, 拒绝原因)
        """
        # 首先检查文件Owner权限
        can_modify, reason = self.can_modify(file_path, agent_id)
        if not can_modify:
            return False, reason
        
        return True, ""
    
    def get_owner_status(self) -> dict:
        """获取Owner统计信息。"""
        owners = self._load_owners()
        
        agent_files = {}
        for file_path, info in owners.items():
            agent = info.get("owner", "unknown")
            if agent not in agent_files:
                agent_files[agent] = []
            agent_files[agent].append(file_path)
        
        return {
            "total_files": len(owners),
            "agent_files": agent_files
        }
