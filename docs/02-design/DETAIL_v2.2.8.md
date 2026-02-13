# 详细设计说明书：oc-collab v2.2.8

**版本**: v1
**创建日期**: 2026-02-13
**作者**: Agent 2 (开发负责人)
**关联概要设计**: docs/02-design/OUTLINE_v2.2.8.md
**版本号**: v2.2.8
**状态**: READY → 待 Agent1 评审

---

## 1. 功能模块映射

### 1.1 映射表

| 功能模块 (概要设计) | 技术模块 (详细设计) | 对应文件 |
|---------------------|---------------------|----------|
| EventDispatcher (F-WEB-003) | EventDispatcher | src/core/event_dispatcher.py |
| StateNotifier (F-WEB-004) | StateNotifier | src/core/state_notifier.py |
| HMACValidator (F-WEB-005) | HMACValidator | src/core/hmac_validator.py |
| RulesInitializer (F-INIT-001) | RulesInitializer | src/core/rules_initializer.py |

### 1.2 新增/变更文件

| 文件路径 | 功能 | 工时 |
|----------|------|------|
| src/core/event_dispatcher.py | 事件分发器 | 5h |
| src/core/state_notifier.py | 状态通知器 | 5h |
| src/core/hmac_validator.py | HMAC签名验证 | 3h |
| src/core/rules_initializer.py | 规则初始化器 | 3h |
| src/cli/rules_commands.py | rules init 命令 | 1h |
| src/cli/webhook_commands.py | webhook notify 命令增强 | 1h |

---

## 2. 技术架构

### 2.1 模块架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        oc-collab v2.2.8 详细架构                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   EventListener (v2.2.7)                                        │
│           │                                                      │
│           │ 解析后的事件                                          │
│           ▼                                                      │
│   ┌─────────────────────┐                                         │
│   │   EventDispatcher   │ ← 事件分发                              │
│   │   (F-WEB-003)      │                                         │
│   └──────────┬──────────┘                                         │
│              │                                                    │
│              │ 分发到回调                                          │
│              ▼                                                    │
│   ┌──────────┴──────────┐                                       │
│   │                      │                                       │
│   ▼                      ▼                                       │
│ StateNotifier         自定义回调                                  │
│ (F-WEB-004)                                                        │
│       │                                                            │
│       │ HTTP POST (HMAC签名)                                      │
│       ▼                                                            │
│ WebhookConfig ──→ HMACValidator ──→ 验证结果                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 模块 | 技术/库 | 版本 | 选型依据 |
|------|---------|------|----------|
| CLI框架 | Click | >=8.0 | 现有技术栈 |
| HTTP请求 | requests | any | 现有依赖 |
| 配置解析 | PyYAML | >=6.0 | 现有依赖 |
| HMAC签名 | hmac + hashlib | 内置 | Python内置，无需额外依赖 |

---

## 3. 核心模块设计

### 3.1 EventDispatcher (事件分发器)

#### 3.1.1 类设计

```python
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DispatchEvent:
    """分发事件"""
    event_type: str
    source: str  # "github" or "gitee"
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
        self._callbacks: Dict[str, List[Callable]] = {}  # event_type -> [callbacks]
        self._filters: Dict[str, Callable] = {}  # callback_name -> filter_func

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

        if callback_id in [cb.__name__ for cb in self._callbacks.get("*", [])]:
            raise ValueError(f"回调 {callback_id} 已注册")

        event_list = event_types or ["*"]
        for event_type in event_list:
            if event_type not in self._callbacks:
                self._callbacks[event_type] = []
            self._callbacks[event_type].append(callback)

        logger.info(f"已注册回调 {callback_id}，关注事件: {event_list}")
        return callback_id

    def unregister_callback(self, callback_id: str) -> bool:
        """取消注册回调"""
        removed = False
        for event_type in self._callbacks:
            self._callbacks[event_type] = [
                cb for cb in self._callbacks[event_type]
                if cb.__name__ != callback_id
            ]
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

        # 获取注册的回调
        callbacks = self._callbacks.get(event.event_type, []) + \
                   self._callbacks.get("*", [])

        for callback in callbacks:
            try:
                start = datetime.now()
                result = callback(event)
                duration = (datetime.now() - start).total_seconds() * 1000

                results.append(CallbackResult(
                    callback_name=callback.__name__,
                    success=True,
                    duration_ms=duration
                ))

                logger.debug(f"回调 {callback.__name__} 执行成功 ({duration:.2f}ms)")

            except Exception as e:
                duration = (datetime.now() - start).total_seconds() * 1000
                results.append(CallbackResult(
                    callback_name=callback.__name__,
                    success=False,
                    error=str(e),
                    duration_ms=duration
                ))

                logger.error(f"回调 {callback.__name__} 执行失败: {e}")

        event.callbacks_results = results
        return event

    def get_registered_callbacks(self) -> Dict[str, List[str]]:
        """获取已注册的回调列表"""
        return {
            event_type: [cb.__name__ for cb in callbacks]
            for event_type, callbacks in self._callbacks.items()
        }

    def clear_callbacks(self):
        """清空所有回调"""
        self._callbacks.clear()
```

