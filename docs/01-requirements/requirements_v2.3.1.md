# 需求规格说明书：oc-collab v2.3.1

**版本**: v1  
**创建日期**: 2026-02-16  
**作者**: Agent 1 (产品经理)  
**版本号**: 2.3.1  
**状态**: DRAFT

---

## 零、核心架构参考 ⭐

| 功能ID | 功能名称 | 架构模块 | 映射路径 | 优先级 |
|--------|----------|----------|----------|--------|
| F-TODO-001 | TODO编号优化 | CLI命令层 | 核心架构 → TODO管理 | P0 |
| F-TODO-002 | 向后兼容 | CLI命令层 | 核心架构 → TODO管理 | P0 |
| F-TODO-003 | 来源标签 | CLI命令层 | 核心架构 → TODO管理 | P0 |
| F-TODO-004 | 模板系统 | CLI命令层 | 核心架构 → TODO管理 | P1 |
| F-COMM-001 | 自动Git同步 | 通信层 | 核心架构 → Git同步 | P0 |
| F-COMM-002 | Agent注册表 | 状态管理层 | 核心架构 → 状态管理 | P0 |
| F-COMM-003 | ACK确认 | 通信层 | 核心架构 → Git同步 | P1 |
| F-COMP-001 | 合规规则更新 | 合规层 | 核心架构 → 合规检查 | P0 |

---

### 2.8 F-COMP-001: 合规规则更新

**来源**: 需求设计

**描述**: 合规模块需要适配新的TODO编号格式

**合规检查规则**:
- Agent1创建TODO → 必须分配给Agent2（不能创建TODO-2to3-xxx）
- Agent2创建TODO → 可分配给自己或Agent1
- 编号格式: 识别新格式 TODO-XtoY-xxx 和旧格式 TODO-X-xxx

**违规处理**:
- 检查失败 → 阻止创建并返回错误信息
- 警告场景 → 记录日志但允许继续

**验收标准**:
- [ ] 合规检查支持新编号格式 TODO-XtoY-xxx
- [ ] 合规检查同时支持旧格式 TODO-X-xxx (向后兼容)
- [ ] 合规规则能正确识别创建者和接收者
- [ ] Agent1尝试创建非法的TODO时阻止并提示

**工时**: 1h

---

## 1. 概述

### 1.1 版本信息

| 项目 | 值 |
|------|-----|
| 前置版本 | v2.3.0 |
| 变更类型 | 功能增强 |

### 1.2 核心原则

| 原则 | 说明 |
|------|------|
| 范围控制 | 本版本聚焦7个功能，总工时 ≤ 23h |
| CLI边界 | 只做CLI能做的事情 |
| 向后兼容 | 旧格式TODO继续可用 |

### 1.3 目标

支持多Agent团队（内部Agent + PM Agent团队）之间互相发任务，彻底解决TODO编号歧义问题。

---

## 2. 功能需求

### 2.1 F-TODO-001: TODO编号优化

**来源**: PROPOSAL-2026-02-021

**描述**: 支持多Agent编号格式，解决创建者/接收者歧义

**CLI参数**:
- `--to <agent_id>` 或 `--receiver <agent_id>`: 指定接收者
- 优先级: CLI参数 > 环境变量 > Agent注册表

**验收标准**:
- [ ] Agent1创建TODO生成格式 TODO-1to2-xxx
- [ ] Agent2创建TODO生成格式 TODO-2to1-xxx
- [ ] 支持多Agent: TODO-1to3-xxx, TODO-2to3-xxx
- [ ] 编号按接收者独立自增
- [ ] 现有TODO不受影响（无需迁移）
- [ ] 未知接收者降级为TODO-1toX-xxx（X为接收者ID）

**异常场景处理**:
- 接收者不存在: 警告但允许创建
- 接收者未注册: 降级处理，继续允许创建
- 接收者离线: 通过Agent注册表的status字段判断，离线则TODO状态保持pending

