# 概要设计说明书：oc-collab v2.2.8

**版本**: v1
**创建日期**: 2026-02-13
**作者**: Agent 1 (产品经理)
**关联需求**: docs/01-requirements/requirements_v2.2.8.md
**版本号**: v2.2.8
**状态**: DRAFT → 待评审

---

## 1. 功能模块概览

### 1.1 v2.2.8 功能模块图

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        oc-collab v2.2.8 Webhook完成与规则初始化                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                     CLI 命令层 (v2.2.8 新增/增强)                            │ │
│  ├─────────────────────────────────────────────────────────────────────────────┤ │
│  │  Webhook命令                            │ Rules命令                          │ │
│  │  ├─ oc-collab webhook notify           │ ├─ oc-collab rules init           │ │
│  │  └─ (现有 webhook init/start/stop)     │ └─ (现有 skill commands)          │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                    │                                              │
│                                    ▼                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         核心功能模块                                           │ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  【v2.2.8完成】Webhook模块                                               ││ │
│  │  │  ├─ EventDispatcher: 事件分发 [v2.2.8]                                  ││ │
│  │  │  ├─ StateNotifier: 状态通知 [v2.2.8]                                    ││ │
│  │  │  ├─ HMACValidator: HMAC签名验证 [v2.2.8]                               ││ │
│  │  │  └─ (现有 WebhookConfig, EventListener)                                 ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  │  ┌─────────────────────────────────────────────────────────────────────────┐│ │
│  │  │  【v2.2.8新增】规则初始化模块                                            ││ │
│  │  │  ├─ RulesInitializer: 规则初始化 [v2.2.8]                               ││ │
│  │  │  └─ DefaultRulesLoader: 默认规则加载 [v2.2.8]                          ││ │
│  │  └─────────────────────────────────────────────────────────────────────────┘│ │
│  │                                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 v2.2.8 功能清单

| 功能模块 | 功能 | 类型 | 工时 | 架构模块 |
|----------|------|------|------|----------|
| Webhook模块 | EventDispatcher (事件分发) | 新增 | 5h | 10.3 |
| Webhook模块 | StateNotifier (状态通知) | 新增 | 5h | 10.3 |
| Webhook模块 | HMACValidator (HMAC签名验证) | 新增 | 3h | 10.3 |
| Rules模块 | RulesInitializer (规则初始化) | 新增 | 3h | 5.1 |

**开发工时**: 16h | **总工时**: 26h

---

## 2. 模块详细设计

### 2.1 EventDispatcher (事件分发器)

#### 2.1.1 职责

将 EventListener 接收的事件分发给注册的回调函数。

#### 2.1.2 依赖关系

| 依赖模块 | 说明 |
|----------|------|
| EventListener | 接收解析后的 GitHub/Gitee 事件 |
| WebhookConfig | 获取分发配置 |

#### 2.1.3 关键设计决策

| 决策项 | 方案 | 理由 |
|--------|------|------|
| 回调注册 | 内存注册表 | 轻量，适合 CLI 场景 |
| 事件过滤 | 类型白名单 | 简单高效 |
| 错误处理 | 记录日志，跳过失败回调 | 不阻塞分发 |

#### 2.1.4 输入输出

| 类型 | 内容 |
|------|------|
| 输入 | EventListener 解析后的 GitHub/Gitee 事件 |
| 输出 | 调用注册的回调函数 |

---

### 2.2 StateNotifier (状态通知器)

#### 2.2.1 职责

将 oc-collab 的状态变更通知到外部系统（如 Webhook URL）。

#### 2.2.2 状态变更事件

| 事件类型 | 触发条件 |
|----------|----------|
| todo.created | 创建 TODO 时 |
| todo.completed | 完成 TODO 时 |
| signoff.completed | 签署完成时 |
| phase.advanced | 阶段推进时 |
| bug.fixed | Bug 修复时 |

#### 2.2.3 依赖关系

| 依赖模块 | 说明 |
|----------|------|
| EventDispatcher | 利用分发机制发送通知 |
| WebhookConfig | 获取 Webhook URL 配置 |

