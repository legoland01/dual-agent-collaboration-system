"""
StateNotifier HTTP接收器

提供Webhook端点接收外部通知。
"""

from flask import Flask, request, jsonify
from typing import Optional
import hmac
import logging

logger = logging.getLogger(__name__)


class StateReceiver:
    """StateNotifier HTTP接收器"""

    def __init__(self, queue_manager: "StateQueueManager", hmac_secret: Optional[str] = None):
        """
        Args:
            queue_manager: 队列管理器
            hmac_secret: HMAC密钥
        """
        self.app = Flask(__name__)
        self.queue_manager = queue_manager
        self.hmac_secret = hmac_secret
        self._setup_routes()

    def _setup_routes(self):
        """设置路由"""

        @self.app.route("/webhook/state", methods=["POST"])
        def handle_state_webhook():
            """处理状态变更Webhook"""
            try:
                # 1. 验证HMAC签名
                if self.hmac_secret:
                    if not self._verify_signature():
                        return jsonify({"error": "Invalid signature"}), 401

                # 2. 解析请求体
                data = request.get_json()
                if not data:
                    return jsonify({"error": "Empty body"}), 400

                # 3. 验证必需字段
                required_fields = ["event_type", "source_agent", "target_agent"]
                for field in required_fields:
                    if field not in data:
                        return jsonify({"error": f"Missing field: {field}"}), 400

                # 4. 入队列
                notification = self.queue_manager.enqueue(data)

                logger.info(f"通知已入队列: {notification.id}")

                return jsonify({
                    "status": "accepted",
                    "notification_id": notification.id
                }), 202

            except Exception as e:
                logger.error(f"处理Webhook失败: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/webhook/state/health", methods=["GET"])
        def health_check():
            """健康检查"""
            return jsonify({
                "status": "healthy",
                "queue_stats": self.queue_manager.get_all_stats()
            }), 200

        @self.app.route("/webhook/state/queue", methods=["GET"])
        def get_queue():
            """获取队列状态"""
            agent_id = request.args.get("agent_id")
            if agent_id:
                stats = self.queue_manager.get_stats(agent_id)
                unread = self.queue_manager.get_unread(agent_id)
                return jsonify({
                    "stats": stats,
                    "notifications": [{"id": n.id, "event": n.event_type} for n in unread]
                }), 200
            else:
                return jsonify({"error": "agent_id required"}), 400

    def _verify_signature(self) -> bool:
        """验证HMAC签名"""
        signature = request.headers.get("X-HMAC-Signature")
        if not signature:
            return False

        expected = hmac.new(
            self.hmac_secret.encode(),
            request.data,
            "sha256"
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected}", signature)

    def run(self, host: str = "0.0.0.0", port: int = 8080):
        """启动接收器"""
        logger.info(f"StateReceiver启动: {host}:{port}")
        self.app.run(host=host, port=port)


class StateReceiverError(Exception):
    """StateReceiver异常"""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.status_code = status_code