#### 3.1.2 命令设计

| 命令 | 函数 | 描述 | 工时 |
|------|------|------|------|
| 无（内部模块） | EventDispatcher | 事件分发器内部模块 | 5h |

---

### 3.2 StateNotifier (状态通知器)

#### 3.2.1 类设计

```python
from typing import Optional
from dataclasses import dataclass
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)


@dataclass
class StateChangeEvent:
    """状态变更事件"""
    event_type: str  # todo.created, todo.completed, signoff.completed, phase.advanced, bug.fixed
    agent_id: str
    details: dict
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class StateNotifier:
    """状态通知器"""

    def __init__(self, webhook_config, dispatcher: Optional['EventDispatcher'] = None):
        """初始化状态通知器

        Args:
            webhook_config: WebhookConfig实例
            dispatcher: EventDispatcher实例（可选）
        """
        self.config = webhook_config
        self.dispatcher = dispatcher
        self._default_webhook_url: Optional[str] = None

    def set_default_webhook_url(self, url: str):
        """设置默认Webhook URL"""
        self._default_webhook_url = url

    def notify(self, event: StateChangeEvent, webhook_url: Optional[str] = None) -> bool:
        """发送状态变更通知

        Args:
            event: 状态变更事件
            webhook_url: 目标Webhook URL，默认使用配置的URL

        Returns:
            是否发送成功
        """
        target_url = webhook_url or self._default_webhook_url
        if not target_url:
            logger.warning("未配置Webhook URL，跳过通知")
            return False

        payload = self._format_payload(event)

        try:
            # 通过EventDispatcher分发（如果有注册）
            if self.dispatcher:
                from src.core.event_dispatcher import DispatchEvent
                dispatch_event = DispatchEvent(
                    event_type="state_notification",
                    source="oc-collab",
                    payload=payload
                )
                self.dispatcher.dispatch(dispatch_event)

            # 直接发送HTTP请求
            response = requests.post(
                target_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code in (200, 201, 204):
                logger.info(f"状态变更通知已发送: {event.event_type}")
                return True
            else:
                logger.error(f"状态变更通知发送失败: {response.status_code} - {response.text}")
                return False

        except requests.RequestException as e:
            logger.error(f"状态变更通知发送异常: {e}")
            return False

    def _format_payload(self, event: StateChangeEvent) -> dict:
        """格式化为GitHub兼容的Webhook Payload"""
        return {
            "action": event.event_type,
            "sender": {
                "login": event.agent_id
            },
            "repository": {
                "full_name": "oc-collab/state-notification"
            },
            "oc_collab": {
                "event_type": event.event_type,
                "timestamp": event.timestamp,
                "details": event.details
            },
            "ref": f"refs/heads/state-{event.event_type.replace('.', '-')}"
        }

    def notify_todo_created(self, todo_id: str, content: str, agent_id: str):
        """通知TODO创建"""
        event = StateChangeEvent(
            event_type="todo.created",
            agent_id=agent_id,
            details={"todo_id": todo_id, "content": content}
        )
        return self.notify(event)

    def notify_todo_completed(self, todo_id: str, content: str, agent_id: str):
        """通知TODO完成"""
        event = StateChangeEvent(
            event_type="todo.completed",
            agent_id=agent_id,
            details={"todo_id": todo_id, "content": content}
        )
        return self.notify(event)

    def notify_signoff_completed(self, stage: str, agent_id: str):
        """通知签署完成"""
        event = StateChangeEvent(
            event_type="signoff.completed",
            agent_id=agent_id,
            details={"stage": stage}
        )
        return self.notify(event)

    def notify_phase_advanced(self, from_phase: str, to_phase: str, agent_id: str):
        """通知阶段推进"""
        event = StateChangeEvent(
            event_type="phase.advanced",
            agent_id=agent_id,
            details={"from": from_phase, "to": to_phase}
        )
        return self.notify(event)

    def notify_bug_fixed(self, bug_id: str, description: str, agent_id: str):
        """通知Bug修复"""
        event = StateChangeEvent(
            event_type="bug.fixed",
            agent_id=agent_id,
            details={"bug_id": bug_id, "description": description}
        )
        return self.notify(event)
```

