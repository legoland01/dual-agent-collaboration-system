# PROPOSAL：OC-Collab 需求评审 Skill 机制

**提案编号**: PROPOSAL-v2.2.3-001
**版本**: v1
**创建日期**: 2026-02-08
**创建人**: Agent 1 (产品经理)
**状态**: 待评审

---

## 1. 背景

### 1.1 问题

| 问题 | 表现 | 影响 |
|------|------|------|
| 走形式评审 | Agent 只写"✅ 通过"，不回答实质性问题 | 需求质量无法保证 |
| 角色混淆 | Agent 1 创建设计文档，Agent 2 写黑盒测试 | 职责混乱 |
| Skill 失效 | Skill 是声明性的，AI 可能不加载 | 规范无法执行 |

### 1.2 核心洞察

```
AI 不是故意的 - 它只是在新 session 中忘记了我们讨论过的规范

解决方案 - 把规范变成代码的前置条件：
评审前必须加载 skill，否则拒绝评审
```

---

## 2. 目标

### 2.1 核心目标

把评审规范从"建议"变成"强制"：

| 目标 | 实现方式 |
|------|----------|
| 加载评审指南 skill | 代码强制检查，不加载无法评审 |
| 实质性评审 | 必须回答所有检查项，否则拒绝签署 |
| 职责分明 | 代码检查角色，禁止跨角色操作 |

### 2.2 预期收益

| 收益 | 说明 |
|------|------|
| 评审质量提升 | 不回答实质性问题的评审被拒绝 |
| 职责清晰 | 代码检查角色，禁止越权 |
| 可追溯 | 每次评审都有 skill 版本记录 |

---

## 3. 功能需求

### 3.1 FR-SKILL-001: Skill 强制加载

**描述**: 评审需求前，必须先加载评审指南 skill。

**实现方式**:
```python
def review_requirements(doc_path):
    if not has_loaded_skill("oc_collab_requirements_review_guide"):
        raise Exception("请先加载评审指南 skill")
```

**验收标准**:
- [ ] 未加载 skill 时，拒绝评审并提示
- [ ] 支持动态加载不同场景的评审 skill
- [ ] 记录已加载的 skill 版本

---

### 3.2 FR-SKILL-002: 实质性检查

**描述**: 评审必须回答实质性检查项，禁止只写"✅ 通过"。

**检查项**:
| 类别 | 必须回答的问题 |
|------|--------------|
| 技术可行性 | 这个功能能实现吗？有风险吗？ |
| 完整性 | 验收标准可测试吗？异常流程呢？ |
| 可实施性 | 工时合理吗？依赖正确吗？ |
| 逆向思考 | 如果我是用户，好用吗？最大风险是什么？ |

**实现方式**:
```python
def check_substantive_review(review_content):
    if not has_answered_all_questions(review_content):
        raise Exception("必须回答所有实质性检查项")
```

**验收标准**:
- [ ] 只写"✅ 通过"会被拒绝
- [ ] 必须至少回答 4 类问题
- [ ] 逆向思考是必填项

---

### 3.3 FR-SKILL-003: 角色检查

**描述**: 代码检查签署角色，禁止跨角色操作。

**检查规则**:
| 角色 | 可以签署 | 禁止签署 |
|------|---------|---------|
| Agent 1 | 创建需求、发起评审 | 技术评审通过 |
| Agent 2 | 技术评审通过 | 创建需求 |

**实现方式**:
```python
def check_signing_role(agent, sign_content):
    if agent == "agent1" and "技术评审通过" in sign_content:
        raise Exception("Agent 1 不能签署\"技术评审通过\"")
```

**验收标准**:
- [ ] 跨角色签署被拒绝
- [ ] 错误信息清晰指出问题

---

## 4. 支持不同评审场景

### 4.1 场景定义

| 场景 | Skill | 用途 |
|------|-------|------|
| 默认评审 | oc_collab_requirements_review_guide | 标准需求评审 |
| 轻量评审 | oc_collab_quick_review_guide | 小改动、Bugfix |
| 深度评审 | oc_collab_deep_review_guide | 大版本、重构 |

### 4.2 动态加载

```python
def review_with_scenario(doc_path, scenario="default"):
    skill_id = get_skill_id(scenario)
    
    if not has_loaded_skill(skill_id):
        raise Exception(f"请先加载 {scenario} 评审 skill")
    
    # 使用该场景的检查清单
    checklist = load_checklist(skill_id)
```

---

## 5. 非功能需求

### 5.1 兼容性

| 要求 | 说明 |
|------|------|
| 向后兼容 | 已有评审流程不变 |
| 可选启用 | Skill 强制加载可以配置开关 |

### 5.2 性能

| 要求 | 说明 |
|------|------|
| 检查延迟 | < 100ms |
| Skill 加载 | < 1s |

---

## 6. 工时预估

| 功能 | 工时 |
|------|------|
| FR-SKILL-001: Skill 强制加载 | 2h |
| FR-SKILL-002: 实质性检查 | 3h |
| FR-SKILL-003: 角色检查 | 1h |
| 测试 + 修复 | 2h |
| **总计** | **8h** |

---

## 7. 依赖关系

| 依赖 | 来源 |
|------|------|
| oc_collab_requirements_review_guide | skill (v1) |
| CLI 框架修改 | 现有代码 |

---

## 8. 实施路线图

### Phase 1: MVP（v2.2.3）

| 功能 | 工时 |
|------|------|
| Skill 强制加载 | 2h |
| 实质性检查 | 2h |
| 角色检查 | 1h |

### Phase 2: 增强（v2.3.0）

| 功能 | 说明 |
|------|------|
| 多场景支持 | 轻量/深度评审 |
| Skill 版本管理 | 追踪评审规范版本 |
| 评审统计 | 分析评审质量 |

---

## 9. 开放问题

| 问题 | 说明 | 负责人 |
|------|------|--------|
| Skill 如何验证加载？ | 检查文件存在还是解析内容？ | 讨论 |
| 可配置开关 | 是否允许跳过 skill 检查？ | 讨论 |

---

## 10. 相关文档

| 文档 | 说明 |
|------|------|
| skill/oc_collab_requirements_review_guide/ | 评审指南 skill |
| docs/00-standards/REQUIREMENTS_REVIEW_GUIDE.md | 评审规范 |

---

## 签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品经理 | Agent 1 | 2026-02-08 | ✅ |
| 开发负责人 | Agent 2 | | ⏳ |

---

## 版本历史

| 版本 | 日期 | 作者 | 变更 |
|------|------|------|------|
| v1 | 2026-02-08 | Agent 1 | 初始版本 |

---

**文档版本**: v1
**创建日期**: 2026-02-08
**状态**: DRAFT (待 Agent 2 评审)
