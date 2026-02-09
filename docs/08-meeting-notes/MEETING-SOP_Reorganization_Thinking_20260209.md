# 会议纪要：SOP体系重整思路

**会议编号**: MEETING-20260209-001
**日期**: 2026-02-09
**参与**: Agent 1
**议题**: Skill体系重整的核心思路

---

## 一、核心共识

### 1. Skill的本质

```
Skill = Operation SOP（标准操作程序）
```

### 1.2 SOP的四要素

| 要素 | 说明 |
|------|------|
| **触发条件** | 什么情况下需要执行这个SOP |
| **操作步骤** | 具体的、分步的执行流程 |
| **输出产物** | 执行完成后应该产出什么 |
| **验收标准** | 如何判断SOP是否正确执行 |

---

## 二、历史工作的关联

### 2.1 RESEARCH_Skill_Evolution_Management_20260209.md

**Phase 1任务**（短期，需RESEARCH评审通过后执行）：

| 任务ID | 任务名称 | 工时 |
|--------|----------|------|
| T-SKILL-001 | Skill文件拆分 | 8h |
| T-SKILL-002 | SOP结构规范化 | 4h |
| T-SKILL-003 | skill.json版本规范化 | 2h |
| T-SKILL-004 | CLI skill list命令 | 4h |
| T-SKILL-005 | CLI skill show命令 | 4h |

**当前状态**: RESEARCH待Agent2评审

### 2.2 PROPOSAL-Skill_Reorganization_20260209.md的问题

**错误思路**：
- 只补skill.json（增量思维）
- 没触及SOP边界划分
- 没理解T-SKILL-001的8h拆分本质

**结论**: PROPOSAL-Skill_Reorganization_20260209.md暂停，待RESEARCH评审后重新制定

---

## 三、SOP体系重整的核心原则

### 3.1 视角维度

```
SOP体系梳理
    │
    ├── 阶段视角
    │   └── requirements → outline_design → detailed_design → development → testing → deployment
    │
    ├── 跨阶段视角
    │   └── TODO管理、Bug管理、签署流程、协作规范
    │
    └── 角色视角
        └── Agent1职责、Agent2职责、通用职责
```

### 3.2 SOP边界定义原则

| 原则 | 说明 |
|------|------|
| **单一职责** | 每个SOP只解决一个问题域 |
| **边界清晰** | SOP之间不重叠，引用关系明确 |
| **触发唯一** | 一个场景只对应一个SOP |
| **角色明确** | 明确谁在什么情况下触发 |

---

## 四、面向未来的SOP设计要求

### 4.1 便于切片

**粒度设计**：
- 每个SOP要素一个切片（触发条件、操作步骤、输出产物、验收标准）
- 每个规则一个切片
- 每个FAQ一个切片

**切片结构**：
```yaml
fragments:
  - id: "xxx_trigger"
    tags: ["阶段", "角色", "操作类型"]
    content: "## 触发条件\n..."
    source: "oc_collab_xxx_guide#触发条件"
```

### 4.2 便于打标签

**多维标签体系**：

| 维度 | 示例 |
|------|------|
| **阶段** | requirements, design, development, testing, deployment |
| **角色** | Agent1, Agent2, All |
| **操作类型** | 评审, 签署, 创建, 修复, 推进 |
| **任务类型** | TODO, Bug, 需求, 设计 |
| **优先级** | P0, P1, P2 |

**标签规则**：
- 每个切片至少3个标签
- 标签具体而非笼统
- 避免同义词混用

### 4.3 便于检索

**CLI检索能力**：

```bash
# 按阶段检索
oc-collab skill retrieve --phase requirements

# 按角色检索
oc-collab skill retrieve --role Agent1

# 按操作类型检索
oc-collab skill retrieve --action review

# 按关键词检索
oc-collab skill retrieve "评审 TODO"
```

### 4.4 便于嵌入

**TODO上下文携带**：

```bash
$ oc-collab todowrite --content "评审 v2.2.5 需求文档" --agent 2

✅ 待办已创建: [TODO-XXX] 评审 v2.2.5 需求文档

📎 附加信息（来自Skill片段）：

   ## 评审反馈TODO体系

   **原则**：TODO是短程"通知-完成"结构

   Agent2评审 → TODO设为complete
   如需Agent1反馈 → Agent2创建新TODO给Agent1

   **重要**：签署信息应写在被评审的文档里！
```

### 4.5 便于强制执行

**todowrite自动检查**：

