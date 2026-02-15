# BUG-2026-02-010: StateReceiver 模块已实现但 CLI 命令缺失

## 基本信息

| 属性 | 值 |
|------|-----|
| Bug ID | BUG-2026-02-010 |
| 严重程度 | P1 |
| 状态 | DRAFT |
| 发现时间 | 2026-02-15 |
| 发现者 | Agent2 |

---

## 问题描述

v2.2.12 版本发布了 StateReceiver 功能，但安装后 `oc-collab state start` 命令不存在，导致用户无法通过 CLI 启动 StateReceiver 服务来接收 TODO 通知。

## 复现步骤

1. 执行 `pip install --upgrade opencode-collaboration` 升级到 v2.2.12
2. 执行 `oc-collab --help` 查看可用命令
3. 执行 `oc-collab state start` 尝试启动 StateReceiver
4. **预期结果**：显示 StateReceiver 服务启动选项
5. **实际结果**：`Error: No such command 'state'`

## 调查结论

### 1. 模块实现情况

| 组件 | 路径 | 状态 | 说明 |
|------|------|------|------|
| StateReceiver 核心类 | `src/core/state_receiver.py` | ✅ 已实现 | 提供 HTTP webhook 接收器 |
| StateQueueManager | `src/core/state_queue.py` | ✅ 已实现 | 队列管理 |
| CLI 命令 | `src/cli/state_commands.py` | ❌ 未创建 | 无对应 CLI 命令 |
| 命令注册 | `src/cli/main.py` | ❌ 未注册 | state 子命令未加入 |

### 2. 证据

**已安装包缺少 state_commands.py：**
```
$ ls src/cli/
__init__.py              deploy_commands.py       enhanced_commands.py     main.py                  rules_commands.py         skill_commands.py         todo_commands.py
agent.py                 deploy_full_commands.py  main.py.bak               skill_check_commands.py   startup_commands.py        webhook_commands.py
```

**可用的 CLI 命令（无 state）：**
```
Commands:
  .a             显示当前关联的项目信息。
  advance        推进到下一阶段
  agent          Agent 守护进程
  auto           自动执行当前任务。
  compliance     合规检查命令组
  deploy         部署相关命令
  design         设计文档管理
  docs           自动同步文档。
  git            Git 同步工具
  history        查看协作历史。
  init           初始化协作项目。
  owner          文件Owner管理命令组
  project        项目管理命令
  push           推送代码
  remote         管理远程仓库
  requirements   需求文档管理
  review         管理评审流程。
  rules          规则管理命令
  signoff        签署确认。
  signoffs       查看签署记录。
  skill          Skill管理命令
  skill-check    Skill管理命令组
  startup-check  执行Agent启动自检
  status         查看当前协作状态。
  switch         切换Agent角色。
  sync           同步远程变更
  sync-all       同步到所有远程平台
  todo           TODO管理命令组
  todoedit       编辑待办任务。
  todowrite      创建待办任务。
  webhook        Webhook管理命令
  work           智能工作流引导。
  workflow       查看当前工作流状态和推理。
```

### 3. 根因分析

v2.2.12 开发周期中，StateReceiver 模块 (`src/core/state_receiver.py`) 已在开发分支实现，但：
1. **需求文档** `docs/01-requirements/requirements_v2.2.12.md` 中未包含 StateReceiver CLI 命令需求
2. **详细设计** `docs/02-design/DETAIL_v2.2.12.md` 聚焦于部署自动化，未覆盖 StateReceiver CLI
3. **CLI 实现** `src/cli/` 目录缺少 `state_commands.py` 文件
4. **命令注册** `src/cli/main.py` 中未导入和注册 state 子命令

### 4. 相关文档

| 文档 | 说明 |
|------|------|
| `docs/01-requirements/requirements_v2.2.12.md` | v2.2.12 需求文档（部署自动化） |
| `docs/02-design/DETAIL_v2.2.12.md` | v2.2.12 详细设计（部署CLI） |
| `docs/01-requirements/requirements_v2.2.11.md` | v2.2.11 需求文档（StateReceiver定义） |
| `docs/02-design/DETAIL_v2.2.11.md` | v2.2.11 详细设计（StateReceiver设计） |
| `docs/04-proposals/PROPOSAL-2026-02-009_state_receiver_integration.md` | StateReceiver 与 CLI 队列集成改进提案 |

### 5. StateReceiver 模块能力

根据 `src/core/state_receiver.py`，StateReceiver 具备：
- HTTP webhook 端点：`POST /webhook/state`
- HMAC 签名验证
- 队列管理集成
- 健康检查端点：`GET /webhook/state/health`
- 队列状态查询：`GET /webhook/state/queue`

---

## 影响范围

| 影响项 | 描述 |
|--------|------|
| 功能可用性 | StateReceiver 功能对用户不可用 |
| 用户体验 | 无法通过 CLI 启动服务 |
| v2.2.11 需求完整性 | v2.2.11 的 F-NOTIF-001 StateNotifier Receiver 功能不完整 |

---

## 建议修复方案

### 方案 A：创建 state_commands.py（推荐）

1. 创建 `src/cli/state_commands.py`
2. 实现 `state start`、`state stop`、`state status` 命令
3. 在 `src/cli/main.py` 中注册 state 子命令

### 方案 B：扩展 webhook 命令

在现有 `webhook` 命令组下添加 state 相关子命令。

---

## 状态历史

| 时间 | 状态 | 操作者 | 说明 |
|------|------|--------|------|
| 2026-02-15 | DRAFT | Agent2 | 发现并记录 Bug |
| - | - | - | 待修复 |

---

## 修复方案

### 实现内容

创建 `src/cli/state_commands.py`，实现以下 CLI 命令：

| 命令 | 功能 |
|------|------|
| `oc-collab state init` | 初始化 StateReceiver 队列 |
| `oc-collab state start` | 启动 StateReceiver 服务 |
| `oc-collab state stop` | 停止 StateReceiver 服务 |
| `oc-collab state status` | 查看服务状态 |
| `oc-collab state queue` | 查看通知队列 |
| `oc-collab state mark-read <id>` | 标记通知为已读 |

### 修改文件

1. **新增** `src/cli/state_commands.py`
2. **修改** `src/cli/main.py` - 添加导入和命令注册

### 测试结果

```bash
$ oc-collab state --help
Commands:
  init       初始化StateReceiver配置。
  mark-read  标记通知为已读。
  queue      查看通知队列。
  start      启动StateReceiver服务。
  status     显示StateReceiver状态
  stop       停止StateReceiver服务。

$ oc-collab state status
          StateReceiver 状态
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 配置项     ┃ 状态                   ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 服务进程   │ ❌ 未运行              │
│ 待处理通知 │ 1                      │
│ 已完成通知 │ 0                      │
│ 队列文件   │ state/state_queue.json │
└────────────┴────────────────────────┘
```

### 部署状态

- [x] 代码实现完成
- [x] CLI 命令注册完成
- [x] 本地测试通过
- [ ] 部署到 PyPI（待执行）

---

## 签署

| 角色 | 签署 | 时间 |
|------|------|------|
| Agent1 | - | - |
| Agent2 | 技术修复完成 | 2026-02-15 |
