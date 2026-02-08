# Bug 报告：TODO任务不同步问题

**Bug ID**: BUG-20260208-002
**严重程度**: P0 - 阻塞
**状态**: 已修复 ✅
**发现人**: Agent 1
**发现日期**: 2026-02-08
**修复人**: Agent 2
**修复日期**: 2026-02-08
**修复版本**: v2.2.3.1

---

## Bug描述

### 表现形式

| 场景 | 问题 |
|------|------|
| Agent1创建TODO | `todowrite` 返回任务ID，命令执行成功 |
| Agent2查看 | `cat state/agent_adhoc_todos.yaml` 没有新任务 |
| 跨会话 | TODO丢失，Agent2无法看到 |

### 重现场景

```bash
# Agent1 创建TODO
$ todowrite --content "评审 v2.2.4 需求分析报告" --priority P0 --agent 2
✅ 待办已创建: [TODO-060] 评审 v2.2.4 需求分析报告
✓ 已同步到 state/agent_adhoc_todos.yaml

# Agent2 检查（不同步）
$ cat state/agent_adhoc_todos.yaml
# 没有 TODO-060！
```

### 影响范围

| 影响 | 严重程度 |
|------|----------|
| Agent2看不到任务 | P0 - 阻塞协作 |
| TODO追踪失效 | P0 - 流程中断 |
| Compaction前TODO丢失 | P0 - 历史断裂 |

---

## 问题分析

### 根因分析

| 问题 | 原因 | 层级 |
|------|------|------|
| todowrite 写入错误文件 | `TodoSyncManager.TODO_FILENAME = "state/todo.yaml"` | 代码 |
| 目标文件应该是 | `state/agent_adhoc_todos.yaml` | 流程 |

### 相关文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `state/agent_adhoc_todos.yaml` | 任务追踪（Agent共享） | ✅ 已修复 |
| `src/core/todo_sync_manager.py` | 待办同步管理 | ✅ 已修复 |

---

## 修复方案

### 已实施：方案B - 修复 todowrite 命令

```
修复内容：
1. TodoSyncManager.TODO_FILENAME = "state/agent_adhoc_todos.yaml"
2. 格式改为 adhoc_todos/total 格式（兼容 agent_adhoc_todos.yaml）
```

### 修复前

```bash
$ todowrite --content "测试" --priority high
✅ 待办已创建: [TODO-001] 测试
✓ 已同步到 state/todo.yaml  # ❌ 错误文件！
```

### 修复后

```bash
$ oc-collab todowrite --content "测试" --priority high
✅ 待办已创建: [TODO-001] 测试
✓ 已同步到 state/agent_adhoc_todos.yaml  # ✅ 正确文件！
```

---

## 验收确认

### 测试验收

| 测试项 | 结果 |
|--------|------|
| 单元测试 | ✅ 42 passed |
| E2E测试 | ✅ 6 passed |
| TODO同步验证 | ✅ 正确写入 agent_adhoc_todos.yaml |

### Agent 1 签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-08 | ✅ 验收通过 |

### 签署内容

```
验收结果: ✅ 通过

验证项:
- ✅ 单元测试: 42 passed
- ✅ E2E测试: 6 passed  
- ✅ TODO同步: 正确写入 agent_adhoc_todos.yaml

签署: Agent 1 @ 2026-02-08
```

---

## 时间线

| 日期 | 事件 |
|------|------|
| 2026-02-08 | Agent 1 发现问题，创建 Bug 报告 |
| 2026-02-08 | Agent 2 调查并修复 |
| 2026-02-08 | 合并到主分支 (commit: d4378d0) |
| 2026-02-08 | Agent 1 测试验收通过 ✅ |
| 2026-02-08 | Agent 1 签署确认 ✅ |

---

## 经验总结

### 教训

| 教训 | 说明 |
|------|------|
| 新功能应复用现有机制 | v2.2.3 的 `TodoSyncManager` 创建了新文件而非复用 `agent_adhoc_todos.yaml` |
| 统一存储位置 | 两个 TODO 文件造成混乱，应统一使用 `agent_adhoc_todos.yaml` |

### 防止措施

| 措施 | 说明 |
|------|------|
| Skill 已更新 | `oc_collab_development_guide` 添加 TODO 管理规范 |

---

## Patch 发布 ⚠️

### 发布前检查清单

```
修复 → 合并 → 验收 ✅ → 发布
                  ↑
            必须按此顺序！
```

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 验收通过 | ✅ | Agent 1 已签署确认 |
| 版本号升级 | ⏳ | 待 Agent 2 执行 |
| 包构建 | ⏳ | 待 Agent 2 执行 |
| PyPI 上传 | ⏳ | 待 Agent 2 执行 |
| Git 推送 | ⏳ | 待 Agent 2 执行 |
| 验证发布 | ⏳ | 待 Agent 2 执行 |

### Patch 信息

| 字段 | 内容 |
|------|------|
| 版本号 | v2.2.3.1 |
| 严重程度 | P0 |
| 发布状态 | 待发布 |

### 发布步骤（Agent 2 执行）

```bash
# 1. 升级版本号
# 编辑 pyproject.toml: version = "2.2.3.1"

# 2. 构建包
python3 -m build

# 3. PyPI 上传
twine upload dist/*

# 4. Git 推送
git add pyproject.toml
git commit -m "chore: BUG-20260208-002 Patch v2.2.3.1"
git push

# 5. 验证发布
curl https://pypi.org/pypi/opencode-collaboration/2.2.3.1/json
```

---

## 关联文档

| 文档 | 说明 |
|------|------|
| `skills/oc_collab_bug_management_guide/` | Bug 管理流程 |
| `skills/oc_collab_development_guide/` | 开发规范（已更新） |
| `src/core/todo_sync_manager.py` | 已修复 |

---

**状态**: 待发布 ⏳
**当前阶段**: Patch 发布
**修复版本**: v2.2.3.1
**Git Commit**: d4378d0

### 等待 Agent 2 执行发布

```
修复 ✅ → 合并 ✅ → 验收 ✅ → 发布 ⏳
```

**下一步**: Agent 2 按上方发布步骤执行 Patch 发布。
