# OC-Collab 协作指南 (v2.2.2)

## Agent 角色定义

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

---

## v2.2.2 新功能：协作规范强制执行

### F-PROC-001: 协作流程规范强制执行

#### 角色边界检查

**Agent1 权限**：
- ✅ 可以创建/修改：docs/01-requirements/, docs/03-test/, docs/04-deployment/
- ❌ 不能操作：docs/02-design/ (设计文档)
- ❌ 不能操作：src/ (代码文件)
- ❌ 不能签署自己创建的文档

**Agent2 权限**：
- ✅ 可以创建/修改：docs/02-design/, src/, tests/
- ❌ 不能修改 docs/01-requirements/ (评审除外)
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
1. Agent1 创建详细设计文档
2. Agent2 Review，写评审意见
3. 循环直到达成一致
4. Agent2 签署设计确认
5. Agent1 打标签：design-v*approved

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
- requirements-v1-approved - 需求确认
- design-v1-approved - 设计确认
- test-v1-passed - 测试通过
- release-v1.0.0 - 正式发布

---

## 文件命名规范

| 阶段 | 文件类型 | 命名模式 |
|------|---------|---------|
| 需求 | 需求文档 | requirements_v{版本}.md |
| 需求 | 评审意见 | requirements_review_v{版本}.md |
| 需求 | 签署确认 | requirements_signoff.md |
| 设计 | 详细设计 | detailed_design_v{版本}.md |
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

## 关键提醒

### Agent 1 的职责
- 创建需求和设计文档
- 编写黑盒测试用例
- 执行黑盒测试
- 部署和发布
- 打标签

### Agent 2 的职责
- 评审需求和设计
- 开发实现
- 编写白盒测试
- 签署确认
- 不准创建需求文档
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
