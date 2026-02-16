# Proposal: 签署流程设计

**提案编号**: PROPOSAL_2026-02-022  
**日期**: 2026-02-16  
**作者**: Consultant (战略规划)  
**状态**: DRAFT

---

## 一、背景

### 1.1 签署流程的重要性

签署流程是刚性框架的核心依赖：
- 签署是里程碑推进的触发条件
- 签署记录是刚性框架审计的依据
- 签署强制是R1阻断的基础

### 1.2 当前问题

| 问题 | 说明 |
|------|------|
| 签署不完整 | Agent跳过签署直接进入下一阶段 |
| 签署无追踪 | 签署记录散落，缺乏统一管理 |
| 签署无强制 | 可绕过签署继续流程 |

---

## 二、签署流程设计

### 2.1 签署类型

| 类型 | 触发条件 | 签署人 | 刚性级别 |
|------|----------|--------|----------|
| 需求签署 | 需求文档完成 | Agent1 | R1 |
| 设计签署 | 设计文档完成 | Agent1+Agent2 | R1 |
| 开发签署 | 代码完成 | Agent2 | R1 |
| 测试签署 | 测试完成 | Agent1 | R1 |
| 部署签署 | 部署完成 | Agent2 | R1 |

### 2.2 签署状态机

```
┌──────────┐     sign     ┌──────────┐     approve     ┌──────────┐
│  draft   │ ──────────→│  signed  │ ──────────────→│ approved │
└──────────┘              └──────────┘                  └──────────┘
     ↑                         │                              │
     │ cancel                   │ cancel                      │
     └─────────────────────────┴──────────────────────────────┘
```

### 2.3 签署数据模型

```yaml
# milestone_signoffs.yaml
- milestone: requirements
  status: approved
  signed_by: agent1
  signed_at: 2026-02-16T10:00:00
  evidence:
    - doc_path: docs/01-requirements/REQ-001.md
    - doc_path: docs/01-requirements/REQ-002.md
  comment: "需求文档完成，符合签署标准"
  
- milestone: design
  status: signed
  signed_by: agent2
  signed_at: 2026-02-16T11:00:00
  evidence:
    - doc_path: docs/02-design/...
  comment: "设计文档完成"
```

### 2.4 签署校验规则

| 规则 | 说明 |
|------|------|
| 前置签署 | 进入下一里程碑前必须完成当前签署 |
| 签署人校验 | 签署人必须是指定角色 |
| 证据完整 | 签署必须包含必要文档证据 |
| 时间顺序 | 签署时间不能早于前置里程碑 |

---

## 三、与刚性框架整合

### 3.1 刚性规则映射

| 刚性规则 | 签署整合点 |
|----------|------------|
| RF-001 自验收 | 签署人不能是代码作者 |
| RF-002 里程碑跳过 | 前置签署未完成则阻断 |
| RF-003 共谋 | 需双签（Agent1+Agent2） |
| RF-004 数据伪造 | 签署必须包含文档证据 |

### 3.2 签署强制

```python
def complete_milestone(milestone):
    # 检查签署
    signoff = get_signoff(milestone)
    if not signoff:
        raise MilestoneBlockedError(f"未完成{milestone}签署")
    
    # 检查签署人
    if not is_valid_signer(signoff.signed_by, milestone):
        raise PermissionError(f"签署人无权限")
    
    # 检查证据
    if not has_evidence(signoff):
        raise ValidationError("签署缺少必要证据")
```

---

## 四、实施计划

| 版本 | 功能 | 工时 |
|------|------|------|
| v2.2 | 签署YAML结构 | 4h |
| v2.5 | 签署强制(R1) | 6h |
| v2.5 | 签署校验规则 | 4h |

---

**提案状态**: DRAFT
