"""
EventListener - Webhook事件监听模块

监听GitHub/Gitee webhook事件：
- 解析GitHub/Gitee webhook payload
- 支持崩溃恢复（自动重启+指数退避）
- 事件过滤
"""

import json
import time
import threading
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
import os


class EventType(Enum):
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    UNKNOWN = "unknown"


@dataclass
class GitHubEvent:
    event_type: str
    repo: str
    branch: str
    author: str
    commits: list = field(default_factory=list)
    action: Optional[str] = None
    number: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GiteeEvent:
    event_type: str
    repo: str
    branch: str
    author: str
    action: Optional[str] = None
    number: Optional[int] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class WebhookEvent:
    source: str
    event_type: EventType
    payload: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class CrashRecoveryPolicy:
    """崩溃恢复策略"""

    MAX_RETRIES = 3
    BACKOFF_INTERVALS = [60, 300, 900]  # 1min, 5min, 15min

    def __init__(self):
        self.retry_count = 0
        self.last_retry_time: Optional[float] = None

    def should_retry(self) -> bool:
        return self.retry_count < self.MAX_RETRIES

    def get_backoff_interval(self) -> int:
        if self.retry_count < len(self.BACKOFF_INTERVALS):
            return self.BACKOFF_INTERVALS[self.retry_count]
        return self.BACKOFF_INTERVALS[-1]

    def record_retry(self):
        self.retry_count += 1
        self.last_retry_time = time.time()

    def reset(self):
        self.retry_count = 0
        self.last_retry_time = None


class EventListener:
    """Webhook事件监听器"""

    def __init__(self, config, crash_recovery: Optional[CrashRecoveryPolicy] = None):
        self.config = config
        self.crash_recovery = crash_recovery or CrashRecoveryPolicy()
        self.server: Optional[HTTPServer] = None
        self._running = False
        self._server_thread: Optional[threading.Thread] = None
        self.event_callbacks: list = []

    def register_callback(self, callback: Callable[[WebhookEvent], None]):
        self.event_callbacks.append(callback)

    def parse_github_payload(self, payload: Dict[str, Any]) -> Optional[GitHubEvent]:
        try:
            event_type = payload.get('action', 'push')
            repo = payload.get('repository', {}).get('full_name', '')
            ref = payload.get('ref', '')
            branch = ref.replace('refs/heads/', '') if ref else ''
            sender = payload.get('sender', {}).get('login', '')

            commits = []
            if 'commits' in payload:
                for commit in payload['commits']:
                    commits.append({
                        'id': commit.get('id', ''),
                        'message': commit.get('message', ''),
                        'timestamp': commit.get('timestamp', '')
                    })

            return GitHubEvent(
                event_type=event_type,
                repo=repo,
                branch=branch,
                author=sender,
                commits=commits,
                action=event_type,
                timestamp=datetime.now().isoformat()
            )
        except Exception:
            return None

    def parse_gitee_payload(self, payload: Dict[str, Any]) -> Optional[GiteeEvent]:
        try:
            event_type = payload.get('action', 'push')
            repo = payload.get('project', {}).get('path_with_namespace', '')
            ref = payload.get('ref', '')
            branch = ref.replace('refs/heads/', '') if ref else ''
            author = payload.get('user_name', '')

            return GiteeEvent(
                event_type=event_type,
                repo=repo,
                branch=branch,
                author=author,
                action=event_type,
                number=payload.get('pull_request', {}).get('iid'),
                timestamp=datetime.now().isoformat()
            )
        except Exception:
            return None

    def _get_event_type(self, headers: Dict[str, str]) -> str:
        github_event = headers.get('X-GitHub-Event', '')
        gitee_event = headers.get('X-Gitee-Event', '')

        if github_event:
            return 'github'
        elif gitee_event:
            return 'gitee'
        return 'unknown'

    def _create_handler(self):
        config = self.config
        crash_recovery = self.crash_recovery

        class WebhookHandler(BaseHTTPRequestHandler):
            def do_POST(self):
                try:
                    content_type, _ = cgi.parse_header(self.headers.get('Content-Type', ''))

                    content_length = int(self.headers.get('Content-Length', 0))
                    body = self.rfile.read(content_length)

                    payload_str = body.decode('utf-8')
                    payload = json.loads(payload_str)

                    event_source = 'unknown'
                    event = None

                    if 'X-GitHub-Event' in self.headers:
                        event_source = 'github'
                        event = listener.parse_github_payload(payload)
                    elif 'X-Gitee-Event' in self.headers:
                        event_source = 'gitee'
                        event = listener.parse_gitee_payload(payload)

                    if event:
                        webhook_event = WebhookEvent(
                            source=event_source,
                            event_type=EventType.PUSH if event.event_type == 'push' else EventType.PULL_REQUEST,
                            payload=payload
                        )

                        for callback in listener.event_callbacks:
                            try:
                                callback(webhook_event)
                            except Exception as e:
                                print(f"Callback error: {e}")

                        crash_recovery.reset()

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "ok"}')

                except Exception as e:
                    print(f"Webhook handler error: {e}")
                    crash_recovery.record_retry()
                    self.send_response(500)
                    self.end_headers()

            def log_message(self, format, *args):
                pass

        return WebhookHandler

    def start_listening(self, port: Optional[int] = None) -> bool:
        if port is None:
            port = self.config.get_webhook_port() or 8080

        if not self.crash_recovery.should_retry():
            print(f"超出最大重试次数 ({CrashRecoveryPolicy.MAX_RETRIES})")
            return False

        try:
            handler_class = self._create_handler()
            self.server = HTTPServer(('0.0.0.0', port), handler_class)
            self._running = True

            self._server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self._server_thread.start()

            print(f"Webhook监听已启动: 0.0.0.0:{port}")
            return True

        except Exception as e:
            print(f"启动监听失败: {e}")
            self.crash_recovery.record_retry()
            return False

    def _run_server(self):
        if self.server:
            try:
                self.server.serve_forever()
            except Exception as e:
                print(f"Server error: {e}")

    def stop(self):
        self._running = False
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.server = None

    def is_running(self) -> bool:
        return self._running

    def get_status(self) -> Dict[str, Any]:
        return {
            'running': self.is_running(),
            'port': self.config.get_webhook_port(),
            'retry_count': self.crash_recovery.retry_count,
            'max_retries': CrashRecoveryPolicy.MAX_RETRIES,
            'can_retry': self.crash_recovery.should_retry()
        }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Webhook事件监听")
    parser.add_argument('--port', '-p', type=int, default=8080, help='监听端口')
    parser.add_argument('--status', '-s', action='store_true', help='查看状态')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    from src.core.webhook_config import WebhookConfigManager
    manager = WebhookConfigManager()
    config = manager.load_config() if manager.config_file.exists() else manager.generate_config()

    listener = EventListener(config=config)

    if args.status:
        status = listener.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("=== EventListener状态 ===")
            print(f"运行中: {status['running']}")
            print(f"端口: {status['port']}")
            print(f"重试次数: {status['retry_count']}/{status['max_retries']}")
            print(f"可重试: {status['can_retry']}")
        return

    if listener.start_listening(port=args.port):
        print("按 Ctrl+C 停止监听")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            listener.stop()
            print("\n监听已停止")


if __name__ == "__main__":
    main()
