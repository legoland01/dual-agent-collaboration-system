# 详细设计说明书：oc-collab v2.2.9

**版本**: v1
**创建日期**: 2026-02-14
**作者**: Agent 2 (开发负责人)
**关联概要设计**: OUTLINE_v2.2.9.md
**版本号**: 2.2.9
**状态**: DRAFT

---

## 1. 功能模块映射

### 1.1 映射表

| 功能模块 (概要设计) | 技术模块 (详细设计) | 对应文件 |
|---------------------|---------------------|----------|
| StateNotifier集成todowrite | TodoWebhookNotifier | core/todo_webhook_notifier.py |
| StateNotifier集成signoff | SignoffWebhookNotifier | core/signoff_webhook_notifier.py |
| StateNotifier集成phase_advance | PhaseWebhookNotifier | core/phase_webhook_notifier.py |
| 自动Bug检测机制 | AutoBugDetector | core/auto_bug_detector.py |
| Agent Compliance CLI准入 | ComplianceEnforcer | core/compliance_enforcer.py |
| 规则自动加载 | RulesAutoLoader | core/rules_auto_loader.py |
| 部署文档同步自动化 | DeployDocSync | core/deploy_doc_sync.py |
| Webhook状态通知增强 | WebhookEnhancer | core/webhook_enhancer.py |

### 1.2 新增/变更文件

| 文件路径 | 功能 | 工时 |
|----------|------|------|
| src/core/todo_webhook_notifier.py | StateNotifier集成todowrite | 3h |
| src/core/signoff_webhook_notifier.py | StateNotifier集成signoff | 2h |
| src/core/phase_webhook_notifier.py | StateNotifier集成phase_advance | 2h |
| src/core/auto_bug_detector.py | 自动Bug检测机制 | 8h |
| src/core/compliance_enforcer.py | Agent Compliance CLI准入 | 7h |
| src/core/rules_auto_loader.py | 规则自动加载 | 5h |
| src/core/deploy_doc_sync.py | 部署文档同步自动化 | 3h |
| src/core/webhook_enhancer.py | Webhook状态通知增强 | 3h |
| src/cli/compliance_commands.py | compliance命令 | 2h |
| src/cli/rules_commands.py | rules init命令变更 | 1h |
| src/cli/deploy_commands.py | deploy check-docs命令 | 1h |

---

## 2. 技术架构

### 2.1 模块架构图

```
v2.2.9 技术架构

┌─────────────────────────────────────────────────────────────────┐
│                        CLI Layer                                  │
├─────────────────────────────────────────────────────────────────┤
│  todowrite → TodoWebhookNotifier → StateNotifier → Webhook     │
│  signoff   → SignoffWebhookNotifier → StateNotifier → Webhook  │
│  phase_advance → PhaseWebhookNotifier → StateNotifier → Webhook│
│  compliance check/report → ComplianceEnforcer                   │
│  rules init → RulesAutoLoader                                   │
│  deploy check-docs → DeployDocSync                              │
├─────────────────────────────────────────────────────────────────┤
│                        Core Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  AutoBugDetector → StateNotifier / Bug Report Generator         │
│  WebhookEnhancer → 重试机制 / 状态追踪                           │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 模块 | 技术/库 | 版本 | 选型依据 |
|------|---------|------|----------|
| CLI框架 | Click | >=8.0 | 现有技术栈 |
| 配置解析 | PyYAML | >=6.0 | 现有依赖 |
| HTTP请求 | requests | >=2.0 | Webhook通知 |
| 状态管理 | 现有StateManager | - | 复用现有 |

---

## 3. 核心模块设计

### 3.1 TodoWebhookNotifier类设计

```python
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

@dataclass
class TodoCreatedPayload:
    event_type: str = "todo_created"
    timestamp: str = None
    agent_id: str = None
    todo_id: str = None
    content: str = None
    webhook_id: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
        if self.webhook_id is None:
            self.webhook_id = str(uuid.uuid4())