#### 3.2.2 命令设计

| 命令 | 函数 | 描述 | 工时 |
|------|------|------|------|
| `oc-collab webhook notify test` | webhook_notify_test | 测试通知功能 | 1h |

---

### 3.3 HMACValidator (HMAC签名验证)

#### 3.3.1 类设计

```python
import hmac
import hashlib
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)


class SignaturePlatform(Enum):
    """签名验证平台"""
    GITHUB = "github"
    GITEE = "gitee"


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    platform: Optional[SignaturePlatform]
    error: Optional[str] = None


class HMACValidator:
    """HMAC签名验证器"""

    # GitHub和Gitee的签名Header
    GITHUB_SIGNATURE_HEADER = "X-Hub-Signature-256"
    GITEE_TOKEN_HEADER = "X-Gitee-Token"

    def __init__(self, secret: str, skip_verification: bool = False):
        """初始化验证器

        Args:
            secret: Webhook Secret
            skip_verification: 是否跳过验证（开发模式）
        """
        self.secret = secret
        self.skip_verification = skip_verification or \
            os.environ.get("OC_COLLAB_WEBHOOK_SKIP_VERIFY", "").lower() == "true"

    def validate_github(self, body: bytes, signature: str) -> ValidationResult:
        """验证GitHub Webhook签名

        Args:
            body: 请求体
            signature: X-Hub-Signature-256 header

        Returns:
            验证结果
        """
        if self.skip_verification:
            logger.debug("开发模式：跳过GitHub签名验证")
            return ValidationResult(is_valid=True, platform=SignaturePlatform.GITHUB)

        if not signature:
            logger.warning("GitHub签名缺失")
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITHUB,
                error="Missing X-Hub-Signature-256 header"
            )

        if not signature.startswith("sha256="):
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITHUB,
                error="Invalid signature format (expected sha256=)"
            )

        expected_sig = "sha256=" + hmac.new(
            self.secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(signature, expected_sig):
            logger.info("GitHub签名验证通过")
            return ValidationResult(is_valid=True, platform=SignaturePlatform.GITHUB)
        else:
            logger.warning("GitHub签名验证失败")
            self._log_security_warning("GitHub", "signature mismatch")
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITHUB,
                error="Signature mismatch"
            )

    def validate_gitee(self, body: bytes, token: str) -> ValidationResult:
        """验证Gitee Webhook签名

        Args:
            body: 请求体
            token: X-Gitee-Token header

        Returns:
            验证结果
        """
        if self.skip_verification:
            logger.debug("开发模式：跳过Gitee Token验证")
            return ValidationResult(is_valid=True, platform=SignaturePlatform.GITEE)

        if not token:
            logger.warning("Gitee Token缺失")
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITEE,
                error="Missing X-Gitee-Token header"
            )

        if hmac.compare_digest(token, self.secret):
            logger.info("Gitee Token验证通过")
            return ValidationResult(is_valid=True, platform=SignaturePlatform.GITEE)
        else:
            logger.warning("Gitee Token验证失败")
            self._log_security_warning("Gitee", "token mismatch")
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITEE,
                error="Token mismatch"
            )

    def validate_request(
        self,
        body: bytes,
        headers: dict
    ) -> Tuple[ValidationResult, Optional[SignaturePlatform]]:
        """综合验证请求（自动检测平台）

        Args:
            body: 请求体
            headers: 请求头

        Returns:
            (验证结果, 检测到的平台)
        """
        github_sig = headers.get(self.GITHUB_SIGNATURE_HEADER)
        gitee_token = headers.get(self.GITEE_TOKEN_HEADER)

        if github_sig:
            result = self.validate_github(body, github_sig)
            return result, SignaturePlatform.GITHUB if result.is_valid else None

        if gitee_token:
            result = self.validate_gitee(body, gitee_token)
            return result, SignaturePlatform.GITEE if result.is_valid else None

        return ValidationResult(
            is_valid=False,
            platform=None,
            error="No signature header found"
        ), None

    def _log_security_warning(self, platform: str, reason: str):
        """记录安全警告"""
        logger.warning(
            f"⚠️  [{platform.upper()}] Webhook安全警告: {reason}"
        )
        # 可以扩展为发送告警到监控系统
```