#### 2.2.4 关键设计决策

| 决策项 | 方案 | 理由 |
|--------|------|------|
| Payload格式 | GitHub兼容格式 | 通用性好 |
| 发送失败 | 记录日志，不重试 | 简化优先 |
| 发送确认 | 不确认ACK | 默认简化模式 |

#### 2.2.5 输入输出

| 类型 | 内容 |
|------|------|
| 输入 | oc-collab 状态变更事件 |
| 输出 | HTTP POST 请求到配置的 Webhook URL |

---

### 2.3 HMACValidator (HMAC签名验证)

#### 2.3.1 职责

验证 Webhook 请求的 HMAC 签名，确保来源可信。

#### 2.3.2 支持平台

| 平台 | Header | 签名算法 |
|------|--------|----------|
| GitHub | X-Hub-Signature-256 | HMAC-SHA256 |
| Gitee | X-Gitee-Token | 简单Token |

#### 2.3.3 关键设计决策

| 决策项 | 方案 | 理由 |
|--------|------|------|
| 验证模式 | 默认开启 | 安全优先 |
| 开发模式 | 环境变量跳过 | 方便调试 |
| 失败处理 | 记录安全警告 | 可追溯 |

#### 2.3.4 输入输出

| 类型 | 内容 |
|------|------|
| 输入 | HTTP 请求（Body + Headers） |
| 输出 | 验证通过/失败 boolean |

---

### 2.4 RulesInitializer (规则初始化器)

#### 2.4.1 职责

初始化 oc-collab 协作框架（生成 AGENTS.md、skills/、docs/00-memos/）。

#### 2.4.2 与现有init的区别

| 命令 | 功能 | 产出 |
|------|------|------|
| `oc-collab init <project>` | 项目信息初始化 | `project_state.yaml` |
| `oc-collab rules init` | 框架规则初始化 | `AGENTS.md`、`skills/`、`docs/00-memos/` |

#### 2.4.3 关键设计决策

| 决策项 | 方案 | 理由 |
|--------|------|------|
| 规则内容 | 完整规则 | AGENTS.md + 全部skill |
| 覆盖策略 | --force 可选覆盖 | 防止误操作 |
| 跳过检测 | 检查 AGENTS.md | 避免重复 |

#### 2.4.4 输入输出

| 类型 | 内容 |
|------|------|
| 输入 | 当前目录（无参数） |
| 输出 | 目录结构 + AGENTS.md |

---

## 3. 技术架构

### 3.1 模块架构

```
src/
├── core/
│   ├── event_dispatcher.py    # EventDispatcher
│   ├── state_notifier.py      # StateNotifier
│   ├── hmac_validator.py      # HMACValidator (新增)
│   └── rules_initializer.py   # RulesInitializer (新增)
│
├── cli/
│   ├── webhook_commands.py   # 增强：新增 webhook notify
│   └── rules_commands.py     # 新增：rules init 命令
│
└── config/
    └── webhook_config.py     # 复用 v2.2.7
```

### 3.2 新增文件清单

| 文件路径 | 功能 | 工时 | 类型 |
|----------|------|------|------|
| `src/core/event_dispatcher.py` | 事件分发器 | 5h | 新增 |
| `src/core/state_notifier.py` | 状态通知器 | 5h | 新增 |
| `src/core/hmac_validator.py` | HMAC签名验证 | 3h | 新增 |
| `src/core/rules_initializer.py` | 规则初始化器 | 3h | 新增 |
| `src/cli/rules_commands.py` | rules init 命令 | 1h | 新增 |
| `src/cli/webhook_commands.py` | 增强 notify 命令 | 1h | 增强 |

### 3.3 内部依赖图

```
EventListener (v2.2.7)
        │
        │ 解析后的事件
        ▼
┌───────────────────────┐
│   EventDispatcher     │  ← 接收事件
│   (F-WEB-003)         │
└───────────┬───────────┘
            │
            │ 分发到回调
            ▼
    ┌───────┴───────┐
    │               │
    ▼               ▼
StateNotifier    其他回调
(F-WEB-004)       (可选)
    │
    │ HTTP POST
    ▼
WebhookConfig ──→ HMACValidator ──→ 验证结果
(F-WEB-001)     (F-WEB-005)
```

