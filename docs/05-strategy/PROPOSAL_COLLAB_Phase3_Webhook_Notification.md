# Proposal: Phase 3 - Webhook实时通知

**提案编号**: PROPOSAL-COLLAB-P3-001
**版本**: v1
**创建日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**状态**: DRAFT
**关联战略**: STRATEGY_Dual_Machine_Collaboration.md
**前置提案**: PROPOSAL_COLLAB_Phase1_Git_Stability.md
**重要说明**: Agent2电脑能被外网访问，无需内网穿透

---

## 1. 背景

### 1.1 当前问题

| 问题 | 表现 | 影响 |
|------|------|------|
| 无实时通知 | Agent2不知道有新评审请求 | 协作延迟 |
| 依赖轮询 | 需要手动检查状态 | 效率低 |
| 错过通知 | 邮件可能被忽略 | 协作中断 |

### 1.2 解决方案

**Webhook = 服务器主动推送通知到客户端**

### 1.3 当前条件

| 条件 | 状态 |
|------|------|
| Agent2电脑能被外网访问 | ✅ 是 |
| 需要内网穿透 | ❌ 不需要 |
| GitHub支持Webhook | ✅ 原生支持 |
| Gitee支持Webhook | ✅ 原生支持 |

---

## 2. 需求

### 2.1 功能需求

| 功能 | 实现方式 | 优先级 |
|------|----------|--------|
| Webhook接收服务 | 轻量HTTP服务接收GitHub/Gitee通知 | P0 |
| 事件处理 | 解析Webhook payload，识别事件类型 | P0 |
| 通知展示 | CLI显示通知，或发送邮件 | P1 |
| 事件过滤 | 只通知关键事件（push、PR、评审） | P1 |

### 2.2 Webhook事件

| 事件类型 | 来源 | 说明 |
|----------|------|------|
| push | GitHub/Gitee | 代码推送 |
| pull_request | GitHub | PR创建/更新 |
| merge_request | Gitee | MR创建/更新 |
| issue_comment | GitHub/Gitee | Issue评论 |

### 2.3 通知类型

| 通知类型 | 触发条件 | 通知内容 |
|----------|----------|----------|
| 代码推送 | push事件 | "Agent1推送了代码到X分支" |
| 评审请求 | PR/MR事件 | "有新MR待评审" |
| 签署提醒 | PR/MR合并前 | "请签署确认" |
| 状态变更 | 自定义事件 | "TODO状态已更新" |

---

## 3. 实现方案

### 3.1 整体架构

```
GitHub/Gitee
    │
    │ Webhook (HTTP POST)
    │
    ▼
┌─────────────────┐
│ Webhook接收服务   │  Agent2电脑 (http://agent2.example.com:8080)
│ - HTTP Server   │
│ - Payload解析   │
│ - 事件路由      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  通知处理器      │
│ - CLI通知       │
│ - 邮件发送      │
└─────────────────┘
```

### 3.2 Webhook接收服务

```python
# src/core/webhook_service.py

import http.server
import socketserver
import json
import threading
from typing import Callable, Dict, Any

class WebhookServer:
    """Webhook接收服务器"""

    PORT = 8080
    SECRET = "your-webhook-secret"  # GitHub/Gitee配置的secret

    def __init__(self, event_handler: Callable[[Dict[str, Any]], None):
        self.event_handler = event_handler
        self.server = None
        self.thread = None

    def start(self):
        """启动Webhook服务器"""
        handler = self._create_handler()

        with socketserver.TCPServer(("", self.PORT), handler) as httpd:
            print(f"🔔 Webhook服务器已启动: http://localhost:{self.PORT}")
            httpd.serve_forever()

    def start_background(self):
        """后台启动Webhook服务器"""
        self.thread = threading.Thread(target=self.start, daemon=True)
        self.thread.start()
        print(f"🔔 Webhook服务器已后台启动: http://localhost:{self.PORT}")

    def _create_handler(self):
        """创建HTTP请求处理器"""
        secret = self.SECRET

        class WebhookHandler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                """处理Webhook POST请求"""
                # 验证secret
                signature = self.headers.get("X-Hub-Signature-256", "")
                if not self._verify_signature(self.rfile.read(), signature, secret):
                    self.send_error(401, "Unauthorized")
                    return

                # 解析payload
                content_length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(content_length))

                # 识别事件类型
                event_type = self.headers.get("X-GitHub-Event",
                                              self.headers.get("X-Gitee-Event", "unknown"))

                # 处理事件
                result = self.event_handler({
                    "event": event_type,
                    "payload": payload,
                    "source": "github" if "X-GitHub-Event" in self.headers else "gitee"
                })

                if result["success"]:
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "ok"}))
                else:
                    self.send_error(400, result["error"])

            def _verify_signature(self, payload: bytes, signature: str, secret: str) -> bool:
                """验证Webhook签名"""
                import hmac
                expected = hmac.new(
                    secret.encode(),
                    payload,
                    "sha256"
                ).hexdigest()
                return hmac.compare_digest(f"sha256={expected}", signature)

        return WebhookHandler

    def stop(self):
        """停止Webhook服务器"""
        if self.server:
            self.server.shutdown()
```

