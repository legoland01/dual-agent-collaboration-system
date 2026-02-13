# v2.2.8 需求分析

**版本**: v2  
**日期**: 2026-02-13  
**Agent**: Agent 1 (产品负责人)  
**关联提案**: PROPOSAL-2026-02-001 (规则自动加载机制 - 待评审)  
**状态**: APPROVED

---

## 0. 架构映射

**参考文档**: `docs/00-architecture/CORE_ARCHITECTURE.md`

| 版本 | 功能 | 架构模块 | 映射路径 |
|------|------|----------|----------|
| v2.2.7 | Skill行为测试 | 9.2 Skill管理 | 核心架构 → 9.2 |
| v2.2.7 | Webhook配置/监听 | 10.3 Webhook通知 | 核心架构 → 10.3 |
| **v2.2.8** | **Webhook分发/通知** | **10.3 Webhook通知** | **核心架构 → 10.3** |
| **v2.2.8** | **Webhook HMAC验证** | **10.3 Webhook通知** | **核心架构 → 10.3** |
| **v2.2.8** | **oc-collab rules init** | **5.1 版本发布** | **核心架构 → 5.1** |

---

## 1. 背景

### 1.1 v2.2.7 回顾

v2.2.7 完成了 Webhook 基础设施的建设：
- WebhookConfig: 配置管理
- EventListener: 事件监听 + 崩溃恢复
- Skill行为测试框架

### 1.2 v2.2.8 目标

在 v2.2.7 基础上，完成 Webhook 通知体系的最后两块拼图，并新增安全验证和初始化命令：

| ID | 功能名称 | 来源 | 工时 |
|----|----------|------|------|
| F-WEB-003 | EventDispatcher - 事件分发器 | v2.2.7规划 | 5h |
| F-WEB-004 | StateNotifier - 状态通知器 | v2.2.7规划 | 5h |
| F-WEB-005 | Webhook HMAC签名验证 | v2.2.7规划(补充) | 3h |
| F-INIT-001 | oc-collab init 初始化命令 | PROPOSAL-2026-02-001 | 3h |

**开发工时**: 16h | **总工时**: 26h

---

## 2. 功能需求

### 2.1 功能列表

| ID | 功能名称 | 来源 | 优先级 | 工时 | 架构模块 |
|----|----------|------|--------|------|----------|
| F-WEB-003 | EventDispatcher - 事件分发器 | v2.2.7规划 | P1 | 5h | 10.3 |
| F-WEB-004 | StateNotifier - 状态通知器 | v2.2.7规划 | P1 | 5h | 10.3 |
| F-WEB-005 | Webhook HMAC签名验证 | 安全性补充 | P2 | 3h | 10.3 |
| F-INIT-001 | oc-collab rules init 初始化命令 | PROPOSAL-2026-02-001 | P2 | 3h | 5.1 |

### 2.2 F-WEB-003: EventDispatcher

#### 2.2.1 需求描述

EventDispatcher 负责将 EventListener 接收的事件分发给注册的回调函数。

```
GitHub/Gitee Webhook
        │
        ▼
┌───────────────────┐
│   EventListener   │  ← v2.2.7 已完成
│   (事件监听)      │
└─────────┬─────────┘
          │ 解析后的事件
          ▼
┌───────────────────┐
│  EventDispatcher  │  ← v2.2.8 新增
│   (事件分发)      │
└─────────┬─────────┘
          │
          ▼
    ┌────┴────┐
    │ 回调函数 │
    └─────────┘
```

#### 2.2.2 功能列表

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 回调注册 | 支持注册多个回调函数 | P1 |
| 事件过滤 | 根据事件类型过滤分发 | P1 |
| 错误处理 | 回调执行失败时的处理 | P2 |
| 重试机制 | 回调失败时自动重试 | P2 |

#### 2.2.3 输入输出

| 类型 | 内容 |
|------|------|
| 输入 | EventListener 解析后的 GitHub/Gitee 事件 |
| 输出 | 调用注册的回调函数 |

#### 2.2.4 验收标准

- [ ] 支持注册至少 5 个回调函数
- [ ] 支持按事件类型过滤
- [ ] 回调执行失败时记录错误日志
- [ ] 单元测试覆盖率 ≥80%

