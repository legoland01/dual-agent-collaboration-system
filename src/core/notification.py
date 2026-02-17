from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """实时通知服务"""
    
    def __init__(self, storage):
        self.storage = storage
        self.config_path = "config/notification.yaml"
        self.instruction_path = "config/instructions/TODO_NOTIFY.md"
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        Path("config").mkdir(parents=True, exist_ok=True)
        Path("config/instructions").mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        """加载配置"""
        import yaml
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def _save_config(self, config: dict):
        """保存配置"""
        import yaml
        self._ensure_config_dir()
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f)
    
    def generate_instruction(self, output_path: Optional[str] = None) -> bool:
        """
        生成Instruction文件
        Returns: success
        """
        if output_path is None:
            output_path = self.instruction_path
        
        self._ensure_config_dir()
        
        content = """# TODO通知处理规则

## 触发条件
当用户告知"我有新TODO"或"查看TODO"时，执行以下操作：

## 操作流程
1. 读取 state/todos.db 中的未读TODO
2. 查找当前用户的未处理TODO
3. 使用 question tool 询问用户操作

## Question Tool 调用示例
当检测到用户有未读TODO时，应调用question tool：

```json
{
  "name": "question",
  "arguments": {
    "questions": [{
      "header": "待办事项",
      "question": "您有 {count} 个待处理TODO: {todo_list}",
      "options": [
        {"label": "立即执行", "description": "开始处理第一个TODO"},
        {"label": "稍后处理", "description": "设置提醒，稍后处理"},
        {"label": "查看详情", "description": "查看所有TODO详情"},
        {"label": "忽略", "description": "暂时忽略"}
      ]
    }]
  }
}
```

## 可用操作
- **立即执行**: 标记TODO为进行中，开始处理
- **稍后处理**: 将TODO标记为延迟，设置提醒时间
- **查看详情**: 显示TODO完整列表和内容
- **忽略**: 关闭通知

## TODO状态说明
- pending: 待处理
- in_progress: 进行中
- completed: 已完成
- cancelled: 已取消
- deferred: 已延迟
"""
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Instruction文件已生成: {output_path}")
            return True
        except Exception as e:
            logger.error(f"生成Instruction文件失败: {e}")
            return False
    
    def notify(self, todo: dict) -> str:
        """
        触发通知
        Returns: notification_id
        """
        import sqlite3
        
        notification_id = f"notif-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notifications (id, todo_id, created_at)
            VALUES (?, ?, ?)
        """, (notification_id, todo.get('id'), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        logger.info(f"通知已触发: {notification_id} for {todo.get('id')}")
        return notification_id
    
    def enable(self) -> bool:
        """启用通知"""
        config = self._load_config()
        config['enabled'] = True
        self._save_config(config)
        
        # 生成Instruction文件
        self.generate_instruction()
        
        logger.info("通知已启用")
        return True
    
    def disable(self) -> bool:
        """禁用通知"""
        config = self._load_config()
        config['enabled'] = False
        self._save_config(config)
        
        logger.info("通知已禁用")
        return True
    
    def get_status(self) -> dict:
        """
        获取通知状态
        Returns: {enabled: bool, last_notification: str}
        """
        config = self._load_config()
        
        import sqlite3
        conn = sqlite3.connect(self.storage.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, created_at FROM notifications
            ORDER BY created_at DESC LIMIT 1
        """)
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "enabled": config.get('enabled', False),
            "last_notification": row[0] if row else None,
            "instruction_exists": Path(self.instruction_path).exists()
        }
