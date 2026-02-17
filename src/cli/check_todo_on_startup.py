"""每次执行命令时检查未读TODO"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..core.todo_queue_manager import TodoQueueManager
from ..core.context_manager import ContextManager


def check_and_notify_todos():
    """检查未读TODO并在有新TODO时显示通知"""
    try:
        # 获取当前Agent
        try:
            context = ContextManager().load_context()
            agent_id = context.agent
            if isinstance(agent_id, int):
                agent_id = f"agent{agent_id}"
        except Exception:
            return
        
        # 检查未读TODO
        queue_manager = TodoQueueManager()
        unread = queue_manager.get_unread(agent_id)
        
        if unread:
            # 显示通知
            print("\n" + "=" * 60)
            print(f"🔔 你有 {len(unread)} 个未读TODO")
            print("-" * 60)
            
            # 显示最新的3个
            for todo in unread[-3:]:
                priority_icon = "🔴" if todo.priority == "high" else "🟡" if todo.priority == "medium" else "🟢"
                content = todo.content[:50] + "..." if len(todo.content) > 50 else todo.content
                print(f"  {priority_icon} [{todo.id}] {content}")
                print(f"     来自: {todo.from_agent}")
            
            if len(unread) > 3:
                print(f"  ... 还有 {len(unread) - 3} 个")
            
            print("=" * 60 + "\n")
            
    except Exception as e:
        pass
