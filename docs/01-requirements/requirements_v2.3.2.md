# 需求文档：oc-collab v2.3.2

**版本**: v1 (DRAFT)  
**创建日期**: 2026-02-17  
**作者**: Agent 1 (产品经理)  
**目标**: TODO存储 + 监听 + 实时通知

---

## 1. 背景

### 1.1 Roadmap规划

根据`ROADMAP_oc-collab.md`，v2.3.2的目标是：
- SQLite存储 - 将TODO从YAML迁移到SQLite
- 监听进程 - agent listen自动启动
- 实时通知 - Question窗口显示通知（已通过POC验证）

### 1.2 POC研究成果

Consultant已完成POC验证（见`docs/00-memos/POC_OpenCode_TUI_Notification_Verification.md`）：

| 方案 | 状态 |
|------|------|
| **Question Tool + Instruction** | ✅ 验证成功 |

---

## 2. 需求概述

### 2.1 版本目标

v2.3.2的核心目标：
1. **SQLite存储** - TODO数据从YAML迁移到SQLite
2. **监听进程** - agent listen自动启动
3. **实时通知** - Question窗口交互

### 2.2 功能范围

| 功能ID | 功能名称 | 优先级 |
|--------|----------|--------|
| F-STORE-001 | SQLite存储 | P0 |
| F-STORE-002 | 数据迁移 | P1 |
| F-LISTEN-001 | 监听进程 | P0 |
| F-LISTEN-002 | 状态感知 | P1 |
| F-LISTEN-003 | 上线拉取 | P1 |
| F-NOTIF-001 | 实时通知 | P0 |
| F-NOTIF-002 | 交互操作 | P0 |
| F-CONFIG-001 | 配置管理 | P1 |

---

## 3. 功能需求

### 3.1 F-STORE-001: SQLite存储

**需求描述**：
将TODO数据从YAML文件迁移到SQLite数据库。

**详细说明**：
1. 使用SQLite作为持久化存储
2. 创建TODO表：id, content, status, priority, sender, receiver, created_at, updated_at
3. 支持CRUD操作
4. 兼容旧版YAML读取

**数据Schema**：
```sql
CREATE TABLE todos (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    sender TEXT,
    receiver TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE INDEX idx_todos_receiver ON todos(receiver);
CREATE INDEX idx_todos_status ON todos(status);
```

**验收标准**：
- [ ] 使用SQLite存储TODO数据
- [ ] CRUD操作正常工作
- [ ] 与现有CLI命令兼容

### 3.2 F-STORE-002: 数据迁移

**需求描述**：
提供YAML到SQLite的迁移脚本。

**详细说明**：
1. 读取现有`state/agent_adhoc_todos.yaml`
2. 转换为SQLite记录
3. 备份原文件
4. 迁移完成后删除原YAML

**验收标准**：
- [ ] 自动迁移现有TODO数据
- [ ] 保留原有TODO ID
- [ ] 迁移失败可回滚

### 3.3 F-LISTEN-001: 监听进程

**需求描述**：
agent listen命令自动启动后台监听。

**详细说明**：
1. 支持守护进程模式启动
2. 自动检测新TODO
3. 支持配置检测间隔
4. 支持开机自启

**CLI命令**：
```bash
# 启动监听（守护进程）
oc-collab agent listen --daemon

# 停止监听
oc-collab agent listen --stop

# 查看监听状态
oc-collab agent listen --status
```

**验收标准**：
- [ ] --daemon模式后台运行
- [ ] 自动检测新TODO
- [ ] 可停止监听

### 3.4 F-LISTEN-002: 状态感知

**需求描述**：
实时感知Agent在线/离线状态。

**详细说明**：
1. 监听Git/Webhook事件
2. 检测Agent上线/下线
3. 记录最后在线时间

**验收标准**：
- [ ] 检测Agent上线事件
- [ ] 检测Agent下线事件
- [ ] 记录状态历史

### 3.5 F-LISTEN-003: 上线拉取

**需求描述**：
Agent上线后自动拉取积压的TODO。

**详细说明**：
1. Agent重新连接时
2. 自动检测未处理的TODO
3. 优先处理积压任务

**验收标准**：
- [ ] 上线时自动拉取TODO
- [ ] 按时间顺序处理
- [ ] 通知用户有待办