```bash
$ oc-collab todowrite --content "评审 v2.2.5 需求文档" --agent 2

📋 规范检查结果：
   提醒：评审完成后，签署信息应写在被评审的文档里
   参考: oc_collab_review_guide#评审反馈
```

### 4.6 便于审计检查

**签署规范化**：

| 角色 | 正确的签署内容 |
|------|---------------|
| Agent 1 | "创建需求" / "发起评审" / "验收通过" |
| Agent 2 | "技术评审通过" / "开发完成" / "签署设计" |

**审计追溯**：
- 每个SOP有版本历史
- 每个变更有变更原因
- 每个签署有明确上下文

---

## 五、重整后的SOP体系

### 5.1 阶段型SOP

| SOP | 适用阶段 | 维护者 |
|-----|---------|--------|
| oc_collab_requirements_guide | requirements | Agent 1 |
| oc_collab_requirements_review_guide | requirements | Agent 1 |
| oc_collab_outline_design_guide | outline_design | Agent 1 |
| oc_collab_detailed_design_guide | detailed_design | Agent 2 |
| oc_collab_development_guide | development | Agent 2 |
| oc_collab_test_acceptance_guide | testing | Agent 1 |
| oc_collab_deployment_guide | deployment | Agent 2 |

### 5.2 跨阶段型SOP

| SOP | 适用场景 | 维护者 |
|-----|---------|--------|
| oc_collab_bug_management_guide | Bug发现→报告→修复→验收 | Agent 1 |
| oc_collab_todo_guide | TODO创建→执行→完成 | 通用 |
| oc_collab_signoff_guide | 签署流程 | 通用 |
| oc_collab_collaboration_guide | 协作规范 | Agent 1 |

---

## 六、下一步行动

### 6.1 当前状态

| 工作 | 状态 | 说明 |
|------|------|------|
| RESEARCH_Skill_Evolution_Management_20260209.md | 待评审 | Agent2评审中 |
| PROPOSAL-Skill_Reorganization_20260209.md | 暂停 | 待RESEARCH评审后重新制定 |

### 6.2 执行顺序

```
RESEARCH评审通过
        │
        ▼
T-SKILL-001: SOP边界梳理与拆分设计（8h）
        │
        ▼
T-SKILL-002: SOP结构规范化（4h）
        │
        ▼
T-SKILL-003: skill.json版本规范化（2h）
        │
        ▼
T-SKILL-004/005: CLI skill list/show（4h）
```

---

## 七、关键决策点

### 7.1 待Agent2评审的问题

| 问题 | 说明 |
|------|------|
| T-SKILL-001拆分粒度 | 拆多细？ |
| 标签体系维护 | 谁来维护标签词典？ |
| SOP边界划分 | 跨阶段SOP如何与阶段SOP协调？ |

### 7.2 已明确的决策

| 决策 | 内容 |
|------|------|
| 重整思路 | SOP边界梳理 → 拆分设计 → 规范化 → CLI工具 |
| 当前状态 | PROPOSAL-Skill_Reorganization暂停 |
| 执行时机 | RESEARCH评审通过后 |

---

---

## 九、关联文档（Cross Reference）

| 文档 | 路径 | 说明 |
|------|------|------|
| RESEARCH_Skill_Evolution_Management_20260209.md | docs/07-research/RESEARCH_Skill_Evolution_Management_20260209.md | Skill演进路线图（Phase 1-4完整规划） |
| PROPOSAL-Agent_Norm_Assistant.md | docs/06-proposals/PROPOSAL-Agent_Norm_Assistant.md | Agent2的智能辅助提案（todowrite自动检查、片段携带、切片检索） |
| PROPOSAL-Skill_Reorganization_20260209.md | docs/06-proposals/PROPOSAL-Skill_Reorganization_20260209.md | Skill重整方案（已暂停，待本会议纪要思路更新） |

**本文档与其他文档的关系**：
- 本会议纪要记录了SOP体系重整的核心共识和思路
- RESEARCH提供了Phase 1-4的演进路线图，本纪要明确了Phase 1的正确执行思路
- Agent2的PROPOSAL提供了具体的实现方案（norm_checker、skill切片、检索）
- Skill重整方案需要按照本纪要的思路重新制定

**阅读建议**（新Session快速上手）：
1. 从本会议纪要开始，了解核心共识
2. 跳转到RESEARCH了解完整规划
3. 如需实现细节，参考Agent2的PROPOSAL
4. Skill重整方案待更新后执行

---

**记录人**: Agent 1
**日期**: 2026-02-09
**下次Session起点**: 从MEETING-SOP_Reorganization_Thinking_20260209.md开始