### 3.3 事件处理器

```python
# src/core/webhook_handler.py

from enum import Enum
from typing import Dict, Any

class WebhookEventType(Enum):
    """Webhook事件类型"""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    MERGE_REQUEST = "merge_request"
    ISSUE_COMMENT = "issue_comment"
    REVIEW_REQUEST = "review_request"

class WebhookEventHandler:
    """Webhook事件处理器"""

    def __init__(self, notifier: "NotificationManager"):
        self.notifier = notifier

    def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """处理Webhook事件"""
        event_type = event["event"]
        payload = event["payload"]
        source = event["source"]

        handlers = {
            WebhookEventType.PUSH.value: self._handle_push,
            WebhookEventType.PULL_REQUEST.value: self._handle_pull_request,
            WebhookEventType.MERGE_REQUEST.value: self._handle_merge_request,
            WebhookEventType.REVIEW_REQUEST.value: self._handle_review_request,
        }

        handler = handlers.get(event_type)
        if not:
            return {"success": True, "message": f"忽略事件: {event_type}"}

        return handler(payload, source)

    def _handle_push(self, payload: Dict, source: str) -> Dict[str, Any]:
        """处理push事件"""
        branch = payload.get("ref", "").replace("refs/heads/", "")
        pusher = payload.get("pusher", {}).get("name", "未知")
        repository = payload.get("repository", {}).get("full_name", "未知")

        message = f"📦 {pusher} 推送了代码到 {repository}:{branch}"
        self.notifier.notify(message, priority="normal")

        return {"success": True, "message": "Push通知已发送"}

    def _handle_pull_request(self, payload: Dict, source: str) -> Dict[str, Any]:
        """处理PR事件"""
        action = payload.get("action", "")
        pr = payload.get("pull_request", {})
        title = pr.get("title", "未知PR")
        number = pr.get("number", 0)

        if action == "opened":
            message = f"🔀 新建PR #{number}: {title}"
            self.notifier.notify(message, priority="high")
        elif action == "review_requested":
            message = f"👀 PR #{number} 请求评审: {title}"
            self.notifier.notify(message, priority="high")

        return {"success": True, "message": "PR通知已发送"}

    def _handle_merge_request(self, payload: Dict, source: str) -> Dict[str, Any]:
        """处理MR事件"""
        action = payload.get("action", "")
        mr = payload.get("object_attributes", {})
        title = mr.get("title", "未知MR")
        number = mr.get("iid", 0)

        if action == "open":
            message = f"🔀 新建MR #{number}: {title}"
            self.notifier.notify(message, priority="high")

        return {"success": True, "message": "MR通知已发送"}

    def _handle_review_request(self, payload: Dict, source: str) -> Dict[str, Any]:
        """处理评审请求"""
        message = f"📋 有新的评审请求: {payload.get('title', '未知')}"
        self.notifier.notify(message, priority="high")

        return {"success": True, "message": "评审通知已发送"}
```

### 3.4 通知管理器

```python
# src/core/notification_manager.py

import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from typing import Optional

class NotificationManager:
    """通知管理器"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cli_enabled = True
        self.email_enabled = config.get("email", {}).get("enabled", False)
        self.webhook_enabled = config.get("webhook", {}).get("enabled", False)

    def notify(self, message: str, priority: str = "normal"):
        """发送通知"""
        # CLI通知
        if self.cli_enabled:
            self._notify_cli(message, priority)

        # 邮件通知
        if self.email_enabled:
            self._notify_email(message, priority)

    def _notify_cli(self, message: str, priority: str):
        """CLI通知"""
        import click
        from rich.console import Console

        console = Console()
        timestamp = datetime.now().strftime("%H:%M:%S")

        if priority == "high":
            console.print(f"[red]🔔 [{timestamp}] {message}[/red]")
        else:
            console.print(f"[green]🔔 [{timestamp}] {message}[/green]")

    def _notify_email(self, message: str, priority: str):
        """邮件通知"""
        if not self.email_enabled:
            return

        config = self.config["email"]
        msg = MIMEText(message, "plain", "utf-8")
        msg["Subject"] = f"[oc-collab] {message}"
        msg["From"] = config["from"]
        msg["To"] = config["to"]

        try:
            with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
                server.starttls()
                server.login(config["username"], config["password"])
                server.send_message(msg)
        except Exception as e:
            print(f"邮件发送失败: {e}")
```