#### 3.3.2 命令设计

| 命令 | 函数 | 描述 | 工时 |
|------|------|------|------|
| 无（内部模块） | HMACValidator | HMAC签名验证内部模块 | 3h |

---

### 3.4 RulesInitializer (规则初始化器)

#### 3.4.1 类设计

```python
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import shutil
import logging
import os

logger = logging.getLogger(__name__)


@dataclass
class InitResult:
    """初始化结果"""
    success: bool
    created_files: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class RulesInitializer:
    """规则初始化器"""

    # 需要初始化的核心文件
    CORE_FILES = [
        ("AGENTS.md", "核心协作规则"),
        ("skills/oc_collab_deployment_guide/content.md", "部署指南"),
        ("skills/oc_collab_development_guide/content.md", "开发指南"),
        ("skills/oc_collab_requirements_guide/content.md", "需求指南"),
        ("skills/oc_collab_outline_design_guide/content.md", "概要设计指南"),
        ("skills/oc_collab_detailed_design_guide/content.md", "详细设计指南"),
    ]

    # 需要初始化的目录
    CORE_DIRS = [
        ("skills/", "Skill目录"),
        ("docs/00-memos/", "备忘录目录"),
    ]

    def __init__(self, project_path: Optional[str] = None):
        """初始化规则初始化器

        Args:
            project_path: 项目路径，默认当前目录
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.initialized_files: List[str] = []
        self.skipped_files: List[str] = []

    def init(self, force: bool = False) -> InitResult:
        """执行规则初始化

        Args:
            force: 是否强制覆盖已存在的文件

        Returns:
            初始化结果
        """
        result = InitResult()
        self.initialized_files = []
        self.skipped_files = []

        # 创建目录
        for dir_path, description in self.CORE_DIRS:
            full_path = self.project_path / dir_path
            if full_path.exists():
                logger.info(f"目录已存在，跳过: {dir_path}")
            else:
                full_path.mkdir(parents=True, exist_ok=True)
                result.created_files.append(dir_path)
                logger.info(f"创建目录: {dir_path}")

        # 初始化文件（这里只创建占位符，实际内容需要从模板或默认内容生成）
        for filename, description in self.CORE_FILES:
            file_path = self.project_path / filename

            if file_path.exists():
                if force:
                    logger.warning(f"强制覆盖: {filename}")
                    self._create_placeholder(file_path, description)
                    result.created_files.append(filename)
                else:
                    logger.info(f"文件已存在，跳过: {filename}")
                    result.skipped_files.append(filename)
                    result.skipped_files.append(filename)
            else:
                self._create_placeholder(file_path, description)
                result.created_files.append(filename)
                logger.info(f"创建文件: {filename}")

        result.success = len(result.errors) == 0
        return result

    def _create_placeholder(self, file_path: Path, description: str):
        """创建占位符文件

        Args:
            file_path: 文件路径
            description: 文件描述
        """
        placeholder_content = f"""# {file_path.name}

> 此文件由 `oc-collab rules init` 自动生成

## 说明

{description}

## 待办

- [ ] 完善此文件内容
"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(placeholder_content, encoding='utf-8')

    def check_status(self) -> dict:
        """检查规则初始化状态"""
        status = {
            "initialized": [],
            "missing": [],
            "outdated": []
        }

        for filename, _ in self.CORE_FILES:
            file_path = self.project_path / filename
            if file_path.exists():
                status["initialized"].append(filename)
            else:
                status["missing"].append(filename)

        for dir_path, _ in self.CORE_DIRS:
            dir_path = self.project_path / dir_path
            if dir_path.exists():
                status["initialized"].append(dir_path + "/")
            else:
                status["missing"].append(dir_path + "/")

        return status

    def reset(self, force: bool = False) -> InitResult:
        """重置规则（删除已初始化的文件）

        Args:
            force: 是否强制删除

        Returns:
            重置结果
        """
        result = InitResult()

        if not force:
            logger.warning("重置需要 --force 参数")
            result.errors.append("需要 --force 参数")
            return result

        for filename, _ in self.CORE_FILES:
            file_path = self.project_path / filename
            if file_path.exists():
                file_path.unlink()
                result.created_files.append(f"[已删除] {filename}")
                logger.info(f"已删除: {filename}")

        for dir_path, _ in self.CORE_DIRS:
            dir_path = self.project_path / dir_path
            if dir_path.exists():
                shutil.rmtree(dir_path)
                result.created_files.append(f"[已删除] {dir_path}/")
                logger.info(f"已删除目录: {dir_path}")

        result.success = True
        return result
```

