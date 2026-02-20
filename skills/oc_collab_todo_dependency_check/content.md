# OC-Collab TODO依赖检查

**Skill ID**: oc_collab_todo_dependency_check  
**版本**: 1.0  
**作者**: Agent 1  
**创建日期**: 2026-02-13

---

## 1. 触发条件

当收到新TODO时自动触发，无需手动调用。

```yaml
trigger: todo_received
priority: high
```

**自动触发场景**：
- 收到新的TODO分配
- 被要求评审/确认某个TODO
- 创建新的TODO给其他Agent

---

## 2. SOP四要素

### 2.1 触发条件（When）

**收到新TODO时立即执行**，包括：
- 系统分配的TODO
- Agent创建的TODO（from/to关系）
- 需要确认/评审的TODO

### 2.2 检查步骤（What）

**Step 1: 解析TODO元数据**

从 SQLite 数据库 `state/todos.db` 查询，提取：
- `id`: TODO编号
- `from`: 发起者
- `to`: 接收者
- `status`: 状态
- `requirements_doc`: 关联文档（若有）
- `phase`: 阶段

**Step 2: 检查前置依赖**

| 检查项 | 规则 | 阻塞条件 |
|--------|------|----------|
| from/to关系 | 当前Agent必须是`to` | ❌ 收到非分配给自己的TODO |
| 关联文档状态 | `requirements_doc`必须已APPROVED | ❌ 文档未确认 |
| 前置TODO | 检查是否有`from: 其他Agent`的PENDING TODO | ❌ 前置未完成 |
| 依赖TODO | 检查`description`中提及的关联TODO | ❌ 关联TODO未完成 |

**Step 3: 验证执行资格**

根据检查结果决定：
- ✅ 可执行：所有依赖满足
- ⏸️ 需等待：前置TODO未完成
- ❌ 异常：收到非分配TODO或文档状态异常

### 2.3 执行操作（How）

**场景1: 可执行（依赖满足）**

```yaml
action: proceed
message: "TODO依赖检查通过，可开始执行"
```

**场景2: 需等待（前置未完成）**

```yaml
action: wait
message: "前置TODO未完成，请等待"
next_step: "检查TODO-XXX状态"
```

**场景3: 异常（收到非分配TODO）**

```yaml
action: reject
message: "此TODO非分配给您，请确认"
next_step: "联系TODO发起者"
```

### 2.4 结束条件（Stop）

当满足以下任一条件时：
- ✅ TODO执行完成（status: completed）
- ⏸️ 明确等待原因（记录待办原因）
- ❌ 异常已记录（Bug Report已创建）

---

## 3. 依赖检查规则

### 3.1 from/to 验证

| 场景 | 检查规则 | 动作 |
|------|----------|------|
| TODO.to == 当前Agent | ✅ 通过 | 执行 |
| TODO.to != 当前Agent | ❌ 异常 | 拒收，确认来源 |

### 3.2 文档状态验证

```yaml
if requirements_doc exists:
    doc_status = get_doc_status(requirements_doc)
    if doc_status != "APPROVED":
        wait("文档未确认")
```

**例外**：DRAFT状态的TODO（如需求分析）可执行，无需文档APPROVED。

### 3.3 前置TODO验证

```yaml
# 检查是否有from其他Agent的PENDING TODO
pending_from_others = query_todos(
    from: "!= 当前Agent",
    status: "pending"
)

if pending_from_others:
    wait(f"存在{len(pending_from_others)}个前置TODO未完成")
```

### 3.4 关联TODO验证

```python
# 从description中提取关联TODO编号
related_ids = extract_todo_ids(description)

for tid in related_ids:
    related_status = get_todo_status(tid)
    if related_status != "completed":
        wait(f"关联TODO-{tid}未完成")
```

---

## 4. 使用示例

### 示例1: 收到评审TODO

```yaml
TODO-294:
  from: agent1
  to: agent2
  status: pending
  requirements_doc: docs/01-requirements/requirements_v2.2.8.md
```

**检查流程**：
1. ✅ to == agent2（正确接收者）
2. ✅ requirements_doc.status == APPROVED
3. ✅ 无前置PENDING TODO
4. ✅ **可执行**

### 示例2: 收到设计TODO（但需求未确认）

```yaml
TODO-295:
  from: agent2
  to: agent1
  status: pending
  requirements_doc: docs/01-requirements/requirements_v2.2.8.md
  phase: design
```

