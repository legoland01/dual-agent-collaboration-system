# v2.3.3 完整CLI E2E测试用例设计

**版本**: v1  
**创建日期**: 2026-02-20  
**作者**: Agent1 (产品经理)  
**目标**: 覆盖全部有效CLI指令，基于SQLite

---

## 一、CLI指令清单（v2.3.3有效）

### 1.1 核心TODO指令（基于SQLite）

| 指令 | 状态 | 说明 |
|------|------|------|
| `oc-collab todo` | ✅ 有效 | TODO管理命令组 |
| `oc-collab todowrite` | ✅ 有效 | 创建TODO |
| `oc-collab todo list` | ✅ 有效 | 查看TODO列表 |
| `oc-collab todo complete` | ✅ 有效 | 完成TODO |
| `oc-collab todo show` | ✅ 有效 | 查看TODO详情 |
| `oc-collab todo delete` | ✅ 有效 | 删除TODO |
| `oc-collab todo edit` | ✅ 有效 | 编辑TODO |

### 1.2 Agent管理指令

| 指令 | 状态 | 说明 |
|------|------|------|
| `oc-collab switch` | ✅ 有效 | 切换Agent角色 |
| `oc-collab agent` | ✅ 有效 | Agent管理 |

### 1.3 签署与阶段指令

| 指令 | 状态 | 说明 |
|------|------|------|
| `oc-collab signoff` | ✅ 有效 | 签署确认 |
| `oc-collab signoffs` | ✅ 有效 | 查看签署记录 |
| `oc-collab advance` | ✅ 有效 | 推进阶段 |
| `oc-collab status` | ✅ 有效 | 查看状态 |

### 1.4 项目与文档指令

| 指令 | 状态 |说明 |
|------|------|------|
| `oc-collab project` | ✅ 有效 | 项目管理 |
| `oc-collab docs` | ✅ 有效 | 文档管理 |

### 1.5 废弃指令（不测试）

| 指令 | 状态 | 原因 |
|------|------|------|
| `oc-collab state queue` | ❌ 废弃 | state_queue.py已废弃 |
| `oc-collab todo-dep-check` | ❌ 废弃 | 引用废弃YAML |

---

## 二、E2E测试用例设计

### 测试模块1: TODO生命周期

#### TC-TODO-001: 创建TODO

```bash
# 步骤
oc-collab todowrite --content "测试任务1" --to agent2 --priority high

# 验证
oc-collab todo list
# 期望: 包含"测试任务1"

# SQLite验证
sqlite3 state/todos.db "SELECT content, receiver, priority FROM todos WHERE content LIKE '%测试任务1%'"
# 期望: content='测试任务1', receiver='agent2', priority='high'
```

#### TC-TODO-002: 查看TODO列表

```bash
# 步骤
oc-collab todo list

# 验证
# 期望: 返回TODO列表，包含id, content, status, sender, receiver

# SQLite验证
sqlite3 state/todos.db "SELECT COUNT(*) FROM todos"
# 期望: count >= 1
```

#### TC-TODO-003: 完成TODO

```bash
# 步骤
oc-collab todowrite --content "测试完成" --to agent2
TODO_ID=$(oc-collab todo list --json | jq -r '.[0].id')
oc-collab todo complete $TODO_ID

# 验证
sqlite3 state/todos.db "SELECT status FROM todos WHERE id='$TODO_ID'"
# 期望: status='completed'
```

#### TC-TODO-004: 删除TODO

```bash
# 步骤
oc-collab todowrite --content "测试删除" --to agent2
TODO_ID=$(oc-collab todo list --json | jq -r '.[] | select(.content=="测试删除") | .id')
oc-collab todo delete $TODO_ID

# 验证
sqlite3 state/todos.db "SELECT COUNT(*) FROM todos WHERE id='$TODO_ID'"
# 期望: count=0
```

#### TC-TODO-005: TODO状态过滤

```bash
# 步骤
oc-collab todo list --status pending
oc-collab todo list --status completed

# 验证
# 期望: 只返回对应状态的TODO
```

---

### 测试模块2: Agent切换

#### TC-AGENT-001: 切换到Agent1

```bash
# 步骤
oc-collab switch 1

# 验证
cat state/agent.identity
# 期望: 包含 "current_agent: agent1"
```

#### TC-AGENT-002: 切换到Agent2

```bash
# 步骤
oc-collab switch 2

# 验证
cat state/agent.identity
# 期望: 包含 "current_agent: agent2"
```

#### TC-AGENT-003: Agent身份隔离

```bash
# 步骤
oc-collab switch 1
oc-collab todowrite --content "Agent1的任务" --to agent2

oc-collab switch 2
oc-collab todo list

# 验证
# 期望: Agent2看不到Agent1创建的TODO（BUG-20260219-004）
```

---

### 测试模块3: Signoff签署

#### TC-SIGNOFF-001: 签署requirements

