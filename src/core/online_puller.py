from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class OnlinePullerService:
    """上线拉取TODO"""
    
    def __init__(self, storage, status_monitor):
        self.storage = storage
        self.status_monitor = status_monitor
    
    def pull_pending(self, agent_id: str) -> List[dict]:
        """
        拉取积压TODO
        Returns: 未处理TODO列表
        """
        # 获取该Agent的未处理TODO
        todos = self.storage.list(
            receiver=agent_id,
            status='pending'
        )
        
        # 过滤已过期的deferred TODO
        now = datetime.now()
        result = []
        
        for todo in todos:
            deferred_until = todo.get('deferred_until')
            if deferred_until:
                deferred_time = datetime.fromisoformat(deferred_until)
                if deferred_time > now:
                    # 还未到处理时间，跳过
                    continue
            
            result.append(todo)
        
        logger.info(f"Agent {agent_id} 拉取到 {len(result)} 个积压TODO")
        return result
    
    def notify_user(self, todos: List[dict]) -> bool:
        """
        通知用户有待办
        Returns: success
        """
        if not todos:
            return True
        
        # 动态生成instruction文件，注入当前TODO信息
        self._update_instruction_with_todos(todos)
        
        # 打印通知信息
        logger.info(f"🔔 您有 {len(todos)} 个待处理TODO:")
        for i, todo in enumerate(todos[:5], 1):
            content = todo.get('content') or ''
            logger.info(f"  {i}. [{todo.get('id')}] {content[:50]}")
        
        if len(todos) > 5:
            logger.info(f"  ... 还有 {len(todos) - 5} 个")
        
        return True
    
    def _update_instruction_with_todos(self, todos: List[dict]):
        """更新instruction文件，注入当前TODO列表"""
        from pathlib import Path
        
        instruction_dir = Path("config/instructions")
        instruction_dir.mkdir(parents=True, exist_ok=True)
        instruction_path = instruction_dir / "TODO_NOTIFY.md"
        
        opencode_instruction_dir = Path("opencode_src/instructions")
        opencode_instruction_path = opencode_instruction_dir / "TODO_NOTIFY.md"
        
        root_instruction_dir = Path("instructions")
        root_instruction_path = root_instruction_dir / "TODO_NOTIFY.md"
        
        # 构建TODO列表
        todo_list = []
        for todo in todos[:10]:
            todo_id = todo.get('id', 'N/A')
            content = todo.get('content', '')[:60]
            priority = todo.get('priority', 'medium')
            todo_list.append(f"- **{todo_id}**: {content} [{priority}]")
        
        todos_text = "\n".join(todo_list)
        
        content = f"""# TODO通知处理规则

## 当前待办 ({len(todos)}个)
{todos_text}

## 触发条件
当用户告知"查看TODO"或"我有新TODO"时，执行以下操作：

## 操作流程
1. 读取 state/todos.db 中的未读TODO
2. 查找当前用户的未处理TODO
3. 使用 question tool 询问用户操作

## Question Tool 调用示例
当检测到用户有未读TODO时，应调用question tool：

```json
{{
  "name": "question",
  "arguments": {{
    "questions": [{{
      "header": "待办事项",
      "question": "您有 {len(todos)} 个待处理TODO",
      "options": [
        {{"label": "立即执行", "description": "开始处理第一个TODO"}},
        {{"label": "稍后处理", "description": "设置提醒，稍后处理"}},
        {{"label": "查看详情", "description": "查看所有TODO详情"}},
        {{"label": "忽略", "description": "暂时忽略"}}
      ]
    }}]
  }}
}}
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
            with open(instruction_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Instruction文件已更新: {instruction_path}")
            
            if opencode_instruction_dir.exists():
                with open(opencode_instruction_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✅ OpenCode Instruction文件已更新: {opencode_instruction_path}")
            
            if root_instruction_dir.exists():
                with open(root_instruction_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✅ 项目根目录Instruction文件已更新: {root_instruction_path}")
        except Exception as e:
            logger.error(f"❌ 更新Instruction文件失败: {e}")
    
    def get_deferred_todos(self, agent_id: str) -> List[dict]:
        """获取已到期的延迟TODO"""
        todos = self.storage.list(
            receiver=agent_id,
            status='deferred'
        )
        
        now = datetime.now()
        result = []
        
        for todo in todos:
            deferred_until = todo.get('deferred_until')
            if deferred_until:
                deferred_time = datetime.fromisoformat(deferred_until)
                if deferred_time <= now:
                    result.append(todo)
            else:
                # 没有deferred_until，不是延迟TODO
                pass
        
        return result
    
    def check_and_notify(self, agent_id: str) -> bool:
        """检查并通知用户"""
        # 检测上线
        self.status_monitor.detect_online(agent_id)
        
        # 拉取积压TODO
        pending = self.pull_pending(agent_id)
        
        # 获取到期延迟TODO
        deferred = self.get_deferred_todos(agent_id)
        
        # 通知
        all_todos = pending + deferred
        if all_todos:
            return self.notify_user(all_todos)
        
        return True
