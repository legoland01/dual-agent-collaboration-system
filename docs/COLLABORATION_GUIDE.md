# 双Agent协作流程指南

## Agent角色定义

### Agent 1: 产品经理 + 测试 + 部署
- 负责编写需求说明和系统设计
- 负责编写黑盒测试用例
- 负责评审详细设计
- 负责执行黑盒测试
- 负责部署和发布

### Agent 2: 开发
- 负责评审需求和设计
- 负责开发实现
- 负责编写白盒测试
- 负责签署确认

## 工作流程

### 阶段1: 需求评审
1. Agent1 创建需求文档 (`docs/01-requirements/requirements_v*.md`)
2. Agent1 创建系统设计文档 (`docs/01-requirements/system_design_v*.md`)
3. Agent1 更新状态文件，标记 `pm_signoff: true`
4. Agent2 拉取最新代码，Review 后写评审意见 (`docs/01-requirements/requirements_review_v*.md`)
5. Agent1 查看评审意见，更新需求文档
6. 循环直到达成一致
7. Agent2 更新状态文件：`dev_signoff: true`，签署需求确认
8. Agent1 打标签：`requirements-v*approved`

### 阶段2: 设计评审
1. Agent1 创建详细设计文档 (`docs/02-design/detailed_design_v*.md`)
2. Agent1 更新状态文件
3. Agent2 Review，写评审意见 (`docs/02-design/design_review_v*.md`)
4. 循环直到达成一致
5. Agent2 签署设计确认
6. Agent1 打标签：`design-v*approved`

### 阶段3: 开发与测试
1. Agent1 编写黑盒测试用例 (`docs/03-test/blackbox_test_cases.md`)
2. Agent2 开发功能
3. Agent2 编写白盒测试，记录结果 (`docs/03-test/whitebox_test_results.md`)
4. Agent2 通知 Agent1 测试完成
5. Agent1 执行黑盒测试，记录结果 (`docs/03-test/blackbox_test_results.md`)
6. 循环直到测试通过
7. Agent1 签署测试确认
8. Agent1 打标签：`test-v*passed`

### 阶段4: 部署发布
1. Agent1 执行部署
2. Agent1 更新变更记录 (`docs/04-changelog/change_log.md`)
3. Agent1 打标签：`release-v*.*.*`

## Git使用规范

### 分支命名
- 需求评审: `requirements-review-*`
- 设计评审: `design-review-*`
- 开发: `feature/*`
- 修复: `fix/*`

### 提交规范
```
<type>(<scope>): <description>

[body]

[footer]
```

Types:
- feat: 新功能
- docs: 文档
- review: 评审意见
- signoff: 签署确认
- test: 测试

### 标签规范
- `requirements-v1-approved` - 需求确认
- `design-v1-approved` - 设计确认
- `test-v1-passed` - 测试通过
- `release-v1.0.0` - 正式发布

## 文件命名规范

| 阶段 | 文件类型 | 命名模式 |
|------|---------|---------|
| 需求 | 需求文档 | `requirements_v{版本}.md` |
| 需求 | 系统设计 | `system_design_v{版本}.md` |
| 需求 | 评审意见 | `requirements_review_v{版本}.md` |
| 需求 | 签署确认 | `requirements_signoff.md` |
| 设计 | 详细设计 | `detailed_design_v{版本}.md` |
| 设计 | 评审意见 | `design_review_v{版本}.md` |
| 设计 | 签署确认 | `design_signoff.md` |
| 测试 | 黑盒用例 | `blackbox_test_cases.md` |
| 测试 | 白盒结果 | `whitebox_test_results.md` |
| 测试 | 黑盒结果 | `blackbox_test_results.md` |
| 变更 | 变更记录 | `change_log.md` |

## 状态文件更新规则

每次更新文档后，必须同步更新 `state/project_state.yaml`：
- 更新版本号
- 更新状态
- 更新最后更新时间
- 记录当前操作的 Agent

## 通讯约定

1. Agent2 完成 Review 后，在状态文件中更新 `requirements.status` 为 `pending_pm_update`
2. Agent1 更新文档后，更新状态为 `pending_dev_review`
3. 双方达成一致后，状态更新为 `approved`
4. 签署确认后，更新对应的 `signoff` 字段

---

## 流程合规检查

### Agent 启动时的自我检查

每次开始工作前，Agent 必须快速检查：

| 检查项 | 检查内容 |
|--------|----------|
| Git 最新 | `git pull` 拉取最新代码 |
| 状态文件 | 检查 `state/project_state.yaml` 当前阶段 |
| 待办任务 | 检查 `oc-collab todo` 是否有分配任务 |
| 违规检查 | 上次是否有未处理的违规提醒 |

### 关键决策点的合规检查

