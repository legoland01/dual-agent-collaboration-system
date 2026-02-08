# OC-Collab 协作指南 (v2.2.2)

## Agent 角色定义

### Agent 1: 产品经理 + 测试 + 部署
- 负责编写需求说明和概要设计
- 负责评审详细设计
- 负责编写黑盒测试用例
- 负责执行黑盒测试
- 负责部署和发布

### Agent 2: 开发
- 负责创建概要设计的详细设计
- 负责评审概要设计
- 负责开发实现
- 负责编写白盒测试
- 负责签署确认

---

## v2.2.2 新功能：协作规范强制执行

### F-PROC-001: 协作流程规范强制执行

#### 角色边界检查

**Agent1 权限**：
- ✅ 可以创建/修改：docs/01-requirements/, docs/02-design/OUTLINE_*.md, docs/03-test/, docs/04-deployment/
- ❌ 不能操作：docs/02-design/DETAIL_*.md (详细设计文档)
- ❌ 不能操作：src/ (代码文件)
- ❌ 不能签署自己创建的文档

**Agent2 权限**：
- ✅ 可以创建/修改：docs/02-design/DETAIL_*.md, src/, tests/
- ✅ 可以评审：docs/01-requirements/, docs/02-design/OUTLINE_*.md
- ❌ 不能修改 docs/01-requirements/ (评审除外)
- ❌ 不能创建概要设计文档
- ❌ 不能签署自己创建的文档

#### 文档状态阶段绑定

| 状态 | Agent1 动作 | Agent2 动作 |
|------|-------------|-------------|
| DRAFT | 编辑、提交评审 | 仅查看 |
| REVIEW_PENDING | 仅查看 | 评审、签署 |
| REVIEWED | 确认、签署 | 仅查看 |
| APPROVED | 仅查看 | 仅查看 |
| ARCHIVED | 仅查看 | 仅查看 |

#### 完整性门禁

- 不允许部分评审（只评审文档的某一章节）
- 不允许评审子文档（从主文档提取的模块）
- 必须评审完整文档

### F-GIT-001: Git 同步集成

#### 新增命令

```bash
# 合规检查
oc-collab compliance check [role|state|completeness]
oc-collab compliance status
oc-collab compliance results

# Git 同步
oc-collab git sync
oc-collab git status
oc-collab git sync-state
oc-collab git warn

# 阶段推进（自动同步）
oc-collab phase-advance --sync
oc-collab phase-advance --no-sync
```

#### 自动同步行为

| 操作 | 自动同步 |
|------|---------|
| `oc-collab phase-advance` | ✅ 自动 git add → commit → push |
| `oc-collab todo done` | ✅ 自动 git add → commit |

---

---

## 工作流程

### 阶段1: 需求评审
1. Agent1 创建需求文档
2. Agent1 更新状态文件，标记 pm_signoff: true
3. Agent2 Review 后写评审意见
4. Agent1 查看评审意见，更新需求文档
5. 循环直到达成一致
6. Agent2 签署需求确认
7. Agent1 打标签：requirements-v*approved

### 阶段2: 设计评审

设计阶段分为两个子阶段：概要设计和详细设计

#### 2.1 概要设计 (Agent 1 创建)

1. Agent 1 基于需求文档创建概要设计
2. Agent 1 创建TODO要求Agent 2评审概要设计 ← 新增
3. Agent 2 评审概要设计
4. Agent 1 修订并更新状态
5. Agent 2 签署概要设计确认

#### 2.2 详细设计 (Agent 2 创建)

1. Agent 2 基于概要设计创建详细设计
2. Agent 1 评审详细设计
3. Agent 2 修订并更新状态
4. Agent 1 签署详细设计确认

### 阶段3: 开发与测试
1. Agent1 编写黑盒测试用例
2. Agent2 开发功能
3. Agent2 编写白盒测试
4. Agent1 执行黑盒测试
5. Agent1 签署测试确认
6. Agent1 打标签：test-v*passed

### 阶段4: 部署发布
1. Agent1 执行部署
2. Agent1 更新变更记录
3. Agent1 打标签：release-v*.*.*