**检查流程**：
1. ✅ to == agent1（正确接收者）
2. ⚠️ requirements_doc.status == REVIEW_PENDING
3. ⏸️ **需等待**：需求文档未APPROVED

### 示例3: 收到创建TODO（但自己是发起者）

```yaml
TODO-296:
  from: agent1
  to: agent1
  status: pending
```

**检查流程**：
1. ❌ to == from（同一人）
2. ⚠️ **异常**：自己给自己创建TODO不需要from/to

---

## 5. 输出产物

### 5.1 决策结果

| 输出 | 类型 | 说明 |
|------|------|------|
| `action` | enum | proceed / wait / reject |
| `message` | string | 人类可读的状态描述 |
| `blocking_todos` | list | 阻塞的前置TODO列表 |
| `blocking_reason` | string | 阻塞原因（若wait） |

### 5.2 日志记录

```yaml
log:
  timestamp: ISO8601
  todo_id: "TODO-XXX"
  action: "wait"
  reason: "前置TODO-293未完成"
  blocking_todos:
    - "TODO-293"
```

---

## 6. 常见问题

### Q1: 收到TODO但文档是REVIEW_PENDING？

**答**：检查TODO的phase：
- 若phase == design → 需等待（需求应先APPROVED）
- 若phase == requirements → 可执行（正在评审中）

### Q2: 前置TODO超过24小时未完成？

**答**：
1. 检查TODO状态是否准确
2. 提醒TODO发起者
3. 超过48小时可创建Bug Report

### Q3: 收到TODO但from/to异常？

**答**：
1. 确认TODO来源（系统/Agent1/Agent2）
2. 拒收并要求重新分配
3. 创建Bug Report记录异常

---

## 9. Agent独立编号规则 ⭐ (v2.2.11起生效)

### 9.1 编号格式

| Agent | 编号格式 | 示例 |
|-------|----------|------|
| Agent 1 | TODO-1-XXX | TODO-1-001, TODO-1-002 |
| Agent 2 | TODO-2-XXX | TODO-2-001, TODO-2-002 |

### 9.2 编号规则

| 规则 | 说明 | 违反后果 |
|------|------|----------|
| **Agent1只能创建TODO-1-XXX** | Agent1创建的TODO必须使用TODO-1前缀 | SQLite约束冲突 |
| **Agent2只能创建TODO-2-XXX** | Agent2创建的TODO必须使用TODO-2前缀 | SQLite约束冲突 |
| **禁止手动指定ID** | 编号由todowrite自动生成，禁止手动指定 | 编号冲突 |
| **历史TODO保持兼容** | v2.2.10之前的TODO无需强制迁移 | 兼容旧版本 |

### 9.3 依赖检查增强

```yaml
# 检查TODO编号格式是否正确
def validate_todo_id(todo):
    agent_id = get_current_agent_id()  # 从环境变量读取
    expected_prefix = f"TODO-{agent_id}-"

    if not todo.id.startswith(expected_prefix):
        return {
            "valid": False,
            "reason": f"TODO编号格式错误：预期{expected_prefix}前缀，实际为{todo.id}"
        }

    return {"valid": True}
```

### 9.4 违反场景

| 场景 | 错误做法 | 正确做法 |
|------|----------|----------|
| Agent1创建TODO | 手动指定 TODO-2-001 | 使用todowrite自动生成 TODO-1-001 |
| Agent2创建TODO | 手动指定 TODO-1-003 | 使用todowrite自动生成 TODO-2-003 |
| 跨Agent创建 | Agent1创建TODO给Agent2 | Agent1创建 TODO-1-XXX，Agent2创建自己的 TODO-2-XXX |

---

## 10. 版本历史

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| 1.1 | 2026-02-14 | 新增"Agent独立编号规则"章节 | Agent 1 |
| 1.0 | 2026-02-13 | 初始版本 | Agent 1 |

---

## 11. 关联文档

| 文档 | 说明 |
|------|------|
| `state/todos.db` | TODO数据源 (SQLite) |
| `docs/00-memos/BUG-20260213-005_todo_dependency_check.md` | Bug报告（问题背景） |
| `skills/oc_collab_requirements_guide/content.md` | 需求阶段参考 |
| `skills/oc_collab_requirements_review_guide/content.md` | 评审阶段参考 |
| `docs/01-requirements/requirements_v2.2.11.md` | v2.2.11需求文档 |

---

**维护者**: Agent 1
**更新日期**: 2026-02-14