| 决策场景 | 合规检查 |
|----------|----------|
| 签署前 | 是否已完成所有 Ad-hoc To-do Items？ |
| 开发前 | 是否有正式任务指派（oc-collab todo）？ |
| 评审前 | 文档是否处于正确状态（READY/IN_REVIEW）？ |
| 提交前 | 是否已运行测试并通过？ |

### 违反流程规范的提醒

当检测到违规行为时，Agent 应自我提醒：

| 违规类型 | 提醒 |
|----------|------|
| 跳过评审直接开发 | ⚠️ 违反协作流程：请先完成评审 |
| 未签署就开发 | ⚠️ PRD 未签署：确认是否继续 |
| 无任务自主开发 | ⚠️ 无正式任务：请等待 Agent 1 指派 |
| 忽略 LSP 错误 | ⚠️ LSP 报错：请先清理错误 |

---

## 任务触发流程

### Agent 2 的职责边界

**核心原则**：Agent 2 禁止主动开始开发，必须等待正式任务指派。

| 场景 | 正确做法 |
|------|----------|
| 需求已评审 | ✅ 等待 Agent 1 发布任务 (`oc-collab todo make`) |
| 设计已评审 | ✅ 等待 Agent 1 发布任务 |
| 发现问题 | ✅ 通知 Agent 1，不要自己修复 |
| 有疑问 | ✅ 询问 Agent 1，不要自己猜 |

### 任务检查点

Agent 2 在开始开发前，必须确认：

- [ ] 有正式的任务指派（`oc-collab todo list` 显示 pending 任务）
- [ ] 任务关联到当前版本的需求
- [ ] 任务范围在需求文档中有明确描述

### 违规处理

| 违规场景 | 处理方式 |
|----------|----------|
| 无任务主动开发 | ⚠️ 提醒：等待正式任务后再开始 |
| 任务范围外开发 | ⚠️ 提醒：任务可能超出范围 |

---

## 需求完整性检查

### 创建设计前的检查

在创建设计文档前，必须检查：

| 检查项 | 说明 |
|--------|------|
| 需求文档完整 | 所有计划的里程碑（M1~M5）都有对应章节 |
| 需求已签署 | 对应需求文档的 `agent1_signoff` 和 `agent2_signoff` 都为 `true` |
| 无遗留 MEMO | MEMO 中的需求已整合到正式需求文档 |

### 评审设计前的检查

在评审设计文档前，必须检查：

| 检查项 | 说明 |
|--------|------|
| 设计对应需求 | 每个设计章节都有对应的需求章节 |
| 设计覆盖所有需求 | 需求中的功能点都被设计覆盖 |
| 无跳跃评审 | 不会跳过需求直接评审设计 |

### 遗漏处理

如果发现需求遗漏：

1. **暂停当前工作**
2. **通知 Agent 1** 需求不完整
3. **等待 Agent 1 补充需求**
4. **需求完整后再继续评审/开发**

---

## MEMO 处理流程

### MEMO 的定位

MEMO 是快速记录想法的工具，不能直接作为开发依据。

### MEMO 到需求的转化

| 步骤 | 操作 | 负责人 |
|------|------|--------|
| 1 | 在 MEMO 中标记需要转化为需求的内容 | 任意 Agent |
| 2 | 创建或更新正式需求文档 | Agent 1 |
| 3 | 走评审签署流程 | Agent 1 + Agent 2 |
| 4 | 需求签署后才能用于开发 | Agent 2 |

### 禁止事项

| 禁止 | 说明 |
|------|------|
| ❌ 直接基于 MEMO 开发 | MEMO 不是正式需求，未经评审 |
| ❌ MEMO 跳过签署 | MEMO 中的需求必须整合到正式文档 |
| ❌ 忽略 MEMO 中的问题 | MEMO 记录的问题需要处理 |

### 检查清单

基于 MEMO 开始开发前，必须确认：

- [ ] MEMO 内容已整合到 `docs/01-requirements/` 下的正式需求文档
- [ ] 需求文档已完成评审并双方签署
- [ ] 任务已通过 `oc-collab todo make` 指派

---

## 协作指南更新规则

### 何时更新协作指南

| 触发事件 | 是否需要更新 |
|----------|--------------|
| 新增协作流程 | ✅ 需要 |
| 发现协作漏洞 | ✅ 需要 |
| 软件功能更新（新增命令） | ✅ 需要 |
| 修复 BUG 后总结的规范 | ✅ 需要 |

### 更新流程

1. **Agent 1** 创建或更新协作指南章节
2. **Agent 2** 评审并签署确认
3. **更新协作指南版本号**
4. **双方学习新规范**

### 版本记录

| 版本 | 更新日期 | 更新内容 |
|------|----------|----------|
| v1 | 2026-01-31 | 初始版本：Agent 角色、工作流程、Git 规范 |
| v2 | 2026-02-06 | 新增：流程合规检查、任务触发流程、需求完整性检查、MEMO 处理流程 |