---

## Git 使用规范

### 分支命名
- 需求评审: requirements-review-*
- 设计评审: design-review-*
- 开发: feature/*
- 修复: fix/*

### 提交规范
```
<type>(<scope>): <description>
```

Types:
- feat: 新功能
- docs: 文档
- review: 评审意见
- signoff: 签署确认
- test: 测试

### 标签规范
- requirements-v*approved - 需求确认
- outline-design-v*approved - 概要设计确认
- design-v*approved - 详细设计确认
- test-v*passed - 测试通过
- release-v*.*.* - 正式发布

---

## 文件命名规范

| 阶段 | 文件类型 | 命名模式 |
|------|---------|---------|
| 需求 | 需求文档 | requirements_v{版本}.md |
| 需求 | 评审意见 | requirements_review_v{版本}.md |
| 需求 | 签署确认 | requirements_signoff.md |
| 设计 | 概要设计 | OUTLINE_DESIGN_v{版本}.md |
| 设计 | 详细设计 | DETAIL_v{版本}.md |
| 设计 | 评审意见 | design_review_v{版本}.md |
| 设计 | 签署确认 | design_signoff.md |
| 测试 | 黑盒用例 | blackbox_test_cases.md |
| 测试 | 白盒结果 | whitebox_test_results.md |
| 测试 | 黑盒结果 | blackbox_test_results.md |

---

## 状态文件更新规则

每次更新文档后，必须同步更新 `state/project_state.yaml`：
- 更新版本号
- 更新状态
- 更新最后更新时间
- 记录当前操作的 Agent

---

## TODO 任务管理规范 ⭐

**任何协作动作发生后，必须创建TODO来追踪**

### 什么时候必须创建TODO？

| 场景 | 示例 | 执行人 |
|------|------|--------|
| 发现Bug | 测试失败、流程问题 | 发现者 |
| 创建提案 | 新功能想法 | Agent 1 |
| 评审通过 | 需求/设计评审通过 | Agent 2 |
| 开发完成 | 功能实现完成 | Agent 2 |
| 测试完成 | 测试用例编写完成 | Agent 1 |
| 发现遗留问题 | 上次会议遗留 | 当前Agent |
| 需求变更 | 需求修改 | Agent 1 |
| 设计变更 | 设计修改 | Agent 2 |

### ⚠️ TODO 创建黄金法则

| 规则 | 说明 | 示例 |
|------|------|------|
| **只创建当前步骤的TODO** | 只创建"下一步要做"的TODO，不要创建下下步的TODO | ✅ 修复Bug → ❌ 不要同时创建"修复后测试" |
| **不提前创建** | 只有当某项工作明确需要做时才创建TODO | ❌ Bug还没发现就创建"修复Bug的TODO" |
| **不代他人创建** | 即使TODO指向自己，也不要替别人创建 | ❌ Agent1 不要创建"Agent2修复Bug"的TODO |
| **不自创TODO** | 不要为了"可能有需要"而预先创建TODO | ❌ "以后可能需要测试" → 实际需要时再创建 |

### 为什么不应该提前创建TODO？

| 错误做法 | 问题 | 正确做法 |
|----------|------|----------|
| 提前创建"修复后测试"的TODO | 时机不对，Bug还没修复 | 等Agent2提交修复后，Agent1自主创建 |
| 预先创建下阶段TODO | 流程可能变化，TODO可能作废 | 实际进入该阶段时再创建 |
| 代他人创建TODO | 不知道他人什么时候需要 | 由需要的人自己创建 |

### 实际案例：BUG-20260208-003的正确处理

| 错误做法 | 正确做法 |
|----------|----------|
| 1. 发现Bug | 1. 发现Bug |
| 2. 创建"Agent2修复"的TODO | 2. 创建"Agent2修复"的TODO |
| 3. 提前创建"Agent1重新测试"的TODO ❌ | 3. 等待Agent2修复并提交 |
| 4. 混乱 | 4. Agent1看到修复后，自主创建测试TODO ✅ |

### TODO 创建时机判断

| 问题 | 答案 |
|------|------|
| 这项工作明确要做吗？ | ✅ 是 → 创建 |
| 这项工作现在必须做吗？ | ✅ 是 → 创建 |
| 这是他人的工作吗？ | ✅ 是 → 只有对方需要时协助创建 |
| 这项工作可能变化吗？ | ✅ 是 → 推迟到明确时再创建 | |

### 评审反馈TODO体系 ⭐

**原则**：TODO是短程"通知-完成"结构，保持最大灵活性

```
Agent2评审 → TODO设为complete（评审工作完成）
              ↓
        如需Agent1反馈
              ↓
    Agent2创建新TODO给Agent1
```

**示例**：
1. Agent2评审需求文档，发现问题
2. Agent2将评审TODO设为complete
3. Agent2创建新TODO："Agent1修复评审意见"（agent_id: "1"）
4. Agent1修复后，可创建TODO给Agent2确认

**禁止**：Agent2将评审TODO设为complete后，自己再创建TODO给自己

### TODO 标准格式

```yaml
todos:
  - id: "TODO-001"
    content: "任务描述"
    from: "agent1"        # 发起人
    to: "agent2"          # 执行人
    phase: "requirements" # 阶段
    priority: "P0"        # P0/P1/P2
    status: "pending"     # pending/in_progress/completed
    created_at: "timestamp"
    started_at: "timestamp"
    completed_at: "timestamp"
```

### TODO 创建检查清单

```bash
# 创建TODO后必须检查：
1. ✅ 是否指定了 from（发起人）
2. ✅ 是否指定了 to（执行人）
3. ✅ 是否指定了 phase（阶段）
4. ✅ 是否指定了 priority（P0/P1/P2）
5. ✅ 描述是否清晰可执行
```

### TODO 优先级定义

| 优先级 | 定义 | 响应时间 |
|--------|------|----------|
| **P0** | 阻塞当前流程 | 立即处理 |
| **P1** | 影响当前版本 | 本次会话完成 |
| **P2** | 可以推迟 | 下个版本完成 |

### TODO 生命周期

```
创建 → 分配 → 执行 → 完成
  ↓       ↓       ↓
  确认    开始    签署
```

| 阶段 | 操作 | 说明 |
|------|------|------|
| **创建** | todowrite | 任务描述清晰 |
| **分配** | 自动分配给 to 字段 | 指定执行人 |
| **执行** | todoedit --status in_progress | 开始执行 |
| **完成** | todoedit --status completed | 执行完成 |
| **确认** | 签署/关闭 | 任务闭环 |

### 常见错误与正确做法

| 错误做法 | 正确做法 |
|----------|----------|
| 发现问题不创建TODO | 发现问题立即创建TODO |
| TODO不指定执行人 | 必须指定 to 字段 |
| TODO描述模糊 | 描述清晰可执行 |
| 执行完不更新状态 | 执行完立即标记completed |
| 跨会话丢失TODO | Compaction前检查TODO状态 |
| 验收通过不更新state | 签署后更新project_state.yaml |
| 提前创建下阶段的TODO | 只有明确需要时才创建 |
| 代他人创建TODO | 由需要的人自己创建 |
| 为了"可能有需要"自创TODO | 实际需要时再创建 |
| 手动编辑文件后不git add/commit | 编辑后立即提交 |

### ⚠️ BUG-20260208-007教训：手动编辑文件的问题

**场景**：Agent1直接编辑 `state/agent_adhoc_todos.yaml`，Agent2看不到更改

**问题**：
- Agent1编辑文件后忘记git add/commit
- Agent2拉取远程后看不到新TODO
- 误以为是todowrite工具的bug

**教训**：
```
不是todowrite的bug，而是操作问题！

手动编辑 state/agent_adhoc_todos.yaml 后，必须：
1. git add state/agent_adhoc_todos.yaml
2. git commit -m "chore: 添加TODO-XXX"
3. git push（或等待其他人push）

验证方法：
git status  # 检查文件是否已标记
git log --oneline  # 检查提交是否成功
```

**正确做法**：
| 方式 | 步骤 | 验证 |
|------|------|------|
| 使用todowrite | `oc-collab todowrite --content "任务" --agent 2` | 检查文件是否已修改 |
| 手动编辑 | 1.编辑文件 2.git add 3.git commit | `git status && git log` |

**调查方法**：遇到TODO问题先运行测试
```bash
# 验证todowrite是否正常
python3 -m pytest tests/test_todowrite_persistence.py -v
```

---

### TODO 追踪检查

```bash
# 每次会话开始时
oc-collab todo

# 检查我的待办
# - pending: 待处理
# - in_progress: 进行中
# - completed: 已完成

# Compaction 前
# 1. 检查所有TODO状态
# 2. 更新未完成的TODO
# 3. 记录遗留问题到state/
```

---

## 关键提醒

### Agent 1 的职责
- 创建需求文档和概要设计
- 评审详细设计
- 编写黑盒测试用例
- 执行黑盒测试
- 部署和发布
- 打标签

### Agent 2 的职责
- 评审需求和概要设计
- 创建详细设计
- 开发实现
- 编写白盒测试
- 签署确认
- 不准创建概要设计文档
- 不准修改验收标准
- 不准签署需求文档

---

## 当你困惑时

1. 检查当前阶段
2. 确认自己的角色职责
3. 查看待办任务
4. 按照工作流程执行

---

## 快速参考

### 当前阶段判断
- state/project_state.yaml 中查看当前 phase

### 任务来源
- 检查 state/agent_adhoc_todos.yaml 中的待办任务

### 下一步行动
- 遵循当前阶段的工作流程
- 等待任务指派（Agent 2）

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.2.0 | 2026-02-01 | 初始版本 |
| v2.2.1 | 2026-02-06 | 动态Checklist |
| v2.2.2 | 2026-02-07 | 协作规范强制执行 + Git同步集成 |
| v2.2.3 | 2026-02-08 | Agent体验优化 |
| v2.2.4 | 2026-02-08 | 新增TODO任务管理规范 |
| v2.2.5 | 2026-02-08 | 新增Bug管理流程规范 + Bug管理Skill |
| v2.2.6 | 2026-02-08 | 设计流程分离：概要设计(Agent1) + 详细设计(Agent2) |
| v2.2.7 | 2026-02-08 | 新增评审反馈TODO体系 |
| v2.2.8 | 2026-02-08 | 新增TODO创建黄金法则 |
| v2.2.9 | 2026-02-08 | 新增手动编辑文件规范 + BUG-20260208-007教训 |

## 📚 教训总结（v2.2.8新增）

### BUG-20260208-003: 测试中发现新Bug的协作流程

**场景**: v2.2.4验收时发现oc-collab工具无法识别项目状态

**核心教训**:

| 原则 | 说明 |
|------|------|
| 测试完整性 | v2.2.x功能 + 基础设施必须全部测试 |
| Bug测试覆盖 | 测试中发现的Bug必须有测试用例覆盖 |
| Agent1测试权限 | Agent1可以编写测试代码（测试是其职责） |
| 回退验收 | 发现新Bug必须回退验收状态 |

### 协作流程修正

**原流程**:
```
开发完成 → 测试 → 通过 → 签署 ✅
```

**修正后流程**:
```
开发完成 → 测试 → 通过 → 发现新Bug
                                    ↓
                              ✅ 写测试用例覆盖Bug
                              ✅ 回退验收状态
                              ✅ 创建TODO给Agent2
                              ⏳ 等待修复
                              修复后重新测试 → 通过 → 签署 ✅
```

### Agent职责澄清

| 职责 | Agent1 | Agent2 |
|------|--------|--------|
| 编写黑盒测试代码 | ✅ | ✅ |
| 编写白盒测试代码 | ❌ | ✅ |
| 创建Bug报告 | ✅ | ✅ |
| 修复Bug | ❌ | ✅ |
| 签署Bug修复验收 | ✅ | ❌ |

---

**维护者**: Agent 1
**更新日期**: 2026-02-08