class TodoWebhookNotifier:
    """StateNotifier集成到todowrite"""
    
    def __init__(self, state_notifier=None, webhook_config=None):
        self.state_notifier = state_notifier
        self.webhook_config = webhook_config
    
    def notify_todo_created(self, todo_id: str, content: str, agent_id: str) -> bool:
        """
        TOD创建时发送Webhook通知
        
        Returns:
            True: 通知成功或已跳过
            False: 通知失败
        """
        # 检查Webhook是否配置
        if not self._is_webhook_configured():
            return True  # 静默跳过，不报错
        
        payload = TodoCreatedPayload(
            agent_id=agent_id,
            todo_id=todo_id,
            content=content
        )
        
        return self._send_webhook(payload)
    
    def _is_webhook_configured(self) -> bool:
        """检查Webhook URL是否已配置"""
        # 复用现有webhook_config逻辑
        pass
    
    def _send_webhook(self, payload: TodoCreatedPayload) -> bool:
        """发送Webhook通知"""
        # 复用现有StateNotifier逻辑
        pass
```

### 3.2 AutoBugDetector类设计

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

@dataclass
class BugReport:
    bug_id: str
    bug_type: str
    description: str
    related_todo: Optional[str]
    detected_at: str
    detected_by: str

class AutoBugDetector:
    """自动Bug检测机制"""
    
    BUG_TYPES = {
        "DOCUMENT_STATUS_NOT_UPDATED": r"TODO.*completed.*document.*not.*updated",
        "SIGNOFF_INCOMPLETE": r"signoff.*incomplete",
        "MISSING_REQUIRED_FILE": r"required.*file.*missing",
    }
    
    def __init__(self, state_manager=None, doc_generator=None):
        self.state_manager = state_manager
        self.doc_generator = doc_generator
    
    def check_todo_completion(self, todo_id: str) -> List[BugReport]:
        """
        TODO完成时检查文档状态是否更新
        
        Returns:
            Bug报告列表
        """
        bugs = []
        
        # 检查TODO关联的文档状态
        pass
        
        return bugs
    
    def check_signoff_completion(self, stage: str) -> List[BugReport]:
        """
        评审完成时检查签署是否完成
        """
        pass
    
    def check_command_result(self, command: str, result: Dict) -> List[BugReport]:
        """
        命令执行后检查返回值是否异常
        """
        bugs = []
        
        # 检测异常
        if result.get("return_code") != 0:
            bug = BugReport(
                bug_id=self._generate_bug_id(),
                bug_type="COMMAND_FAILED",
                description=f"Command {command} failed: {result.get('error')}",
                related_todo=None,
                detected_at=datetime.utcnow().isoformat() + "Z",
                detected_by="AutoBugDetector"
            )
            bugs.append(bug)
        
        return bugs
    
    def _generate_bug_id(self) -> str:
        """生成Bug ID"""
        date = datetime.now().strftime("%Y%m%d")
        return f"BUG-{date}-XXX"
    
    def generate_bug_report(self, bug: BugReport) -> str:
        """生成Bug报告文件"""
        pass
```

### 3.3 ComplianceEnforcer类设计

```python
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class AgentRole(Enum):
    AGENT_1 = "agent1"
    AGENT_2 = "agent2"

class CommandType(Enum):
    TODOWRITE = "todowrite"
    TODOEDIT = "todoedit"
    OTHER = "other"

class ComplianceLevel(Enum):
    BLOCK = "block"
    WARN = "warn"
    ALLOW = "allow"

@dataclass
class ComplianceResult:
    allowed: bool
    level: ComplianceLevel
    message: str

class ComplianceEnforcer:
    """Agent Compliance CLI准入检查"""
    
    # Agent1禁用的命令
    DISABLED_COMMANDS = {
        AgentRole.AGENT_1: [
            CommandType.TODOWRITE,
            CommandType.TODOEDIT,
        ]
    }
    
    def __init__(self, agent_role: AgentRole, command_type: CommandType):
        self.agent_role = agent_role
        self.command_type = command_type
    
    def check(self) -> ComplianceResult:
        """
        检查命令是否允许执行
        
        Returns:
            ComplianceResult: 检查结果
        """
        # Agent2始终允许
        if self.agent_role == AgentRole.AGENT_2:
            return ComplianceResult(
                allowed=True,
                level=ComplianceLevel.ALLOW,
                message=""
            )
        
        # Agent1检查
        disabled_commands = self.DISABLED_COMMANDS.get(self.agent_role, [])
        
        if self.command_type in disabled_commands:
            return ComplianceResult(
                allowed=False,
                level=ComplianceLevel.BLOCK,
                message=self._get_block_message()
            )
        
        return ComplianceResult(allowed=True, level=ComplianceLevel.ALLOW, message="")
    
    def _get_block_message(self) -> str:
        """获取阻止消息"""
        return (
            "⛔ Agent1禁止执行此命令。\n"
            "请创建TODO给Agent2执行。\n"
            "正确做法: oc-collab todowrite --content '任务描述' --agent 2"
        )
    
    def record_violation(self, result: ComplianceResult):
        """记录违规到state/compliance_violations.yaml"""
        pass
```

### 3.4 命令设计

| 命令 | 函数 | 描述 | 工时 |
|------|------|------|------|
| `oc-collab compliance check` | compliance_check() | 检查当前Agent合规状态 | 1h |
| `oc-collab compliance report` | compliance_report() | 生成合规报告 | 1h |
| `oc-collab deploy check-docs` | deploy_check_docs() | 检查部署文档同步 | 1h |
| `oc-collab rules init [--force]` | rules_init() | 初始化框架规则(变更) | 1h |

---

## 4. 数据结构

### 4.1 合规违规记录

```yaml
# state/compliance_violations.yaml
violations:
  - timestamp: "2026-02-14T00:00:00Z"
    agent_id: "agent1"
    command: "todowrite"
    reason: "Agent1禁止执行todowrite"
    blocked: true

total_violations: 1
```

### 4.2 Webhook通知统计

```yaml
# state/webhook_stats.yaml
notifications:
  - webhook_id: "uuid-v4"
    event_type: "todo_created"
    timestamp: "2026-02-14T00:00:00Z"
    status: "sent" | "failed" | "retried"
    retry_count: 0
```

### 4.3 Bug报告

```yaml
# docs/00-memos/BUG-20260214-XXX_自动检测.md
bug_id: BUG-20260214-XXX
type: DOCUMENT_STATUS_NOT_UPDATED
description: "TODO-XXX已完成，但关联文档未更新"
related_todo: TODO-XXX
detected_at: "2026-02-14T00:00:00Z"
detected_by: AutoBugDetector
```

---

## 5. 算法与逻辑

### 5.1 StateNotifier集成流程

```
todowrite执行
    │
    ├── 1. 创建TODO成功
    │
    ├── 2. 调用 TodoWebhookNotifier.notify_todo_created()
    │       │
    │       ├── 检查Webhook URL是否配置
    │       │       │
    │       │       ├── 未配置 → 返回True（静默跳过）
    │       │       │
    │       │       └── 已配置 → 继续
    │       │
    │       ├── 构建Payload
    │       │       │
    │       │       ├── event_type: "todo_created"
    │       │       ├── todo_id: "TODO-XXX"
    │       │       ├── content: "任务描述"
    │       │       ├── agent_id: "agent1"
    │       │       └── webhook_id: "uuid"
    │       │
    │       └── 发送Webhook
    │               │
    │               ├── HTTP POST到配置URL
    │               │
    │               └── 记录状态到webhook_stats.yaml
    │
    └── 返回成功
```

### 5.2 合规检查流程