### 3.5 GitHub/Gitee配置

#### GitHub Webhook配置

| 配置项 | 值 |
|--------|-----|
| Payload URL | `http://agent2.example.com:8080/webhook` |
| Content type | `application/json` |
| Secret | `your-webhook-secret` |
| 触发事件 | Push, Pull request, Issue comment |

#### Gitee Webhook配置

| 配置项 | 值 |
|--------|-----|
| 回调URL | `http://agent2.example.com:8080/webhook` |
| 密码 | `your-webhook-secret` |
| 触发事件 | Push code, Pull request, Review |

---

## 4. 验收标准

### 4.1 功能验收

| 序号 | 验收项 | 验收标准 |
|------|--------|----------|
| W-01 | HTTP服务启动 | `python -m webhook_server` 成功启动 |
| W-02 | GitHub推送通知 | GitHub推送后5秒内收到CLI通知 |
| W-03 | Gitee MR通知 | Gitee MR创建后5秒内收到通知 |
| W-04 | 邮件发送 | 启用时能收到邮件通知 |
| W-05 | 签名验证 | 拒绝未签名的Webhook请求 |

### 4.2 性能验收

| 序号 | 验收项 | 验收标准 |
|------|--------|----------|
| P-01 | 通知延迟 | GitHub事件→通知<5秒 |
| P-02 | 服务稳定性 | 连续运行72小时无崩溃 |

### 4.3 安全验收

| 序号 | 验收项 | 验收标准 |
|------|--------|----------|
| S-01 | 签名验证 | 伪造请求被拒绝 |
| S-02 | 端口安全 | 只监听localhost:8080 |

---

## 5. 工时预估

| 任务 | 工时 | 说明 |
|------|------|------|
| Webhook接收服务 | 4h | HTTP服务器、签名验证 |
| 事件处理器 | 3h | 解析GitHub/Gitee payload |
| 通知管理器 | 3h | CLI通知 + 邮件 |
| CLI命令 | 2h | `oc-collab webhook start/stop` |
| 配置文档 | 1h | GitHub/Gitee配置指引 |
| 单元测试 | 3h | 覆盖所有事件类型 |
| E2E测试 | 2h | 实际GitHub事件测试 |
| **合计** | **18h** | 3天 |

---

## 6. 依赖关系

| 依赖 | 说明 |
|------|------|
| `src/core/webhook_service.py` | 新建 |
| `src/core/webhook_handler.py` | 新建 |
| `src/core/notification_manager.py` | 新建 |
| `config/notification.yaml` | 新建 |

---

## 7. 风险与应对

| 风险 | 可能性 | 影响 | 应对 |
|------|--------|------|------|
| GitHub webhook超时 | 低 | 低 | 5秒超时，快速响应 |
| Agent2电脑IP变化 | 中 | 高 | 使用DDNS或固定IP |
| 防火墙阻止 | 低 | 高 | 开放8080端口 |
| 邮件发送失败 | 低 | 低 | CLI通知作为备选 |

---

## 8. 实施计划

| 日期 | 任务 | 交付物 |
|------|------|--------|
| Day 1 | Webhook服务器 | `src/core/webhook_service.py` |
| Day 1 | 事件处理器 | `src/core/webhook_handler.py` |
| Day 2 | 通知管理器 | `src/core/notification_manager.py` |
| Day 2 | CLI命令 | `src/cli/webhook.py` |
| Day 3 | 单元测试 | `tests/test_webhook.py` |
| Day 3 | 配置文档 | GitHub/Gitee配置指南 |
| Day 4 | E2E测试 | 实际GitHub事件测试 |

---

## 9. 后续配置（Agent2需手动执行）

### 9.1 GitHub配置

```bash
# 1. 进入项目仓库设置 → Webhooks → Add webhook

# 2. 配置Webhook
Payload URL: http://agent2.example.com:8080/webhook
Content type: application/json
Secret: your-webhook-secret

# 3. 选择触发事件
- Push
- Pull request
- Issue comment
```

### 9.2 启动服务

```bash
# 在Agent2电脑上执行
oc-collab webhook start --port 8080 --secret your-webhook-secret

# 查看状态
oc-collab webhook status

# 停止服务
oc-collab webhook stop
```

---

## 10. 签署确认

### Agent 1 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-08 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT
