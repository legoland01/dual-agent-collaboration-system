# Skill体系梳理报告与重整方案

**版本**: v1.0.0
**日期**: 2026-02-09
**状态**: 待Agent2评审

---

## 一、现有Skill体系概览

### 1.1 Skill清单与基本信息

| # | Skill名称 | content.md行数 | skill.json | 版本 | 维护者 |
|---|-----------|---------------|------------|------|--------|
| 1 | oc_collab_bug_management_guide | 727 | ❌ 无 | - | Agent 1 |
| 2 | oc_collab_test_acceptance_guide | 388 | ❌ 无 | - | Agent 1 |
| 3 | oc_collab_development_guide | 329 | ❌ 无 | - | Agent 2 |
| 4 | oc_collab_detailed_design_guide | 387 | ✅ 有 | v1 | Agent 2 |
| 5 | oc_collab_outline_design_guide | 283 | ✅ 有 | v1 | Agent 1 |
| 6 | oc_collab_requirements_guide | 474 | ✅ 有 | v1 | Agent 1 |
| 7 | oc_collab_requirements_review_guide | 181 | ✅ 有 | v1 | Agent 1 |
| 8 | oc_collab_collaboration_guide | 100+ | ✅ 有 | v1.2 | Agent 1 |
| 9 | oc_collab_deployment_guide | 509 | ❌ 无 | - | Agent 2 |

**总计**: 9个Skill
- 有skill.json: 5个
- 无skill.json: 4个

### 1.2 按阶段分类

| 阶段 | 相关Skill | 问题 |
|------|----------|------|
| requirements | oc_collab_requirements_guide | ✅ 有json |
| requirements_review | oc_collab_requirements_review_guide | ✅ 有json |
| outline_design | oc_collab_outline_design_guide | ✅ 有json |
| detailed_design | oc_collab_detailed_design_guide | ✅ 有json |
| development | oc_collab_development_guide | ❌ 无json |
| testing | oc_collab_test_acceptance_guide | ❌ 无json |
| deployment | oc_collab_deployment_guide | ❌ 无json |
| 跨阶段 | oc_collab_bug_management_guide | ❌ 无json |
| 跨阶段 | oc_collab_collaboration_guide | ✅ 有json |

---

## 二、从SOP视角分析现有体系

### 2.1 SOP四要素对比分析

| SOP要素 | 理想状态 | 现状 | 问题 |
|---------|----------|------|------|
| **触发条件** | 明确什么情况下触发 | 部分有 | 4个skill无json，导致触发条件不明确 |
| **操作步骤** | 清晰的步骤指引 | ✅ 都有 | 内容详略不一 |
| **输出产物** | 明确产出物 | 部分有 | 缺失标准化的输出物定义 |
| **验收标准** | 明确如何验收 | 部分有 | 大部分只有检查清单 |

### 2.2 各Skill SOP要素完备性评估

| Skill | 触发条件 | 操作步骤 | 输出产物 | 验收标准 | 综合评分 |
|-------|---------|---------|---------|---------|---------|
| oc_collab_collaboration_guide | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ⭐⭐⭐⭐⭐ |
| oc_collab_requirements_guide | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ⭐⭐⭐⭐⭐ |
| oc_collab_requirements_review_guide | ✅ 完整 | ✅ 完整 | ✅ 完整 | ✅ 完整 | ⭐⭐⭐⭐⭐ |
| oc_collab_outline_design_guide | ⚠️ 基础 | ✅ 完整 | ⚠️ 部分 | ⚠️ 部分 | ⭐⭐⭐ |
| oc_collab_detailed_design_guide | ⚠️ 基础 | ✅ 完整 | ⚠️ 部分 | ⚠️ 部分 | ⭐⭐⭐ |
| oc_collab_development_guide | ❌ 无 | ✅ 完整 | ⚠️ 部分 | ⚠️ 部分 | ⭐⭐ |
| oc_collab_test_acceptance_guide | ❌ 无 | ✅ 完整 | ⚠️ 部分 | ⚠️ 部分 | ⭐⭐ |
| oc_collab_deployment_guide | ❌ 无 | ✅ 完整 | ⚠️ 部分 | ⚠️ 部分 | ⭐⭐ |
| oc_collab_bug_management_guide | ❌ 无 | ✅ 完整 | ⚠️ 部分 | ⚠️ 部分 | ⭐⭐ |

---

## 三、核心问题识别