```
Agent1执行命令
    │
    ├── ComplianceEnforcer.check()
    │       │
    │       ├── 检查Agent角色
    │       │       │
    │       │       ├── Agent1 → 检查命令类型
    │       │       │       │
    │       │       │       ├── todowrite/todoedit → 阻止
    │       │       │       │
    │       │       │       └── 其他 → 允许
    │       │       │
    │       │       └── Agent2 → 允许
    │       │
    │       └── 返回检查结果
    │
    ├── 允许 → 执行命令
    │
    └── 阻止
            │
            ├── 打印阻止消息
            ├── 记录违规到compliance_violations.yaml
            └── 返回错误码
```

### 5.3 边界条件

| 边界条件 | 处理方式 |
|----------|----------|
| Webhook URL未配置 | 静默跳过，不报错 |
| Webhook发送失败 | 记录日志，返回成功 |
| Agent1执行禁用命令 | 阻止执行，提示正确做法 |
| 合规违规记录失败 | 降级处理，不影响主流程 |

---

## 6. API设计

### 6.1 内部CLI命令

| 命令 | 参数 | 返回值 | 说明 |
|------|------|--------|------|
| `oc-collab compliance check` | 无 | 合规状态字符串 | 检查当前Agent合规状态 |
| `oc-collab compliance report` | 无 | Markdown表格 | 生成合规报告 |
| `oc-collab deploy check-docs` | 无 | 检查结果 | 检查CHANGELOG/README同步 |
| `oc-collab webhook status` | 无 | 通知统计 | 显示Webhook通知统计 |

### 6.2 错误码

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 1001 | Agent1禁止执行 | 提示创建TODO给Agent2 |
| 1002 | Webhook未配置 | 静默跳过 |
| 1003 | 部署文档未同步 | 阻止部署，提示同步 |

---

## 7. 错误处理

### 7.1 异常类型

| 异常类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| ComplianceViolationError | Agent1执行禁用命令 | 阻止，返回错误码 |
| WebhookNotConfiguredError | Webhook URL未配置 | 静默跳过 |
| WebhookSendError | Webhook发送失败 | 记录日志，重试1次 |
| DocumentSyncError | 部署文档未同步 | 阻止部署 |

### 7.2 异常处理流程

```
异常发生
    │
    ├── ComplianceViolationError
    │       └── 打印阻止消息，记录违规，返回错误码
    │
    ├── WebhookNotConfiguredError
    │       └── 静默跳过，继续执行
    │
    ├── WebhookSendError
    │       └── 重试1次，失败则记录日志
    │
    └── DocumentSyncError
            └── 阻止部署，提示同步文档
```

---

## 8. 测试策略

### 8.1 单元测试

| 测试项 | 测试内容 | 预期结果 |
|--------|----------|----------|
| TodoWebhookNotifier.notify_todo_created | Webhook已配置 | 发送通知成功 |
| TodoWebhookNotifier.notify_todo_created | Webhook未配置 | 静默跳过 |
| ComplianceEnforcer.check | Agent1执行todowrite | 返回阻止 |
| ComplianceEnforcer.check | Agent2执行todowrite | 返回允许 |
| AutoBugDetector.check_command_result | 命令成功 | 无Bug报告 |
| AutoBugDetector.check_command_result | 命令失败 | 生成Bug报告 |

### 8.2 E2E测试

| 测试场景 | 测试步骤 | 验收标准 |
|----------|----------|----------|
| Agent1执行todowrite | oc-collab todowrite --content "test" | 返回"Agent1禁止执行" |
| Agent2执行todowrite | oc-collab todowrite --content "test" --agent 2 | TODO创建成功，Webhook发送 |
| 合规报告 | oc-collab compliance report | 显示违规记录 |
| 部署文档检查 | oc-collab deploy check-docs | 显示检查结果 |

---

## 9. 签署确认

### Agent 2 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-14 | ✅ |

### Agent 1 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-14
**修订日期**: 2026-02-14
**状态**: READY