### 3.6 F-NOTIF-001: 实时通知

**需求描述**：
通过OpenCode Question窗口显示TODO通知。

**详细说明**：
1. Instruction文件生成
2. LLM自动调用question tool
3. 用户在Question窗口选择操作

**参考**: POC_OpenCode_TUI_Notification_Verification.md

**验收标准**：
- [ ] 生成TODO_NOTIFY.md instruction
- [ ] LLM能识别新TODO
- [ ] 弹出question窗口

### 3.7 F-NOTIF-002: 交互操作

**需求描述**：
用户在Question窗口直接操作TODO。

**用户操作选项**：
| 操作 | 说明 |
|------|------|
| 立即执行 | 标记TODO为进行中 |
| 留待空闲 | 移入留待队列 |
| 不用执行 | 标记为无需执行 |
| 查看详情 | 显示完整内容 |

**验收标准**：
- [ ] question窗口显示TODO
- [ ] 支持4种操作
- [ ] 操作后更新状态

### 3.8 F-CONFIG-001: 配置管理

**需求描述**：
管理OpenCode连接配置。

**详细说明**：
1. 配置OpenCode服务器地址
2. 配置Webhook URL
3. 配置通知规则

**CLI命令**：
```bash
# 设置配置
oc-collab config set opencode.url http://localhost:11411
oc-collab config set webhook.url https://example.com/hook

# 查看配置
oc-collab config list
```

**验收标准**：
- [ ] 可配置OpenCode URL
- [ ] 可配置Webhook
- [ ] 配置持久化

---

## 4. CLI 命令清单

### 新增命令

| 命令 | 说明 | 工时 |
|------|------|------|
| `oc-collab agent listen --daemon` | 守护进程模式启动监听 | 1h |
| `oc-collab agent listen --stop` | 停止监听 | 0.5h |
| `oc-collab agent listen --status` | 查看监听状态 | 0.5h |
| `oc-collab config set` | 设置配置 | 1h |
| `oc-collab config list` | 查看配置 | 0.5h |
| `oc-collab notify enable` | 启用通知 | 1h |
| `oc-collab notify disable` | 禁用通知 | 0.5h |
| `oc-collab notify status` | 查看通知状态 | 0.5h |

### 变更命令

| 命令 | 变更说明 |
|------|----------|
| `oc-collab todo` | 底层存储从YAML改为SQLite |

---

## 5. 工时预估

| 模块 | 功能 | 工时 |
|------|------|------|
| M1 | SQLite存储层 | 4h |
| M2 | 数据迁移 | 2h |
| M3 | 监听进程 | 3h |
| M4 | 状态感知 | 2h |
| M5 | 上线拉取 | 2h |
| M6 | 实时通知 | 3h |
| M7 | 交互操作 | 3h |
| M8 | 配置管理 | 2h |
| - | 测试与调试 | 3h |
| - | 文档 | 1h |
| **总计** | | **21h** |

---

## 6. 依赖关系

### 6.1 外部依赖

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.8+ | 运行环境 |
| SQLite | 3.x | 内置数据库 |
| OpenCode | 最新版 | Question Tool |

### 6.2 内部依赖

| 功能 | 依赖 |
|------|------|
| F-LISTEN-001 | F-STORE-001 |
| F-NOTIF-001 | POC成果 |
| F-NOTIF-002 | F-NOTIF-001 |

---

## 7. 验收标准汇总

| 功能ID | 验收标准数 |
|--------|-----------|
| F-STORE-001 | 3 |
| F-STORE-002 | 3 |
| F-LISTEN-001 | 3 |
| F-LISTEN-002 | 3 |
| F-LISTEN-003 | 3 |
| F-NOTIF-001 | 3 |
| F-NOTIF-002 | 3 |
| F-CONFIG-001 | 3 |
| **总计** | **24** |

---

## 评审记录

| 日期 | 评审人 | 评审结果 | 意见 |
|------|--------|----------|------|
| 2026-02-17 | Agent 2 | 技术评审通过 | 备份策略已完善 |

## 签署

| 角色 | 签署内容 | 日期 |
|------|----------|------|
| Agent 1 (产品经理) | 创建需求 | 2026-02-17 |
| Agent 2 (开发) | 技术评审通过 | 2026-02-17 |

---

**状态**: APPROVED  
**待评审**: -

