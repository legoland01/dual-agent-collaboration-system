# oc-collab 使用指南

**用途**: 各子系统集成oc-collab时的参考手册
**维护**: 随版本更新，查阅 `docs/00-architecture/CORE_ARCHITECTURE.md` 了解架构

---

## 快速索引

| 场景 | 使用的命令 |
|------|-----------|
| 创建任务 | `oc-collab todowrite` |
| 查看任务列表 | `oc-collab todo list` |
| 启动Agent监听 | `oc-collab agent listen` |
| 同步代码 | `oc-collab push` / `oc-collab sync` |
| 查看项目状态 | `oc-collab status` |

---

## 常用命令

### 任务管理

```bash
# 创建任务
oc-collab todowrite --content "实现登录功能" --to agent2 --priority high --source REQUIREMENT

# 查看任务列表
oc-collab todo list
oc-collab todo list --status pending
oc-collab todo list --unread

# 查看任务详情
oc-collab todo show TODO-1to2-001

# 完成任务
oc-collab todo complete TODO-1to2-001

# 确认交付
oc-collab todo ack TODO-1to2-001

# 统计
oc-collab todo stats
```

### Agent管理

```bash
# 列出所有Agent
oc-collab agent list

# 注册Agent
oc-collab agent register --id agent3 --role FE

# 启动监听（接收任务通知）
oc-collab agent listen --daemon

# 查看监听状态
oc-collab agent listen --status
```

### Git同步

```bash
# 推送
oc-collab push

# 拉取
oc-collab sync

# 查看状态
oc-collab status
```

### 项目管理（跨项目）

```bash
# 列出所有项目（内部子系统权限）
oc-collab project list

# 查看某项目状态
oc-collab project <项目名> status

# 查看某项目TODO
oc-collab project <项目名> todos
```

### 签署与合规

```bash
# 签署里程碑
oc-collab signoff requirement
oc-collab signoff design

# 查看签署历史
oc-collab signoffs
```

### 文档操作

```bash
# 需求管理
oc-collab requirements

# 设计文档
oc-collab design

# 评审
oc-collab review
```

---

## 任务编号规则

```
TODO-{发送者}to{接收者}-{序号}
示例：
  TODO-1to2-001   → Agent1发给Agent2的第1个任务
  TODO-3to2-001   → PM-Agent(编号3)发给Agent2的任务
```

**可用接收者**: agent1, agent2, agent3, ... (通过 `oc-collab agent list` 查看)

---

## 数据存储位置

| 数据 | 路径 |
|------|------|
| 任务 | `state/todos.db` (SQLite) |
| Agent状态 | `state/agent_status.db` (SQLite) |
| 签署记录 | `state/signoffs.yaml` |
| 配置 | `config/*.yaml` |
| 需求文档 | `docs/01-requirements/` |
| 设计文档 | `docs/02-design/` |

---

**查阅**: 完整CLI帮助 `oc-collab --help` 或 `oc-collab <command> --help`
