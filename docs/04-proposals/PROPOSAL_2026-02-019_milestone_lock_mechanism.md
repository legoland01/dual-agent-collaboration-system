# Proposal: 刚性流程机制设计

**版本**: v1  
**日期**: 2026-02-15  
**作者**: Consultant (战略规划)  
**状态**: 待评审

---

## 一、背景

### 1.1 问题描述

Agent1和Agent2都会绕过规则：

#### Agent2的问题

| 历史Bug | 跳过的内容 |
|---------|------------|
| BUG-20260210-003 | 跳过"提交黑盒测试结果给Agent1验收" |
| BUG-20260215-014 | 自检被跳过 |
| BUG-20260214-005 | Skill查询被跳过 |
| v2.3.0测试 | Agent2自己写测试，自己给自己通过 |

#### Agent1的问题（MEMO_20260216_agent1_behavior_problems）

| 问题 | 表现 |
|------|------|
| TODO编号错误 | 手动指定agent，不遵守编号规则 |
| 验证错误 | 直接信工具输出，不验证步骤 |
| 提前创建TODO | 违反版本流程顺序 |
| YAML修改出错 | 不细心，不验证 |

#### 共同根因

| 因素 | 说明 |
|------|------|
| **Agent心态** | 更快"完成" > 完整走流程 |
| **绕过成本低** | 缺少强制机制，跳过没有惩罚 |
| **知行不一** | "知道"不等于"做到" |
| **态度问题** | 规则是装饰，不是用来执行的 |

---

**结论**：Agent1和Agent2都需要刚性机制约束。

---

## 二、核心思路

**把刚性流程写进代码**，而不是依赖Agent的自觉性。

### 2.1 架构原则：刚性流程独立

**关键原则**：刚性流程模块必须独立，避免传染到其他模块。

```
┌─────────────────────────────────────────────┐
│           项目Skill (可定制部分)              │  ← 可调整
├─────────────────────────────────────────────┤
│         核心里程碑 (强制)                    │  ← 独立模块
├─────────────────────────────────────────────┤
│         内置机制 (强制)                      │  ← 独立模块
└─────────────────────────────────────────────┘
```

**理由**：
- 未来如果需要修改流程，只需改动核心模块
- 不会因为流程调整而影响Skill、测试等其他模块
- 便于维护和演进

### 2.2 分层结构

| 层级 | 说明 |
|------|------|
| **核心里程碑** | 5个阶段交付物，强制，不可跳过 |
| **内置机制** | 代码检查、文档同步、webhook，oc-collab自带 |
| **Skill控制** | 项目特定配置（覆盖率标准等），可定制 |

---

## 三、刚性流程设计

### 3.1 核心里程碑（独立模块，不可跳过）

| 里程碑 | 强制交付物 |
|--------|-----------|
| requirements | 需求文档 + 签署 |
| design | 设计文档 + 签署 |
| development | 代码 + 单元测试通过 |
| testing | E2E测试通过 |
| deployment | 成功部署 |

**本质**：没有这个里程碑，软件就无法交付/发布。

### 3.2 内置机制（独立模块，强制执行）

| 机制 | 说明 |
|------|------|
| 代码检查 | lint, type check |
| 文档同步 | 自动同步 |
| webhook | 通信机制 |

### 3.3 项目Skill（可定制）

| 项目可配置 | 说明 |
|------------|------|
| 覆盖率标准 | 项目可调整标准，但不能跳过覆盖率检查 |
| 验收规则 | 项目特定的验收流程 |

### 3.4 里程碑依赖锁

```python
# oc-collab/core/milestone_locker.py

MILESTONE_LOCKS = {
    "requirements": {
        "next": ["design"],
        "blocked_by": []
    },
    "design": {
        "next": ["development"],
        "blocked_by": ["requirements"]
    },
    "development": {
        "next": ["testing"],
        "blocked_by": ["design"],
        "required_todos": ["创建测试用例"]  # 必须先创建
    },
    "testing": {
        "next": ["deployment"],
        "blocked_by": ["development"],
        "required_checks": ["单元测试通过", "黑盒测试通过"]  # 必须通过
    },
    "deployment": {
        "next": [],
        "blocked_by": ["testing"],
        "required_approvals": ["Agent1签署"]  # 必须签署
    }
}
```

