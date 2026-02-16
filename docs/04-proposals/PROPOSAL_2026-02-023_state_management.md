# Proposal: 状态管理系统设计

**提案编号**: PROPOSAL_2026-02-023  
**日期**: 2026-02-16  
**作者**: Consultant (战略规划)  
**状态**: DRAFT

---

## 一、背景

### 1.1 状态管理的定位

状态管理系统是刚性框架的基础：
- 里程碑状态决定流程流转
- TODO状态反映任务进度
- 签署状态关联里程碑

### 1.2 当前问题

| 问题 | 说明 |
|------|------|
| 状态分散 | 里程碑/TODO/签署状态各自管理 |
| 状态不一致 | 各模块状态定义不统一 |
| 状态无审计 | 状态变更无记录 |

---

## 二、状态类型设计

### 2.1 里程碑状态

```
┌─────────────────────────────────────────────────────────────┐
│ 需求 → 概要设计 → 详细设计 → 开发 → 测试 → 部署 → 完成    │
└─────────────────────────────────────────────────────────────┘
```

| 状态 | 说明 |
|------|------|
| pending | 待开始 |
| in_progress | 进行中 |
| completed | 已完成 |
| blocked | 已阻塞 |
| skipped | 已跳过（需豁免） |

### 2.2 TODO状态

```
draft → pending → in_progress → completed → closed
                ↘ cancelled ↗
```

| 状态 | 说明 | 可转换到 |
|------|------|----------|
| draft | 草稿 | pending |
| pending | 待处理 | completed, cancelled |
| in_progress | 处理中 | completed, cancelled |
| completed | 已完成 | closed |
| cancelled | 已取消 | - |
| closed | 已关闭 | - |

### 2.3 签署状态

| 状态 | 说明 |
|------|------|
| unsigned | 未签署 |
| signed | 已签署 |
| approved | 已批准 |
| rejected | 已拒绝 |
| cancelled | 已取消 |

---

## 三、统一状态管理

### 3.1 状态存储

```yaml
# project_state.yaml
project:
  name: my-project
  status: in_progress
  current_milestone: development
  
milestones:
  requirements:
    status: completed
    signoff: requirements-001
    completed_at: 2026-02-15T10:00:00
    
  design:
    status: completed
    signoff: design-001
    completed_at: 2026-02-15T14:00:00
    
  development:
    status: in_progress
    started_at: 2026-02-15T15:00:00
    todos:
      - TODO-1to2-001
      - TODO-1to2-002

todos:
  TODO-1to2-001:
    status: completed
    target_agent: agent2
    ...
    
signoffs:
  requirements-001:
    milestone: requirements
    status: approved
    signed_by: agent1
```

### 3.2 状态变更日志

```yaml
# state_history.yaml
- timestamp: 2026-02-16T10:00:00
  entity: milestone/design
  field: status
  old_value: in_progress
  new_value: completed
  actor: agent2
  reason: "设计文档已完成并通过评审"
  
- timestamp: 2026-02-16T10:05:00
  entity: todo/TODO-1to2-001
  field: status
  old_value: pending
  new_value: completed
  actor: agent2
  evidence: ci_log_001
```

---

## 四、与刚性框架整合

### 4.1 状态强校验

| 刚性规则 | 状态约束 |
|----------|----------|
| RF-001 自验收 | TODO完成状态只能由target_agent变更 |
| RF-002 里程碑跳过 | 只能推进到已完成前置的里程碑 |
| RF-003 共谋 | 状态变更需有证据支持 |

### 4.2 状态一致性校验

```python
def check_state_consistency():
    errors = []
    
    # 里程碑状态与签署一致
    for milestone in milestones:
        signoff = get_signoff(milestone)
        if signoff.status != 'approved' and milestone.status == 'completed':
            errors.append(f"里程碑{.milestone}无签署但状态为completed")
    
    # TODO状态与里程碑一致
    for todo in todos:
        if todo.status == 'completed' and not is_milestone_completed(todo.milestone):
            errors.append(f"TODO关联里程碑未完成")
    
    if errors:
        raise StateInconsistencyError(errors)
```

---

## 五、实施计划

| 版本 | 功能 | 工时 |
|------|------|------|
| v2.3 | 统一状态模型 | 4h |
| v2.3 | 状态变更日志 | 4h |
| v2.5 | 状态一致性校验 | 6h |
| v2.5 | 状态强制(R1) | 6h |

---

## 六、关联

| 关联 | 说明 |
|------|------|
| TODO系统 | TODO状态管理 |
| 刚性框架 | 状态强制校验 |
| 签署流程 | 签署状态关联里程碑 |
| PM-Agent | 状态可视化 |

---

**提案状态**: DRAFT
