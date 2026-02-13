from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DispatchEvent:
    """分发事件"""
    event_type: str
    source: str
    payload: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    callbacks_results: List[dict] = field(default_factory=list)


@dataclass
class CallbackResult:
    """回调执行结果"""
    callback_name: str
    success: bool
    error: Optional[str] = None
    duration_ms: float = 0.0


class EventDispatcher:
    """事件分发器"""

    def __init__(self):
        self._callbacks: Dict[str, List[Callable]] = {}
        self._callback_names: Dict[Callable, str] = {}

    def register_callback(
        self,
        callback: Callable,
        event_types: Optional[List[str]] = None,
        name: Optional[str] = None
    ) -> str:
        """注册回调函数

        Args:
            callback: 回调函数
            event_types: 关注的事件类型列表，None表示所有类型
            name: 回调名称，默认使用函数名

        Returns:
            callback_id: 回调唯一标识
        """
        callback_id = name or callback.__name__

        if callback_id in self._callback_names.values():
            raise ValueError(f"回调 {callback_id} 已注册")

        event_list = event_types or ["*"]
        for event_type in event_list:
            if event_type not in self._callbacks:
                self._callbacks[event_type] = []
            self._callbacks[event_type].append(callback)

        self._callback_names[callback] = callback_id
        logger.info(f"已注册回调 {callback_id}，关注事件: {event_list}")
        return callback_id

    def unregister_callback(self, callback_id: str) -> bool:
        """取消注册回调"""
        removed = False
        for event_type in self._callbacks:
            for callback in self._callbacks[event_type]:
                if self._callback_names.get(callback) == callback_id:
                    self._callbacks[event_type].remove(callback)
                    del self._callback_names[callback]
                    removed = True
        return removed

    def dispatch(self, event: DispatchEvent) -> DispatchEvent:
        """分发事件到所有注册的回调

        Args:
            event: 解析后的GitHub/Gitee事件

        Returns:
            包含回调执行结果的事件
        """
        results = []
        callbacks = self._callbacks.get(event.event_type, []) + \
                   self._callbacks.get("*", [])

        for callback in callbacks:
            callback_id = self._callback_names.get(callback, callback.__name__)
            try:
                start = datetime.now()
                result = callback(event)
                duration = (datetime.now() - start).total_seconds() * 1000

                results.append({
                    "callback_name": callback_id,
                    "success": True,
                    "duration_ms": round(duration, 2)
                })
                logger.debug(f"回调 {callback_id} 执行成功 ({duration:.2f}ms)")

            except Exception as e:
                duration = (datetime.now() - start).total_seconds() * 1000
                results.append({
                    "callback_name": callback_id,
                    "success": False,
                    "error": str(e),
                    "duration_ms": round(duration, 2)
                })
                logger.error(f"回调 {callback_id} 执行失败: {e}")

        event.callbacks_results = results
        return event

    def get_registered_callbacks(self) -> Dict[str, List[str]]:
        """获取已注册的回调列表"""
        return {
            event_type: [self._callback_names.get(cb, cb.__name__) for cb in callbacks]
            for event_type, callbacks in self._callbacks.items()
        }

    def clear_callbacks(self):
        """清空所有回调"""
        self._callbacks.clear()
        self._callback_names.clear()
