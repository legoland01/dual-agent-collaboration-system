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