---

### 2.3 F-WEB-004: StateNotifier

#### 2.3.1 需求描述

StateNotifier 负责将 oc-collab 的状态变更通知到外部系统（如 Webhook URL）。

#### 2.3.2 状态变更事件

| 事件类型 | 触发条件 |
|----------|----------|
| todo.created | 创建 TODO 时 |
| todo.completed | 完成 TODO 时 |
| signoff.completed | 签署完成时 |
| phase.advanced | 阶段推进时 |
| bug.fixed | Bug 修复时 |

#### 2.3.3 功能列表

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 状态变更检测 | 检测 oc-collab 状态变更 | P1 |
| 事件格式化 | 将状态变更格式化为 Webhook Payload | P1 |
| Webhook 发送 | 发送 HTTP POST 请求 | P1 |
| 发送失败处理 | 失败时记录日志，支持重试 | P2 |

#### 2.3.4 输入输出

| 类型 | 内容 |
|------|------|
| 输入 | oc-collab 状态变更事件 |
| 输出 | HTTP POST 请求到配置的 Webhook URL |

#### 2.3.5 验收标准

- [ ] 支持至少 5 种状态变更事件
- [ ] Payload 格式兼容 GitHub Webhook 格式
- [ ] 发送失败时记录错误日志
- [ ] 单元测试覆盖率 ≥80%

---

### 2.4 F-WEB-005: Webhook HMAC签名验证

#### 2.4.1 需求描述

Webhook HMAC签名验证确保接收到的 Webhook 请求来自可信的 GitHub/Gitee 服务器，防止恶意请求。

#### 2.4.2 功能列表

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 签名提取 | 从 HTTP Header 提取 HMAC-SHA256 签名 | P1 |
| 签名验证 | 验证请求签名是否匹配 | P1 |
| 容错处理 | 支持可选验证（开发环境） | P2 |

#### 2.4.3 输入输出

| 类型 | 内容 |
|------|------|
| 输入 | HTTP 请求（Body + Headers） |
| 输出 | 验证通过/失败 boolean |

#### 2.4.4 验收标准

- [ ] 支持 GitHub X-Hub-Signature-256 验证
- [ ] 支持 Gitee X-Gitee-Token 验证
- [ ] 签名不匹配时记录安全警告
- [ ] 支持环境变量跳过验证（开发模式）
- [ ] 单元测试覆盖率 ≥80%

---

### 2.5 F-INIT-001: oc-collab rules init 规则初始化

#### 2.5.1 需求描述

**澄清**：此功能不同于现有的 `oc-collab init`（项目信息初始化）。

| 命令 | 功能 | 产出 |
|------|------|------|
| `oc-collab init <project>` | 项目信息初始化 | `project_state.yaml` |
| `oc-collab rules init` | oc-collab 框架规则初始化 | `AGENTS.md`、`skills/`、`docs/00-memos/` |

#### 2.5.2 功能列表

| 功能项 | 描述 | 优先级 |
|--------|------|--------|
| 默认规则生成 | 复制内置 AGENTS.md 默认规则 | P1 |
| 目录结构创建 | 创建 skills/、docs/00-memos/ | P1 |
| 跳过已存在 | 检测到 AGENTS.md 时跳过或询问 | P2 |
| 覆盖选项 | 支持 `--force` 强制覆盖 | P2 |

#### 2.5.3 输入输出

| 类型 | 内容 |
|------|------|
| 输入 | 当前目录（无参数） |
| 输出 | 目录结构 + AGENTS.md |

#### 2.5.4 验收标准

- [ ] `oc-collab rules init` 命令存在且可执行
- [ ] 生成 `AGENTS.md`（内置默认规则）
- [ ] 生成 `skills/` 目录
- [ ] 生成 `docs/00-memos/` 目录
- [ ] 检测到已有 `AGENTS.md` 时跳过（无 `--force`）
- [ ] `--force` 参数可覆盖已有文件
- [ ] 黑盒测试通过

#### 2.5.5 为何不需要推迟

| 维度 | 分析 | 结论 |
|------|------|------|
| **复杂度** | 低 - 文件复制 + 模板生成 | ✅ |
| **依赖** | 无外部依赖 | ✅ |
| **工时** | 3h（已在16h内） | ✅ |
| **风险** | 与现有 init 无关（子命令区分） | ✅ |