**工时**: 4h

---

### 2.2 F-TODO-002: 向后兼容

**来源**: 需求设计

**描述**: 旧格式TODO继续可用

**验收标准**:
- [ ] 旧格式 TODO-1-xxx 自动视为 TODO-1to1-xxx
- [ ] CLI输出同时支持显示两种格式
- [ ] 支持命令: `oc-collab todo list` 和 `oc-collab todo show`
- [ ] 边界测试: TODO-12-001 和 TODO-1to2-001 不混淆
- [ ] 非法格式 TODO-abc-123 拒绝创建

**工时**: 2h

---

### 2.3 F-TODO-003: 来源标签

**来源**: PROPOSAL-2026-02-021

**描述**: 区分TODO从哪里来

**CLI参数**:
- `--source <type>` 或 `-s <type>`: 指定来源

**新增命令**:
- `oc-collab todo show <todo_id>`: 查看TODO详情（含来源信息）

**验收标准**:
- [ ] 支持 source 字段: REQUIREMENT/BUG/FEEDBACK/MANUAL
- [ ] CLI支持按来源筛选: `oc-collab todo --source BUG`
- [ ] `oc-collab todo show` 显示来源信息
- [ ] 支持 -s 简写
- [ ] 不指定时默认 MANUAL

**工时**: 3h

---

### 2.4 F-TODO-004: 模板系统

**来源**: PROPOSAL-2026-02-021

**描述**: TODO内容模板标准化

**配置文件**: `config/templates.yaml`

**CLI参数**:
- `--type <template_type>`: 选择模板类型

**验收标准**:
- [ ] 内置需求任务模板和BUG修复模板
- [ ] 模板数据存储在 config/templates.yaml
- [ ] 支持用户自定义模板（扩展templates.yaml）
- [ ] CLI支持模板选择: `oc-collab todowrite --type BUG_FIX`
- [ ] 模板自动填充必要字段（从上下文推断）

**工时**: 4h

---

### 2.5 F-COMM-001: 自动Git同步

**来源**: Roadmap规划

**描述**: 所有文档操作自动sync到所有远程仓库

**配置文件**: `config/git_sync.yaml`

**触发机制**: 
- 文件监控 (watch): 检测到state文件变更后自动触发
- 或手动触发: `oc-collab sync`

**验收标准**:
- [ ] TODO创建/变更自动触发git add + commit
- [ ] 配置文件 `config/git_sync.yaml` 定义remotes列表
- [ ] 同步失败时提示错误，但不阻塞主流程
- [ ] 支持配置开关，默认关闭

**失败处理**:
- 单个仓库失败: 继续推送其他仓库
- 全部失败: 记录日志，提示用户手动处理

**工时**: 4h

---

### 2.6 F-COMM-002: Agent注册表

**来源**: PROPOSAL-2026-02-017, PROPOSAL-2026-02-021

**描述**: 在project_state.yaml中注册Agent信息

**CLI参数**:
- `oc-collab agent register --id <agent_id> --role <role> --team <team>`
- `oc-collab agent auto-register`: 从环境变量/Git config自动注册

**优先级**: CLI参数 > 环境变量 OC_AGENT_ID > Git config

**Role可选值**: PRODUCT_MANAGER, DEVELOPMENT_LEAD, FRONTEND_DEV, BACKEND_DEV, QA_ENGINEER

**验收标准**:
- [ ] 支持环境变量注册: export OC_AGENT_ID=agent3
- [ ] 支持自动注册: `oc-collab agent auto-register`（从环境变量/git config获取信息）
- [ ] 注册信息包含: id, role, team, status, git_name
- [ ] 支持查询Agent列表: `oc-collab agent list`

**数据结构**:
```yaml
agents:
  agent1:
    id: agent1
    role: DEVELOPMENT_LEAD
    team: internal
    status: active
    git_name: "zhangsan"
```