#### 3.4.2 命令设计

| 命令 | 函数 | 描述 | 工时 |
|------|------|------|------|
| `oc-collab rules init [--force]` | rules_init_command | 初始化框架规则 | 1h |

---

## 4. 数据结构

### 4.1 状态文件Schema

```yaml
# state/project_state.yaml
v2.2.8:
  deployment:
    status: pending
    phase: pending
  design:
    agent1_signoff: true
    agent2_signoff: true
    status: APPROVED
  development:
    phase: pending
    started_at: null
    completed_at: null
    status: pending
  features:
    - F-WEB-003: EventDispatcher
    - F-WEB-004: StateNotifier
    - F-WEB-005: HMACValidator
    - F-INIT-001: RulesInitializer
  testing:
    phase: pending
    status: pending
    unit_tests: 0
    blackbox_tests: 0
  version: 2.2.8
  workload: 26h
```

### 4.2 配置Schema

```yaml
# config/webhook.yaml (复用v2.2.7)
webhook:
  github:
    secret: "${WEBHOOK_GITHUB_SECRET}"
    events:
      - push
      - pull_request
  gitee:
    secret: "${WEBHOOK_GITEE_SECRET}"
    events:
      - push_hooks
      - merge_request_hooks
```

### 4.3 Webhook Payload格式

```json
{
  "action": "todo.created",
  "sender": {
    "login": "agent1"
  },
  "repository": {
    "full_name": "oc-collab/state-notification"
  },
  "oc_collab": {
    "event_type": "todo.created",
    "timestamp": "2026-02-13T12:00:00Z",
    "details": {
      "todo_id": "TODO-001",
      "content": "测试任务"
    }
  },
  "ref": "refs/heads/state-todo-created"
}
```

---

## 5. 算法与逻辑

### 5.1 核心流程

#### EventDispatcher事件分发流程

```
开始 → 注册回调 → 接收事件 → 过滤事件 → 分发到回调 → 收集结果 → 记录日志 → 结束
                    │
                    └── 异常处理 ──→ 记录错误 ──→ 继续处理其他回调
```

#### StateNotifier通知发送流程

```
状态变更事件 ──→ 格式化Payload ──→ 获取Webhook URL ──→ 发送HTTP POST
                    │
                    └── 失败 ──→ 记录日志 ──→ 返回False
```

#### HMACValidator签名验证流程

```
接收请求 ──→ 提取Header ──→ 选择验证策略 ──→ 执行验证 ──→ 返回结果
                                        │
                    ┌───────────────────┘
                    │
                    ▼
            GitHub: sha256=xxx
                    │
                    ▼
            Gitee: X-Gitee-Token
```