---

## 4. 开放问题

| 问题 | 负责人 | 需澄清 |
|------|--------|--------|
| StateNotifier 是否需要支持 Webhook URL 模板？ | Agent2 | 支持 Jinja2 模板？ |
| 是否需要支持 Webhook 重试次数配置？ | Agent2 | 写入配置文件还是命令行参数？ |
| 通知发送是否需要确认 ACK？ | Agent2 | 简化模式还是可靠模式？ |

---

## 5. 验收标准

### 5.1 EventDispatcher (F-WEB-003)

- [ ] 支持注册至少 5 个回调函数
- [ ] 支持按事件类型过滤
- [ ] 回调执行失败时记录错误日志
- [ ] 单元测试覆盖率 ≥80%

### 5.2 StateNotifier (F-WEB-004)

- [ ] 支持至少 5 种状态变更事件
- [ ] Payload 格式兼容 GitHub Webhook 格式
- [ ] 发送失败时记录错误日志
- [ ] 单元测试覆盖率 ≥80%

### 5.3 HMACValidator (F-WEB-005)

- [ ] 支持 GitHub X-Hub-Signature-256 验证
- [ ] 支持 Gitee X-Gitee-Token 验证
- [ ] 签名不匹配时记录安全警告
- [ ] 支持环境变量跳过验证（开发模式）
- [ ] 单元测试覆盖率 ≥80%

### 5.4 RulesInitializer (F-INIT-001)

- [ ] `oc-collab rules init` 命令存在且可执行
- [ ] 生成 `AGENTS.md`（内置默认规则）
- [ ] 生成 `skills/` 目录
- [ ] 生成 `docs/00-memos/` 目录
- [ ] 检测到已有 `AGENTS.md` 时跳过（无 `--force`）
- [ ] `--force` 参数可覆盖已有文件
- [ ] 黑盒测试通过

---

## 6. 工时估算

| 阶段 | 任务 | 工时 |
|------|------|------|
| 概要设计 | OUTLINE_v2.2.8.md | 2h |
| 详细设计 | DETAIL_v2.2.8.md | 3h |
| 开发 | EventDispatcher (F-WEB-003) | 5h |
| 开发 | StateNotifier (F-WEB-004) | 5h |
| 开发 | HMACValidator (F-WEB-005) | 3h |
| 开发 | RulesInitializer (F-INIT-001) | 3h |
| 测试 | 单元测试 + 黑盒测试 | 5h |
| **合计** | | **26h** |

---

## 7. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Webhook URL 配置复杂 | 用户配置困难 | 复用 v2.2.7 的配置机制 |
| 网络不稳定导致发送失败 | 通知丢失 | 添加重试机制（可配置） |
| Payload 格式不兼容 | 接收方无法解析 | 参考 GitHub Webhook 格式 |
| rules init 与现有 init 混淆 | 用户困惑 | 子命令区分（rules init） |

---

## 8. 关联文档

| 文档 | 说明 |
|------|------|
| `docs/01-requirements/requirements_v2.2.8.md` | v2.2.8 需求文档 |
| `docs/02-design/DETAIL-2026-02-v2.2.7.md` | v2.2.7 详细设计（参考） |
| `docs/04-proposals/PROPOSAL-2026-02-001_rules_auto_loading.md` | 规则自动加载提案 |
| `src/core/event_listener.py` | EventListener（v2.2.7） |
| `src/core/webhook_config.py` | WebhookConfig（v2.2.7） |

---

**创建人**: Agent 1
**日期**: 2026-02-13
**状态**: APPROVED

---

**签署**:
- Agent 1 (产品负责人): 创建概要设计 ✅ 2026-02-13
- Agent 2 (技术负责人): 技术评审通过 ✅ 2026-02-13