**并发处理**:
- 重复注册: 更新而非拒绝
- 已分配TODO的Agent注销: 禁止注销

**工时**: 3h

---

### 2.7 F-COMM-003: ACK确认

**来源**: PROPOSAL-2026-02-017

**描述**: commit message确认收到TODO

**ACK触发时机**:
- 接收者执行 `oc-collab todo show <todo_id>` 时自动ACK
- 或执行 `oc-collab todo ack <todo_id>` 手动ACK

**Commit标记格式**: `[ACK] TODO-1to2-001 acknowledged by agent2`

**验收标准**:
- [ ] Agent查看TODO详情时，自动发送commit包含ACK标记
- [ ] TODO状态自动更新为acknowledged
- [ ] 创建者可通过 `oc-collab todo show` 查看ACK状态
- [ ] CLI支持: `oc-collab todo --ack 查看`

**ACK流程**:
- 触发方式: 自动（接收者读取TODO时）+ 手动
- 超时处理: 可选配置超时时间
- 创建者可见: 通过TODO详情查看

**工时**: 3h

---

## 3. CLI 命令清单

### 3.1 新增命令

| 命令 | 功能 | 优先级 |
|------|------|--------|
| oc-collab todowrite --to | 指定接收者 | P0 |
| oc-collab todowrite --type | 选择模板类型 | P1 |
| oc-collab todowrite --source | 指定来源标签 | P0 |
| oc-collab todo --source | 按来源筛选 | P0 |
| oc-collab todo show | 查看TODO详情（含来源、ACK状态） | P0 |
| oc-collab todo ack | 手动确认TODO | P1 |
| oc-collab agent register | 注册Agent | P0 |
| oc-collab agent list | 列出Agent | P0 |
| oc-collab agent auto-register | 自动注册 | P0 |

### 3.2 变更命令

| 命令 | 变更内容 |
|------|----------|
| oc-collab todowrite | 输出新格式TODO-ID，支持--to参数 |
| oc-collab todo list | 支持新编号格式显示，支持--source筛选 |
| oc-collab todo | 新增--ack选项 |

---

## 4. 工时预估

| 功能ID | 功能名称 | 工时 | 优先级 |
|--------|----------|------|--------|
| F-TODO-001 | TODO编号优化 | 4h | P0 |
| F-TODO-002 | 向后兼容 | 2h | P0 |
| F-TODO-003 | 来源标签 | 3h | P0 |
| F-TODO-004 | 模板系统 | 4h | P1 |
| F-COMM-001 | 自动Git同步 | 4h | P0 |
| F-COMM-002 | Agent注册表 | 3h | P0 |
| F-COMM-003 | ACK确认 | 3h | P1 |
| F-COMP-001 | 合规规则更新 | 1h | P0 |
| **总计** | | **24h** | |

---

## 5. 依赖关系

| 功能ID | 前置依赖 | 说明 |
|--------|----------|------|
| F-TODO-001 | 无 | 核心功能 |
| F-TODO-002 | F-TODO-001 | 基于新格式兼容 |
| F-TODO-003 | 无 | 独立功能 |
| F-TODO-004 | 无 | 独立功能 |
| F-COMM-001 | 无 | 独立功能 |
| F-COMM-002 | 无 | 基础设施 |
| F-COMM-003 | F-COMM-002 | 依赖Agent注册表 |

---

## 6. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 编号格式变化大 | 旧任务可能出现歧义 | 向后兼容逻辑 |
| 自动Git同步过于频繁 | 频繁commit | 可配置开关 |
| 多Agent注册冲突 | 同时注册同一ID | 乐观锁处理 |

---

## 7. 签署确认

### Agent 1 签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-16 | ✅ 创建 |

### Agent 2 签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | |

---

**状态**: DRAFT → READY (Agent1创建) → APPROVED (Agent2评审通过)
