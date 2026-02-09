# v2.2.5 需求文档

**版本**: v1
**日期**: 2026-02-08
**作者**: Agent 1 (产品经理)
**状态**: DRAFT → 待Agent 2评审
**关联**: 
- ANALYSIS_v2.2.5_Requirements_Analysis.md (APPROVED)
- docs/02-design/OUTLINE_v2.2.5.md (待评审)

---

## 1. 版本概述

### 1.1 版本目标

**核心目标**：修复流程漏洞，完善协作规范

### 1.2 功能范围

| 功能 | 类型 | 工时 | 来源 |
|------|------|------|------|
| 文件Owner机制 | 需开发 | 5.5h | FP-001 |
| 状态识别修复 | Bug修复 | 1h | FP-014 |
| signoff修复 | Bug修复 | 1h | FP-015 |
| 版本结束后需求分析流程 | 用Skill | 1h | FP-002 |
| 评审机制优化 | 用Skill | 2h | FP-011 |

**总计工时**: 10.5h

---

## 2. 功能需求

### 2.1 FR-OWNER-001: 文件Owner机制

**功能描述**：
- 文件创建者 = Owner
- 只有Owner能修改文件
- 签署后Owner转移给签署方

**验收标准**：
- [ ] Agent1创建的文件，Agent1能修改
- [ ] Agent1创建的文件，Agent2不能修改
- [ ] Agent2签署后，Owner转移给Agent2
- [ ] Agent2能修改签署后的文件

---

### 2.2 FR-STATE-001: 状态识别修复

**功能描述**：
- 修复StateManager，支持v2.2.x版本化结构
- oc-collab status能正确识别当前版本状态

**验收标准**：
- [ ] `oc-collab status` 显示正确的项目名称
- [ ] `oc-collab status` 显示正确的当前阶段
- [ ] `oc-collab status` 显示正确的Agent ID

---

### 2.3 FR-SIGN-001: signoff修复

**功能描述**：
- 修复_get_stage_data方法
- 修复_save_stage_data方法
- 支持v2.2.x版本化结构

**验收标准**：
- [ ] `oc-collab signoff test` 能正确读取testing字段
- [ ] `oc-collab signoff test` 能正确保存到testing字段
- [ ] 签署后状态正确更新

---

### 2.4 FR-PROC-001: 版本结束后需求分析流程

**功能描述**：
- 每个版本部署完成后，必须立即执行需求分析
- 整合所有待处理文档(Proposal/Memo/Bug/Retrospective/Strategy)
- 确定下一版本范围

**验收标准**：
- [ ] 版本部署完成后创建需求分析报告
- [ ] 报告包含所有待处理文档的整合
- [ ] 报告确定下一版本功能范围

---

### 2.5 FR-PROC-002: 评审机制优化

**功能描述**：
- 明确定义评审优先级
- Critical Review覆盖Technical Review
- 解决两个评审并存的问题

**验收标准**：
- [ ] 协作规范中明确评审优先级
- [ ] 同一文档只有一个最终评审结论
- [ ] Critical Review结论覆盖Technical Review

---

## 3. 测试需求

### 3.1 单元测试

| 模块 | 测试文件 | 覆盖率要求 |
|------|----------|------------|
| role_boundary_checker | tests/test_role_boundary.py | ≥80% |
| state_manager | tests/test_state_manager.py | ≥80% |
| signoff | tests/test_signoff.py | ≥80% |

### 3.2 E2E测试

| 测试场景 | 预期结果 |
|----------|----------|
| Agent1创建文件，Agent1修改 | 成功 |
| Agent1创建文件，Agent2修改 | 被拒绝 |
| Agent2签署后修改 | 成功 |
| oc-collab status | 正确显示状态 |
| oc-collab signoff test | 正确签署 |

---

## 4. 文档需求

### 4.1 Skill更新

| Skill | 更新内容 |
|-------|----------|
| oc_collab_requirements_guide | 添加版本周期规则 |
| oc_collab_collaboration_guide | 添加评审机制优化 |

---

## 5. 验收签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品经理 | Agent 1 | 2026-02-08 | ⏳ |
| 开发负责人 | Agent 2 | | ⏳ |

---

**创建人**: Agent 1
**日期**: 2026-02-08
**状态**: DRAFT
