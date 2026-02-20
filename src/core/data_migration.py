import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import yaml
import logging

logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """迁移错误"""
    pass


class DataMigrationService:
    """YAML到SQLite迁移服务"""
    
    def __init__(self, storage):
        self.storage = storage
        self.backup_dir = Path("state/backup")
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """确保备份目录存在"""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _normalize_priority(self, priority: str) -> str:
        """标准化优先级格式"""
        mapping = {
            'P0': 'high',
            'P1': 'medium',
            'P2': 'low',
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }
        return mapping.get(priority, 'medium')
    
    def _infer_sender_receiver(self, todo: dict) -> Tuple[str, str]:
        """
        推断sender和receiver
        - 有agent_id: 使用agent_id作为sender
        - 无agent_id: 尝试从TODO编号推断
        """
        agent_id = todo.get('agent_id')
        
        if agent_id is not None:
            return str(agent_id), "unknown"
        
        # 尝试从TODO ID推断
        todo_id = todo.get('id', '')
        if '-' in todo_id:
            parts = todo_id.split('-')
            if len(parts) >= 2:
                # TODO-1-001 -> sender=1
                try:
                    sender = parts[1]
                    return sender, "unknown"
                except:
                    pass
        
        return "unknown", "unknown"
    
    def _transform_todo(self, todo: dict) -> dict:
        """转换TODO格式"""
        sender, receiver = self._infer_sender_receiver(todo)
        
        return {
            'id': todo.get('id'),
            'content': todo.get('content', ''),
            'status': todo.get('status', 'pending'),
            'priority': self._normalize_priority(todo.get('priority', 'medium')),
            'sender': sender,
            'receiver': receiver,
            'source': 'legacy',
            'created_at': todo.get('created_at') or datetime.now().isoformat(),
            'updated_at': todo.get('updated_at'),
            'is_read': 0,
            'metadata': {'original': todo}
        }
    
    def _parse_yaml(self, yaml_path: str) -> List[dict]:
        """解析YAML文件"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data or 'todos' not in data:
            raise MigrationError(f"无效的YAML格式: {yaml_path}")
        
        return data.get('todos', [])
    
    def backup(self, yaml_path: str) -> str:
        """备份原YAML文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"agent_adhoc_todos_{timestamp}.yaml"
        
        shutil.copy2(yaml_path, backup_path)
        logger.info(f"备份完成: {backup_path}")
        
        return str(backup_path)
    
    def migrate(self, yaml_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        执行迁移
        Args:
            yaml_path: YAML文件路径，用于旧项目迁移。新项目不需要。
        Returns: (success, message)
        """
        if yaml_path is None:
            return False, "请显式指定YAML路径: migrate(yaml_path='state/agent_adhoc_todos.yaml')"
        
        # 检查YAML文件是否存在
        if not os.path.exists(yaml_path):
            return False, f"YAML文件不存在: {yaml_path}"
        
        try:
            # 1. 备份
            backup_path = self.backup(yaml_path)
            
            # 2. 解析
            todos = self._parse_yaml(yaml_path)
            
            # 3. 转换并写入
            success_count = 0
            error_count = 0
            errors = []
            
            for todo in todos:
                transformed = self._transform_todo(todo)
                ok, msg = self.storage.add(transformed)
                if ok:
                    success_count += 1
                else:
                    error_count += 1
                    errors.append(f"{todo.get('id')}: {msg}")
            
            # 4. 验证
            db_count = len(self.storage.list())
            
            message = f"迁移完成: 成功{success_count}条, 失败{error_count}条, 数据库共{db_count}条"
            if errors:
                message += f"\n错误: {errors[:5]}"
            
            logger.info(message)
            return True, message
            
        except Exception as e:
            logger.error(f"迁移失败: {e}")
            return False, str(e)
    
    def preview(self, yaml_path: Optional[str] = None) -> Dict[str, Any]:
        """
        预览迁移结果，不执行
        Args:
            yaml_path: YAML文件路径，用于旧项目迁移。新项目不需要。
        Returns: 预览信息
        """
        if yaml_path is None:
            return {"error": "请显式指定YAML路径: preview(yaml_path='state/agent_adhoc_todos.yaml')"}
        
        if not os.path.exists(yaml_path):
            return {"error": f"文件不存在: {yaml_path}"}
        
        todos = self._parse_yaml(yaml_path)
        
        preview_todos = []
        for todo in todos:
            transformed = self._transform_todo(todo)
            preview_todos.append(transformed)
        
        return {
            "total": len(todos),
            "todos": preview_todos[:10],  # 只返回前10条
            "backup_will_be_created": True
        }
    
    def rollback(self, backup_path: str) -> bool:
        """
        回滚迁移
        Returns: success
        """
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_path):
                logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            # 删除SQLite数据库
            db_path = "state/todos.db"
            if os.path.exists(db_path):
                os.remove(db_path)
                logger.info(f"已删除数据库: {db_path}")
            
            logger.info(f"回滚完成，可使用备份文件: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"回滚失败: {e}")
            return False
    
    def list_backups(self) -> List[str]:
        """列出可用备份"""
        backups = list(self.backup_dir.glob("agent_adhoc_todos_*.yaml"))
        return [str(b) for b in sorted(backups, reverse=True)]