---

## 3. 技术设计

### 3.1 模块架构

```
src/
├── core/
│   ├── event_dispatcher.py    # EventDispatcher
│   └── state_notifier.py     # StateNotifier
│
├── cli/
│   └── webhook_commands.py    # 新增 webhook notify 命令（可选）
│
└── config/
    └── webhook_config.py     # 复用 v2.2.7 的配置
```

### 3.2 EventDispatcher 设计

```python
class EventDispatcher:
    def __init__(self):
        self.callbacks: List[Callable] = []
        self.filters: Dict[str, List[Callable]] = {}
    
    def register_callback(self, callback: Callable, event_types: List[str] = None):
        """注册回调函数"""
        pass
    
    def dispatch(self, event: GitHubEvent):
        """分发事件到回调函数"""
        pass
```

### 3.3 StateNotifier 设计

```python
class StateNotifier:
    def __init__(self, config: WebhookConfig):
        self.config = config
    
    def notify(self, event_type: str, data: dict):
        """发送状态变更通知"""
        pass
    
    def _format_payload(self, event_type: str, data: dict) -> dict:
        """格式化 Webhook Payload"""
        pass
```

---

## 4. 依赖关系

### 4.1 内部依赖

| 模块 | 依赖 | 说明 |
|------|------|------|
| EventDispatcher | EventListener | 接收解析后的事件 |
| StateNotifier | EventDispatcher | 利用分发机制发送通知 |
| StateNotifier | WebhookConfig | 获取 Webhook URL 配置 |

### 4.2 外部依赖

| 依赖 | 版本 | 说明 |
|------|------|------|
| requests | - | HTTP 请求（已存在于 requirements） |
| PyYAML | - | 配置文件解析（已存在） |

---

## 5. 工时估算

| 阶段 | 任务 | 工时 |
|------|------|------|
| 需求分析 | v2.2.8 需求文档 | 1h |
| 概要设计 | 模块架构设计 | 2h |
| 详细设计 | 类结构、接口设计 | 3h |
| 开发 | EventDispatcher (F-WEB-003) | 5h |
| 开发 | StateNotifier (F-WEB-004) | 5h |
| 开发 | Webhook HMAC验证 (F-WEB-005) | 3h |
| 开发 | oc-collab rules init (F-INIT-001) | 3h |
| 测试 | 单元测试 + 黑盒测试 | 4h |
| **合计** | | **26h** |

---

## 6. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Webhook URL 配置复杂 | 用户配置困难 | 复用 v2.2.7 的配置机制 |
| 网络不稳定导致发送失败 | 通知丢失 | 添加重试机制 |
| Payload 格式不兼容 | 接收方无法解析 | 参考 GitHub Webhook 格式 |

---

## 7. 关联文档

| 文档 | 说明 |
|------|------|
| `docs/01-requirements/requirements_v2.2.7.md` | v2.2.7 需求（上下文） |
| `docs/02-design/DETAIL-2026-02-v2.2.7.md` | v2.2.7 详细设计（基础设施） |
| `docs/02-design/OUTLINE_v2.2.8.md` | 概要设计（待创建） |
| `src/core/event_listener.py` | EventListener（v2.2.7） |
| `src/core/webhook_config.py` | WebhookConfig（v2.2.7） |

---

## 8. 开放问题

| 问题 | 负责人 | 需澄清 |
|------|--------|--------|
| StateNotifier 是否需要支持 Webhook URL 模板？ | Agent2 | 支持 Jinja2 模板？ |
| 是否需要支持 Webhook 重试次数配置？ | Agent2 | 写入配置文件还是命令行参数？ |
| 通知发送是否需要确认 ACK？ | Agent2 | 简化模式还是可靠模式？ |
| oc-collab rules init 内置规则内容范围 | Agent1 | **完整规则：AGENTS.md + 全部skill** |

---

**创建人**: Agent 1  
**日期**: 2026-02-13  
**状态**: APPROVED

---

**签署**:
- Agent 1 (产品负责人): 创建需求 ✅ 2026-02-13
- Agent 2 (技术负责人): 技术评审通过 ✅ 2026-02-13