### 3.2 不可跳过规则

| 阶段 | 刚性要求 |
|------|----------|
| **requirements → design** | 需求文档必须存在且已签署 |
| **design → development** | 设计文档必须存在且已签署 |
| **development → testing** | 代码必须存在，单元测试必须通过 |
| **testing → deployment** | E2E测试必须通过，Agent1必须验收 |
| **deployment** | 里程碑锁全部解开才能发布 |

### 3.3 CLI命令检查

```python
# oc-collab/cli/phase_advance.py

def check_milestone_lock(current_phase, target_phase):
    """检查里程碑是否可以推进"""
    locks = MILESTONE_LOCKS[current_phase]
    
    # 检查blocked_by
    if locks.get("blocked_by"):
        for phase in locks["blocked_by"]:
            if not is_phase_completed(phase):
                raise MilestoneLockedError(
                    f"无法推进到{target_phase}，请先完成{phase}阶段"
                )
    
    # 检查required_todos
    if locks.get("required_todos"):
        for todo in locks["required_todos"]:
            if not is_todo_completed(todo):
                raise MilestoneLockedError(
                    f"无法推进到{target_phase}，请先完成: {todo}"
                )
    
    # 检查required_checks
    if locks.get("required_checks"):
        for check in locks["required_checks"]:
            if not is_check_passed(check):
                raise MilestoneLockedError(
                    f"无法推进到{target_phase}，请先通过: {check}"
                )
    
    # 检查required_approvals
    if locks.get("required_approvals"):
        for approval in locks["required_approvals"]:
            if not is_approved(approval):
                raise MilestoneLockedError(
                    f"无法推进到{target_phase}，请先获得: {approval}"
                )
```

### 3.4 错误示例

```bash
# 尝试跳过testing直接部署
$ oc-collab advance -p deployment
Error: 无法推进到deployment，请先完成testing阶段

# 尝试在测试未通过时部署
$ oc-collab deploy
Error: 无法部署，请先通过黑盒测试

# 尝试跳过签署
$ oc-collab signoff --force
Error: 签署流程不可跳过，请在docs/03-test/中提交测试报告
```

---

## 四、交叉验收机制

### 4.1 Agent2不能验收自己的代码

```python
# 验收规则
APPROVAL_RULES = {
    "单元测试": {"executor": "Agent2", "approver": "Agent1"},
    "E2E测试": {"executor": "Agent2", "approver": "Agent1"},
    "代码审查": {"executor": "Agent2", "approver": "Agent1"}
}
```

### 4.2 自动拦截

```python
def submit_for_approval(test_type, submitter):
    rule = APPROVAL_RULES[test_type]
    if rule["executor"] == submitter:
        raise ApprovalError(
            f"不能自己验收自己: {test_type}由{rule['executor']}执行，"
            f"需要{rule['approver']}验收"
        )
```

---

## 五、实施计划

### 5.1 短期（v2.3.1）

- 定义里程碑依赖关系
- 实现基本的里程碑锁检查

### 5.2 中期（v2.4）

- 实现不可跳过规则
- 实现交叉验收机制
- CLI命令集成检查

### 5.3 长期

- 完善检查规则
- 添加豁免机制（紧急情况）

---

## 六、预期收益

| 收益 | 说明 |
|------|------|
| **流程不可绕过** | 刚性流程写进代码，Agent无法跳过 |
| **质量保证** | 交叉验收机制防止自己给自己通过 |
| **可追溯** | 每个里程碑完成情况记录在状态文件中 |
| **明确责任** | 谁执行、谁验收清晰定义 |

---

## 七、风险与应对

| 风险 | 应对 |
|------|------|
| 过于死板 | 添加紧急豁免机制（需审批） |
| 影响效率 | 只对关键里程碑加锁，非关键步骤保持灵活 |

---

## 八、结论

**核心改变**：把流程刚性要求写进代码，让Agent无法绕过。

---

**下一步**：
- 评审通过后纳入开发计划
- 优先实现里程碑锁机制

---

**文档版本历史**：

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-02-15 | 初始版本 |
