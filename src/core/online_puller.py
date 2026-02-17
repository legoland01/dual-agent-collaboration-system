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
        
        # 打印通知信息
        logger.info(f"您有 {len(todos)} 个待处理TODO:")
        for i, todo in enumerate(todos[:5], 1):
            content = todo.get('content') or ''
            logger.info(f"  {i}. [{todo.get('id')}] {content[:50]}")
        
        if len(todos) > 5:
            logger.info(f"  ... 还有 {len(todos) - 5} 个")
        
        return True
    
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