#### RulesInitializer初始化流程

```
oc-collab rules init ──→ 检查现有文件 ──→ 创建目录 ──→ 创建占位符文件
                                    │
                    ┌───────────────┘
                    │
                    ▼
            已存在? ──→ 是 ──→ force? ──→ 否 ──→ 跳过
                    │           │
                    ▼           ▼
                是      覆盖并创建
```

### 5.2 状态机

| 当前状态 | 事件 | 下一状态 |
|----------|------|----------|
| pending | rules init | in_progress |
| in_progress | 初始化完成 | completed |
| completed | 重置(--force) | pending |

### 5.3 边界条件

| 边界条件 | 处理方式 |
|----------|----------|
| Webhook URL未配置 | 记录警告，跳过发送 |
| HMAC签名验证失败 | 记录安全警告，返回401 |
| 回调执行超时 | 记录错误，继续处理其他回调 |
| 文件已存在（无--force） | 跳过，不覆盖 |
| 目录已存在 | 跳过，不重复创建 |

---

## 6. API设计

### 6.1 CLI命令

| 命令 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `oc-collab rules init` | [--force] | 0=成功, 1=失败 | 初始化框架规则 |
| `oc-collab rules status` | 无 | 0=成功 | 检查规则初始化状态 |
| `oc-collab webhook notify test` | [--url URL] | 0=成功, 1=失败 | 测试通知功能 |

### 6.2 错误码

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 1001 | 参数错误 | 提示用户正确用法 |
| 1002 | 文件已存在 | 添加--force参数覆盖 |
| 1003 | Webhook URL未配置 | 提示配置webhook.yaml |
| 1004 | 签名验证失败 | 返回401，拒绝请求 |
| 1005 | 网络请求失败 | 记录日志，返回错误 |

---

## 7. 错误处理

### 7.1 异常类型

| 异常类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| ValidationError | 参数验证失败 | 返回错误信息，退出码1 |
| WebhookConfigError | Webhook配置错误 | 记录错误，跳过处理 |
| NetworkError | 网络请求失败 | 记录警告，重试1次 |
| SignatureError | HMAC签名验证失败 | 记录安全警告，返回401 |

### 7.2 日志策略

```python
# 日志级别
logger.debug("详细调试信息")
logger.info("操作成功")
logger.warning("警告信息，可恢复")
logger.error("错误信息，需要关注")
logger.critical("严重错误")
```

---

## 8. 测试策略

### 8.1 单元测试

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| EventDispatcher.register_callback | 注册有效回调 | 返回callback_id |
| EventDispatcher.register_duplicate | 注册重复回调 | 抛出ValueError |
| EventDispatcher.dispatch | 分发事件到回调 | 所有回调执行 |
| EventDispatcher.clear | 清空回调 | 回调列表为空 |
| StateNotifier.notify | 发送状态通知 | HTTP POST成功 |
| StateNotifier._format_payload | 格式化Payload | GitHub兼容格式 |
| HMACValidator.validate_github | 验证GitHub签名 | 签名匹配返回True |
| HMACValidator.validate_gitee | 验证Gitee Token | Token匹配返回True |
| HMACValidator.skip_mode | 跳过验证模式 | 始终返回True |
| RulesInitializer.init | 初始化规则 | 创建目录和文件 |
| RulesInitializer.status | 检查状态 | 返回初始化状态 |

### 8.2 E2E测试

| 测试场景 | 测试步骤 | 验收标准 |
|----------|----------|----------|
| rules init | 1. 执行rules init<br>2. 检查生成文件 | 文件生成成功 |
| rules init --force | 1. 修改AGENTS.md<br>2. 执行rules init --force<br>3. 检查文件被覆盖 | 文件被覆盖 |
| webhook notify | 1. 配置webhook.yaml<br>2. 执行webhook notify test | 通知发送成功 |
| webhook签名验证 | 1. 发送带签名请求<br>2. 检查验证结果 | 签名验证正确 |

---

## 9. 签署确认

### Agent 2 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-13 | ✅ |

### Agent 1 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-13
**状态**: DRAFT / READY / APPROVED