### 3.1 结构性问题

| 问题类型 | 具体表现 | 影响 |
|----------|----------|------|
| **skill.json缺失** | 4个核心Skill缺少skill.json | Agent无法自动识别触发条件 |
| **skill.json不一致** | 有的完整，有的只有关键词 | 检索和匹配效率低 |
| **内容长度差异大** | 181行 vs 727行 | 查找效率不一致 |
| **版本管理混乱** | 有的标版本v1/v1.2，有的无 | 演进历史不清晰 |

### 3.2 内容问题

| 问题 | 示例 |
|------|------|
| **触发条件不明确** | bug_management_guide没有触发条件，不知道什么时候应该使用 |
| **输出产物定义模糊** | 大部分只有"创建文档"，没有具体模板或格式要求 |
| **验收标准缺失** | 部分只有"检查清单"，没有明确的质量标准 |
| **角色权限不清** | collaboration_guide有完整权限定义，其他Skill引用不统一 |

### 3.3 流程性问题

| 问题 | 表现 |
|------|------|
| **Skill之间引用混乱** | 各Skill互相引用，但引用的内容可能已过时 |
| **跨阶段协作缺失** | 阶段之间的衔接没有明确规范 |
| **文档状态流转** | 已有状态定义，但Skill之间引用不一致 |

---

## 四、重整方案

### 4.1 重整目标

| 目标 | 描述 | 优先级 |
|------|------|--------|
| **标准化** | 所有Skill都有统一的skill.json结构 | P0 |
| **SOP化** | 所有Skill都有完整的四要素 | P0 |
| **可检索** | Agent能快速找到相关Skill | P1 |
| **可演进** | 有清晰的版本管理机制 | P2 |

### 4.2 重整原则

| 原则 | 说明 |
|------|------|
| **最小改动** | 先做标准化，不做内容重构 |
| **渐进式** | 逐个Skill处理，不一次性大改 |
| **可回滚** | 保留原文备份，便于回滚 |
| **可验证** | 每次改动后能验证有效性 |

### 4.3 重整步骤

#### Phase 1: 标准化skill.json（优先级P0）

**目标**: 所有Skill都有完整的skill.json

**步骤**:
1. 为4个缺失的Skill创建skill.json
2. 为2个只有关键词的Skill补充完整skill.json
3. 统一skill.json结构

**统一skill.json结构**:
```json
{
  "id": "oc_collab_xxx_guide",
  "name": "OC-Collab xxx指南",
  "version": "v1.0.0",
  "description": "简短描述",
  "author": "Agent X",
  "created_at": "YYYY-MM-DD",
  "updated_at": "YYYY-MM-DD",
  "tags": ["xxx", "guide"],
  "applicable_phase": "xxx|all",
  "applicable_role": "Agent1|Agent2|All",
  "triggers": [
    {
      "condition": "xxx",
      "priority": "high|medium|low",
      "description": "xxx"
    }
  ],
  "outputs": {
    "documents": ["docs/xx/"],
    "artifacts": ["state/xxx.yaml"]
  },
  "related_skills": [
    "oc_collab_xxx_guide"
  ]
}
```

**缺失skill.json的Skill列表**:
- [ ] oc_collab_bug_management_guide
- [ ] oc_collab_test_acceptance_guide
- [ ] oc_collab_development_guide
- [ ] oc_collab_deployment_guide

**需要补充的Skill列表**:
- [ ] oc_collab_outline_design_guide
- [ ] oc_collab_detailed_design_guide

#### Phase 2: 补充SOP四要素（优先级P1）

**目标**: 所有Skill都有完整的SOP四要素

**在content.md中添加SOP头信息**:

```markdown
# OC-Collab xxx指南

**版本**: v1.0.0
**适用阶段**: xxx
**适用角色**: Agent X

---

## SOP结构概览

| SOP要素 | 内容 |
|---------|------|
| **1. 触发条件** | 见"1. 触发条件"章节 |
| **2. 操作步骤** | 见"2. 操作步骤"章节 |
| **3. 输出产物** | xxx |
| **4. 验收标准** | 见"4. 验收标准"章节 |

---

## 1. 触发条件 ⭐

**什么情况下需要使用本Skill？**

...

## 2. 操作步骤 ⭐

**步骤1: xxx**
...

## 3. 输出产物 ⭐

| 产物 | 位置 | 格式 |
|------|------|------|
| xxx | docs/xx/ | Markdown |

## 4. 验收标准 ⭐

| 标准 | 检查方法 |
|------|----------|
| xxx | xxx |

---
```