```bash
# 步骤
oc-collab signoff requirements

# 验证
ls state/signoffs/
# 期望: 存在签署记录文件

sqlite3 state/todos.db "SELECT status FROM todos WHERE content LIKE '%requirements%' LIMIT 1"
# 期望: 状态已更新
```

#### TC-SIGNOFF-002: 查看签署记录

```bash
# 步骤
oc-collab signoffs

# 期望: 显示签署历史
```

---

### 测试模块4: 阶段推进

#### TC-PHASE-001: 推进阶段

```bash
# 步骤
oc-collab advance

# 验证
cat state/project_state.yaml | grep phase
# 期望: phase已更新
```

---

### 测试模块5: 项目查询（v2.3.3新功能）

#### TC-PROJECT-001: 查询项目状态

```bash
# 步骤
oc-collab project default status --json

# 期望: 返回JSON格式项目状态
```

#### TC-PROJECT-002: 查询项目TODO

```bash
# 步骤
oc-collab project default todos --json

# 期望: 返回JSON格式TODO列表
```

#### TC-PROJECT-003: 查询项目变更

```bash
# 步骤
oc-collab project default changes --since=2026-01-01 --json

# 期望: 返回变更列表
```

---

### 测试模块6: 文档查询（v2.3.3新功能）

#### TC-DOCS-001: 文档查询

```bash
# 步骤
oc-collab docs query "requirements" --json

# 期望: 返回包含关键字的文档
```

#### TC-DOCS-002: 文档列表

```bash
# 步骤
oc-collab docs list --json

# 期望: 返回文档列表
```

#### TC-DOCS-003: 架构查看

```bash
# 步骤
oc-collab docs architecture --json

# 期望: 返回架构信息
```

---

### 测试模块7: Bug追踪

#### TC-BUG-001: 创建Bug

```bash
# 步骤
oc-collab bug create --title "测试Bug" --severity high

# 验证
# 期望: Bug创建成功
```

---

### 测试模块8: 合规检查

#### TC-COMPLIANCE-001: 运行合规检查

```bash
# 步骤
oc-collab compliance check

# 期望: 返回检查结果
```

---

### 测试模块9: 配置管理

#### TC-CONFIG-001: 查看配置

```bash
# 步骤
oc-collab config list

# 期望: 返回配置列表
```

---

### 测试模块10: 集成测试

#### TC-INTEGRATION-001: 完整TODO流程

```bash
# 完整流程
# 1. 创建TODO
oc-collab todowrite --content "集成测试任务" --to agent2 --priority high

# 2. 切换到Agent2
oc-collab switch 2

# 3. 查看TODO
oc-collab todo list

# 4. 完成TODO
TODO_ID=$(oc-collab todo list --json | jq -r '.[] | select(.content=="集成测试任务") | .id')
oc-collab todo complete $TODO_ID

# 5. 签署
oc-collab signoff requirements

# 验证
sqlite3 state/todos.db "SELECT status FROM todos WHERE content LIKE '%集成测试任务%'"
# 期望: status='completed'
```

---

## 三、测试数据隔离验证

### TC-ISOLATION-001: 测试数据库独立

```bash
# 步骤
export OC_TEST_DB=1
oc-collab todowrite --content "测试环境任务" --to agent2

# 验证
ls state/todos_test.db
# 期望: 测试数据库文件存在

# 验证生产数据不受影响
sqlite3 state/todos.db "SELECT COUNT(*) FROM todos WHERE content='测试环境任务'"
# 期望: count=0
```

---

## 四、测试统计

| 测试模块 | 用例数 | 说明 |
|----------|--------|------|
| TODO生命周期 | 5 | CRUD完整流程 |
| Agent切换 | 3 | 身份隔离验证 |
| Signoff签署 | 2 | 签署流程 |
| 阶段推进 | 1 | advance命令 |
| 项目查询 | 3 | v2.3.3新功能 |
| 文档查询 | 3 | v2.3.3新功能 |
| Bug追踪 | 1 | Bug管理 |
| 合规检查 | 1 | compliance命令 |
| 配置管理 | 1 | config命令 |
| 集成测试 | 1 | 完整流程 |
| 数据隔离 | 1 | 测试沙箱 |
| **总计** | **22** | |

---

## 五、执行顺序

1. **基础测试** (TC-TODO-001 ~ TC-TODO-005)
2. **Agent测试** (TC-AGENT-001 ~ TC-AGENT-003)
3. **Signoff测试** (TC-SIGNOFF-001 ~ TC-SIGNOFF-002)
4. **项目查询测试** (TC-PROJECT-001 ~ TC-PROJECT-003)
5. **文档查询测试** (TC-DOCS-001 ~ TC-DOCS-003)
6. **集成测试** (TC-INTEGRATION-001)

---

## 六、验收标准

- [ ] 22个测试用例全部通过
- [ ] 测试数据自动清理
- [ ] 测试环境隔离验证通过
- [ ] 覆盖所有有效CLI指令
- [ ] 不包含任何废弃指令测试