#### Phase 3: 统一版本管理（优先级P2）

**目标**: 所有Skill都有清晰的版本历史

**在content.md末尾添加标准版本历史**:

```markdown
---

## 版本历史

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1.0.0 | YYYY-MM-DD | 初始版本 | Agent X |
| v1.0.1 | YYYY-MM-DD | xxx | Agent X |

**维护者**: Agent X
**更新日期**: YYYY-MM-DD
```

### 4.4 重整优先级

| 优先级 | Skill | 工时预估 | 说明 |
|--------|-------|----------|------|
| P0 | oc_collab_bug_management_guide | 1h | 添加skill.json + SOP头 |
| P0 | oc_collab_test_acceptance_guide | 1h | 添加skill.json + SOP头 |
| P0 | oc_collab_development_guide | 1h | 添加skill.json + SOP头 |
| P0 | oc_collab_deployment_guide | 1h | 添加skill.json + SOP头 |
| P1 | oc_collab_outline_design_guide | 0.5h | 补充skill.json |
| P1 | oc_collab_detailed_design_guide | 0.5h | 补充skill.json |
| P2 | 统一版本格式 | 1h | 所有Skill更新版本历史 |

**总工时预估**: 6h

---

## 五、实施计划

### 5.1 实施顺序

1. 先处理P0的4个Skill（缺失skill.json）
2. 再处理P1的2个Skill（补充skill.json）
3. 最后处理P2的统一版本

### 5.2 质量检查清单

每次改动后检查:

- [ ] skill.json语法正确
- [ ] content.md格式统一
- [ ] 引用关系正确
- [ ] 版本历史更新

### 5.3 回滚方案

如果出现问题:
1. 保留原文备份
2. 使用 `git checkout` 恢复
3. 记录问题到docs/00-memos/

---

## 六、待评审事项

请Agent2评审以下事项:

1. **重整方案是否可行？**
   - ✅ 同意
   - ❌ 不同意，需要修改

2. **skill.json统一结构是否合理？**
   - ✅ 同意
   - ❌ 需要调整结构

3. **实施顺序是否正确？**
   - ✅ 同意
   - ❌ 需要调整顺序

4. **工时预估是否合理？**
   - ✅ 同意
   - ❌ 需要重新评估

---

## 七、风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| skill.json格式不兼容 | 低 | 高 | 先在测试环境验证 |
| 内容引用失效 | 中 | 中 | 改动后逐一检查引用 |
| Agent匹配失效 | 低 | 高 | 改动后进行功能测试 |

---

## 关联文档

| 文档 | 路径 | 说明 |
|------|------|------|
| RESEARCH_Skill_Evolution_Management_20260209.md | docs/07-research/RESEARCH_Skill_Evolution_Management_20260209.md | Skill演进路线图（Phase 1的T-SKILL-001/002/003是本方案的基础） |
| PROPOSAL-Agent_Norm_Assistant.md | docs/06-proposals/PROPOSAL-Agent_Norm_Assistant.md | Agent2的智能辅助系统提案（本方案的T-SKILL-006/007/008依赖Agent2提案的实现） |
| MEETING-SOP_Reorganization_Thinking_20260209.md | docs/08-meeting-notes/MEETING-SOP_Reorganization_Thinking_20260209.md | SOP重整思路会议纪要（本方案暂停后重新梳理的思路） |

**本文档与其他文档的关系**：
- 本PROPOSAL是RESEARCH Phase 1（T-SKILL-001/002/003）的具体执行方案
- **当前状态：已暂停**，待RESEARCH评审通过后需要根据会议纪要的思路重新制定
- Agent2的PROPOSAL提供了后续Phase 3的实现能力（切片、检索、嵌入）
- 会议纪要明确了正确的重整思路：SOP边界梳理 → 拆分设计 → 规范化 → CLI工具

**重要提醒**：
- 本方案存在"增量思维"问题（只补json），需要按照会议纪要的思路重新制定
- 正确的思路应该是：先梳理SOP边界，再基于边界拆分，最后规范化

**后续行动**：
1. 等RESEARCH评审通过
2. 根据会议纪要重新制定Skill拆分方案（T-SKILL-001）

---

**创建人**: Agent 1
**日期**: 2026-02-09
**状态**: 已暂停，待RESEARCH评审后更新
