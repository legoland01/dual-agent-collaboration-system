# Research Note: Skill体系演进与应用管理策略

**文档编号**: RESEARCH-20260209-001
**版本**: v1
**日期**: 2026-02-09
**作者**: Agent 1 (产品经理)
**状态**: DRAFT → 待评审

---

## 一、研究背景与问题定义

### 1.1 当前Skill体系面临的挑战

oc-collab的Skill系统是协作规范的载体，但在实际使用中暴露出以下问题：

| 问题分类 | 具体表现 | 影响 |
|----------|----------|------|
| **Agent行为问题** | Agent行动前不读Skill，惯性操作 | 违反协作规范，增加沟通成本 |
| **TODO管理问题** | TODO信息不完整，缺少上下文 | 执行人遗漏关键规范 |
| **检索效率问题** | Skill文档过长（collaboration_guide约630行），难以快速定位 | 降低协作效率，增加出错概率 |
| **体系管理问题** | Skill文件臃肿，更新频繁但缺乏版本管理 | 难以追溯变更，难以评估影响 |

### 1.2 核心洞察

**Skill的本质是什么？**

```
Skill = Operation SOP（标准操作程序）
```

SOP的核心特征：
- **触发条件**：什么情况下触发
- **操作步骤**：具体的执行流程
- **输出产物**：完成后应该产出什么
- **验收标准**：如何判断是否完成

**这个认知对Skill演进至关重要**——我们不是在写"文档"，而是在写"可执行的操作规范"。

### 1.3 Agent2提案的核心思路

Agent 2在`PROPOSAL-Agent_Norm_Assistant.md`中提出了三个关键改进方向：

1. **todowrite自动检查**：根据操作类型匹配规范，提醒相关规则
2. **TODO上下文携带**：嵌入相关Skill片段，减少信息不对称
3. **Skill切片检索**：预切片+标签化，支持快速检索

**这些思路与SOP体系高度契合**，可以作为Skill演进的重要参考。

---

## 二、SOP体系设计原则

### 2.1 SOP的核心要素

```
SOP结构
│
├── 1. 触发条件
│   └── 什么情况下需要执行这个SOP
│
├── 2. 操作步骤
│   └── 具体的、分步的执行流程
│
├── 3. 输出产物
│   └── 执行完成后应该产出什么
│
└── 4. 验收标准
    └── 如何判断SOP是否正确执行
```

### 2.2 Skill与SOP的对应关系

| SOP要素 | Skill对应 | 当前问题 |
|---------|-----------|----------|
| 触发条件 | Skill的适用场景描述 | 场景描述不清晰 |
| 操作步骤 | Skill的流程说明 | 步骤混杂，缺乏结构 |
| 输出产物 | Skill的预期产出 | 预期产出不明确 |
| 验收标准 | Skill的检查清单 | 验收标准缺失或不完整 |

### 2.3 SOP版本化管理原则

| 维度 | 说明 |
|------|------|
| **版本号** | 主版本.次版本.修订号 |
| **变更日志** | 记录每次变更的内容和原因 |
| **兼容性** | 评估变更对现有流程的影响 |
| **回滚机制** | 变更出现问题时的回滚方案 |

---

## 三、Skill体系现状分析

### 3.1 当前Skill文件清单

| Skill文件 | 大小 | 行数 | 主要内容 |
|-----------|------|------|----------|
| oc_collab_collaboration_guide | 19KB | ~630行 | 协作流程、阶段规范 |
| oc_collab_bug_management_guide | 15KB | ~500行 | Bug处理流程 |
| oc_collab_requirements_guide | 13KB | ~460行 | 需求分析、文档规范 |
| oc_collab_deployment_guide | 12KB | ~484行 | 部署发布流程 |
| oc_collab_test_acceptance_guide | 9KB | ~388行 | 测试验收规范 |
| oc_collab_detailed_design_guide | 8KB | ~320行 | 详细设计规范 |
| oc_collab_development_guide | 8KB | ~329行 | 开发规范 |
| oc_collab_outline_design_guide | 6KB | ~200行 | 概要设计规范 |
| oc_collab_requirements_review_guide | 4KB | ~181行 | 需求评审规范 |

### 3.2 存在的问题

| 问题 | 具体表现 | 根因分析 |
|------|----------|----------|
| **文件过大** | collaboration_guide超过630行 | 持续往里塞内容，缺乏拆分 |
| **内容混杂** | 多个主题挤在一个文件 | 没有清晰的模块划分 |
| **检索困难** | 长文档难以快速定位 | 缺乏索引和标签机制 |
| **版本不清** | skill.json版本号更新不一致 | 缺乏版本管理规范 |
| **Agent找不到** | Agent不知道何时读Skill | 缺少触发机制 |

### 3.3 与Agent2提案的对应关系

| Agent2提案 | 对应问题 | 解决思路 |
|------------|----------|----------|
| todowrite自动检查 | Agent找不到Skill | 在行动点自动提醒 |
| TODO上下文携带 | 上下文信息缺失 | 嵌入Skill片段 |
| Skill切片检索 | 长文档难以检索 | 预切片+标签化 |

---

## 四、Skill体系演进方案

### 4.1 演进路线图

```
┌─────────────────────────────────────────────────────────────────┐
│                     Skill体系演进路线图                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: 基础梳理（短期）                                      │
│  ├── 1.1 Skill文件拆分                                         │
│  ├── 1.2 SOP结构规范化                                         │
│  └── 1.3 强制查找机制                                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 2: 检索增强（短期）                                      │
│  ├── 2.1 Skill预切片                                           │
│  ├── 2.2 标签化机制                                            │
│  └── 2.3 CLI检索命令                                           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 3: 智能辅助（中期）                                      │
│  ├── 3.1 todowrite自动检查                                      │
│  ├── 3.2 TODO上下文携带                                        │
│  └── 3.3 规范化提醒系统                                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 4: 多项目适配（长期）                                    │
│  ├── 4.1 标准Skill + 项目层                                     │
│  ├── 4.2 Skill下发机制                                         │
│  └── 4.3 最佳实践共享                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Phase 1: 基础梳理（短期任务）

#### 4.2.1 Skill文件拆分方案

**原则**：按**阶段**和**角色**进行拆分

| 原文件 | 拆分后 | 说明 |
|--------|--------|------|
| oc_collab_collaboration_guide | oc_collab_phase_guide | 阶段推进规范 |
| | oc_collab_signoff_guide | 签署流程规范 |
| | oc_collab_todo_guide | TODO管理规范 |
| | oc_collab_agent_guide | Agent角色规范 |
| oc_collab_requirements_guide | oc_collab_analysis_guide | 需求分析 |
| | oc_collab_requirements_doc_guide | 需求文档规范 |

**拆分后的结构**：
```
skills/
├── oc_collab_phase_guide/
│   ├── skill.json
│   └── content.md
├── oc_collab_signoff_guide/
│   ├── skill.json
│   └── content.md
├── oc_collab_todo_guide/
│   ├── skill.json
│   └── content.md
├── oc_collab_agent_guide/
│   ├── skill.json
│   └── content.md
└── oc_collab_analysis_guide/
    ├── skill.json
    └── content.md
```

#### 4.2.2 SOP结构规范化

**每个Skill必须包含的结构**：

```markdown
# Skill名称

**版本**: v1.0.0
**适用阶段**: [阶段]
**适用角色**: [Agent1/Agent2/通用]

---

## 1. 触发条件

什么情况下需要执行这个SOP？

## 2. 操作步骤

具体的执行流程（编号列表）

## 3. 输出产物

执行完成后应该产出什么

## 4. 验收标准

如何判断SOP是否正确执行（检查清单）

## 5. 常见问题

FAQ或注意事项

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0.0 | 2026-02-09 | 初始版本 |
```

#### 4.2.3 强制查找机制

**目标**：确保Agent在关键行动点自动查找Skill

**关键行动点**：

| 行动点 | 应该查找的Skill |
|--------|------------------|
| 创建TODO | oc_collab_todo_guide |
| 评审文档 | oc_collab_review_guide |
| 签署确认 | oc_collab_signoff_guide |
| 推进阶段 | oc_collab_phase_guide |

**实现方式**：

```
方案A：CLI命令增强
每次执行关键命令时，自动显示相关Skill摘要

方案B：Skill加载优化
在相关CLI命令中嵌入Skill片段

方案C：提醒式检查（Agent2提案思路）
todowrite时检查内容，自动提醒相关规范
```

### 4.3 Phase 2: 检索增强（短期任务）

#### 4.3.1 Skill预切片

**概念**：将长Skill拆分为独立的、可检索的片段

**切片粒度**：
- 每个SOP元素一个切片（触发条件、操作步骤、输出、验收）
- 每个FAQ一个切片
- 每个规则一个切片

**切片结构**：
```yaml
fragments:
  - id: "phase_advance_trigger"
    tags: ["阶段推进", "触发条件", "何时推进"]
    content: |
      ## 触发条件
      
      以下条件全部满足时，才能推进阶段：
      - [ ] 当前阶段所有任务完成
      - [ ] 当前阶段签署完成
      - [ ] 下阶段准备工作完成
    source: "oc_collab_phase_guide#触发条件"
  
  - id: "phase_advance_steps"
    tags: ["阶段推进", "操作步骤", "如何推进"]
    content: |
      ## 操作步骤
      
      1. 检查当前阶段状态
      2. 确认下阶段准备完成
      3. 执行推进命令
      4. 验证推进结果
    source: "oc_collab_phase_guide#操作步骤"
```

#### 4.3.2 标签化机制

**多维标签体系**：

| 标签维度 | 示例 |
|----------|------|
| **阶段** | 需求、设计、开发、测试、部署 |
| **角色** | Agent1、Agent2、通用 |
| **操作类型** | 评审、签署、创建、修复、推进 |
| **任务类型** | TODO、Bug、需求、设计 |
| **优先级** | P0、P1、P2 |

**标签使用规则**：
- 每个切片至少3个标签
- 标签应该具体而非笼统
- 避免同义词混用

#### 4.3.3 CLI检索命令

**命令设计**：

```bash
# 检索命令
oc-collab skill retrieve "阶段推进"
oc-collab skill retrieve "评审 TODO"
oc-collab skill retrieve "签署 规范"

# 查看Skill列表
oc-collab skill list

# 查看特定Skill
oc-collab skill show oc_collab_phase_guide

# 查看Skill变更历史
oc-collab skill history oc_collab_phase_guide
```

### 4.4 Phase 3: 智能辅助（中期任务）

#### 4.4.1 todowrite自动检查（Agent2提案实现）

**功能**：创建TODO时，根据内容自动检查相关规范

**实现思路**：

```python
# 伪代码
def todowrite_check(content: str) -> dict:
    """
    根据TODO内容自动检查相关规范
    """
    rules = {
        "评审": {
            "reminder": "评审完成后，签署信息应写在被评审的文档里",
            "skill_ref": "oc_collab_review_guide#评审反馈"
        },
        "修复": {
            "check": has_bug_report(content),
            "reminder": "修复前请确认已创建Bug报告",
            "skill_ref": "oc_collab_bug_guide#修复流程"
        },
        "签署": {
            "check": has_signoff_target(content),
            "reminder": "签署前请确认已完成实质性变更",
            "skill_ref": "oc_collab_signoff_guide#签署规范"
        }
    }
    
    for keyword, rule in rules.items():
        if keyword in content:
            return rule
    
    return {
        "reminder": "请确认TODO内容清晰",
        "skill_ref": None
    }
```

**输出示例**：

```bash
$ oc-collab todowrite --content "评审 v2.2.5 需求文档" --agent 2

📋 规范检查结果:
   提醒：评审完成后，签署信息应写在被评审的文档里
   参考: oc_collab_review_guide#评审反馈

✅ 待办已创建: [TODO-XXX] 评审 v2.2.5 需求文档
```

#### 4.4.2 TODO上下文携带（Agent2提案实现）

**功能**：创建TODO时，自动嵌入相关Skill片段

**实现思路**：

```yaml
# state/skill_fragments.yaml
fragments:
  - id: "review_signoff"
    tags: ["评审", "签署", "TODO"]
    content: |
      ## 评审反馈TODO体系
      
      **原则**：TODO是短程"通知-完成"结构
      
      Agent2评审 → TODO设为complete
      如需Agent1反馈 → Agent2创建新TODO给Agent1
      
      **重要**：签署信息应写在被评审的文档里！
```

**嵌入效果**：

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

#### 4.4.3 规范化提醒系统

**功能**：在关键节点主动提醒相关规范

**提醒节点**：

| 节点 | 提醒内容 |
|------|----------|
| 创建TODO时 | 相关操作规范 |
| 评审前 | 评审检查清单 |
| 签署前 | 签署条件检查 |
| 推进阶段前 | 阶段推进条件 |

### 4.5 Phase 4: 多项目适配（长期任务）

#### 4.5.1 标准Skill + 项目层

**架构设计**：

```
Skill体系
│
├── 标准Skill（oc-collab核心团队维护）
│   ├── oc_collab_phase_guide/    # 阶段规范
│   ├── oc_collab_todo_guide/     # TODO规范
│   ├── oc_collab_signoff_guide/  # 签署规范
│   └── ...                        # 其他标准规范
│
└── 项目Skill（各项目自定义）
    ├── project-alpha/
    │   └── custom_phase_guide/   # 项目特定规范
    ├── project-beta/
    └── ...
```

**优先级规则**：
1. 项目Skill覆盖标准Skill（项目特定规则优先）
2. 项目Skill未定义的，使用标准Skill
3. 项目Skill的标签体系应兼容标准体系

#### 4.5.2 Skill下发机制

**需求**：标准Skill更新后，自动同步到各项目

**实现思路**：

```
┌─────────────────────┐
│ 标准Skill更新       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 版本比对            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 生成差异报告         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 项目维护者确认       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 下发到各项目         │
└─────────────────────┘
```

**实现方式**：
- Git submodule方式
- 或者统一的Skill同步命令
- 或者CI/CD自动同步

#### 4.5.3 最佳实践共享

**需求**：项目间的经验如何共享

**方案**：

```
┌─────────────────────────────┐
│ 项目特定Skill最佳实践       │
│ (project-alpha/skill/)   │
└─────────────┬─────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 项目特定改进提案           │
│ (docs/06-proposals/)     │
└─────────────┬─────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 评估是否纳入标准Skill     │
│ (oc-collab核心团队)      │
└─────────────┬─────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 纳入标准Skill后同步下发    │
└─────────────────────────────┘
```

**流程**：
1. 项目发现好的实践 → 整理成项目特定Skill
2. 效果验证 → 形成改进提案
3. 评审通过 → 纳入标准Skill
4. 更新发布 → 同步到各项目

---

## 五、任务分解与优先级

### 5.1 短期任务（v2.2.x完成）

| 任务ID | 任务名称 | 工时 | 产出 | 依赖 |
|--------|----------|------|------|------|
| T-SKILL-001 | Skill文件拆分 | 8h | 6个子Skill | - |
| T-SKILL-002 | SOP结构规范化 | 4h | 规范化模板 | T-SKILL-001 |
| T-SKILL-003 | skill.json版本规范化 | 2h | 版本规范 | - |
| T-SKILL-004 | CLI skill list命令 | 4h | skill list命令 | - |
| T-SKILL-005 | CLI skill show命令 | 4h | skill show命令 | - |

**合计工时**：22h

### 5.2 中期任务（v3.0完成）

| 任务ID | 任务名称 | 工时 | 产出 | 依赖 |
|--------|----------|------|------|------|
| T-SKILL-006 | Skill预切片 | 8h | skill_fragments.yaml | T-SKILL-001 |
| T-SKILL-007 | 标签化机制 | 4h | 标签规范 + 标注工具 | T-SKILL-006 |
| T-SKILL-008 | todowrite自动检查 | 8h | norm_checker模块 | T-SKILL-007 |
| T-SKILL-009 | TODO上下文携带 | 8h | 片段嵌入模块 | T-SKILL-006 |
| T-SKILL-010 | CLI skill retrieve | 6h | retrieve命令 | T-SKILL-007 |

**合计工时**：34h

### 5.3 长期任务（待定）

| 任务ID | 任务名称 | 工时 | 产出 | 备注 |
|--------|----------|------|------|------|
| T-SKILL-011 | 多项目适配框架 | 16h | 项目层架构设计 | 需要架构评审 |
| T-SKILL-012 | Skill下发机制 | 12h | 同步命令/CI | 需要CI/CD支持 |
| T-SKILL-013 | 最佳实践共享流程 | 8h | 共享机制设计 | 需要社区协作 |

**合计工时**：36h

### 5.4 任务依赖关系图

```
短期任务
├── T-SKILL-001: Skill文件拆分 ──┬── T-SKILL-002: SOP结构规范化
│                                └── T-SKILL-003: skill.json版本规范化
├── T-SKILL-004: CLI skill list ──┤
└── T-SKILL-005: CLI skill show ─┘

中期任务
├── T-SKILL-006: Skill预切片 ──┬── T-SKILL-007: 标签化机制 ──┬── T-SKILL-008: todowrite自动检查
│                                │                              └── T-SKILL-010: CLI skill retrieve
│                                └── T-SKILL-009: TODO上下文携带
│
└── T-SKILL-011: 多项目适配框架（长期）

长期任务
├── T-SKILL-012: Skill下发机制
└── T-SKILL-013: 最佳实践共享流程
```

---

## 六、与Agent2提案的融合

### 6.1 融合点

| Agent2提案 | 对应Skill演进任务 | 融合方式 |
|------------|------------------|----------|
| todowrite自动检查 | T-SKILL-008 | 实现norm_checker |
| TODO上下文携带 | T-SKILL-009 | 实现片段嵌入 |
| Skill切片检索 | T-SKILL-010 | 实现retrieve命令 |
| 规则引擎 | T-SKILL-008 | 复用norm_checker |
| Skill片段存储 | T-SKILL-006 | 预切片 + fragments.yaml |

### 6.2 复用Agent2的设计

**复用内容**：

```python
# Agent2提案中的设计
class NormChecker:
    RULES = {
        "评审": {...},
        "修复": {...},
        "签署": {...}
    }
    
    def check(self, content: str) -> dict:
        ...

# Skill演进中的实现
class SkillNormChecker(NormChecker):
    # 扩展：支持Skill片段嵌入
    def embed_fragments(self, content: str) -> list[dict]:
        ...
```

---

## 七、风险与应对

### 7.1 短期风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Skill拆分导致碎片化 | Agent更难找到完整流程 | 提供统一索引和导航 |
| Agent不适应新CLI | 学习成本 | 提供迁移指南和过渡期 |
| 标签体系混乱 | 检索不准确 | 制定严格的标签规范 |

### 7.2 中长期风险

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 多项目适配复杂 | 维护成本高 | 保持简单，避免过度设计 |
| Skill同步冲突 | 项目间不一致 | 明确的优先级规则 |
| 最佳实践淹没 | 难以识别有价值的内容 | 评审机制 |

---

## 八、参考文档

| 文档 | 说明 |
|------|------|
| `PROPOSAL-Agent_Norm_Assistant.md` | Agent2的智能辅助系统提案 |
| `skills/*/skill.json` | 当前Skill的元数据 |
| `skills/*/content.md` | 当前Skill的内容 |
| `state/skill_*.yaml` | 可能的片段存储文件 |

---

## 九、开放问题

| 问题 | 说明 | 需要讨论 |
|------|------|----------|
| Skill拆分粒度 | 拆多细？ | 是 |
| 标签体系 | 谁来维护标签词典？ | 是 |
| 多项目架构 | 项目层放在哪里？ | 否（待定） |
| Skill下发时机 | 自动还是手动？ | 否（待定） |

---

## 十、结论与建议

### 10.1 核心结论

1. **Skill本质是SOP**——所有演进应该围绕"可执行的操作规范"展开

2. **Agent2提案高度契合**——todowrite自动检查、片段携带、切片检索都是Skill演进的关键能力

3. **短期聚焦基础**——拆分、规范化、CLI工具，为中长期打基础

4. **长期需要架构设计**——多项目适配是重要但复杂的需求

### 10.2 建议的下一步

| 步骤 | 行动 | 产出 |
|------|------|------|
| 1 | 评审本文档 | 确定演进方向 |
| 2 | 执行T-SKILL-001 | Skill文件拆分 |
| 3 | 执行T-SKILL-002 | SOP结构规范化 |
| 4 | 执行T-SKILL-004/005 | CLI skill list/show |
| 5 | 评审Agent2提案 | 确定智能辅助实现方案 |

---

## 关联文档

| 文档 | 路径 | 说明 |
|------|------|------|
| RESEARCH_Skill_Evolution_Management_20260209.md | docs/07-research/RESEARCH_Skill_Evolution_Management_20260209.md | Skill演进路线图（Phase 1-4规划） |
| PROPOSAL-Agent_Norm_Assistant.md | docs/06-proposals/PROPOSAL-Agent_Norm_Assistant.md | Agent2的智能辅助系统提案（todowrite自动检查、片段携带、切片检索） |
| PROPOSAL-Skill_Reorganization_20260209.md | docs/06-proposals/PROPOSAL-Skill_Reorganization_20260209.md | Skill重整方案（已暂停，待RESEARCH评审后更新） |
| MEETING-SOP_Reorganization_Thinking_20260209.md | docs/08-meeting-notes/MEETING-SOP_Reorganization_Thinking_20260209.md | SOP重整思路会议纪要（核心共识、面向未来的SOP设计要求） |

**本文档与其他文档的关系**：
- 本RESEARCH是SOP体系演进的总规划，包含Phase 1-4的完整路线图
- Agent2的PROPOSAL提供了具体的实现方案（norm_checker、skill切片、检索）
- Skill重整方案是RESEARCH Phase 1的具体执行方案（已暂停）
- 会议纪要记录了重整思路的讨论共识

**阅读建议**：
1. 先读RESEARCH了解整体规划
2. 再读会议纪要理解核心思路
3. 如需实现细节，参考Agent2的PROPOSAL
4. 重整方案待RESEARCH评审后更新

---

**创建人**: Agent 1
**日期**: 2026-02-09
**状态**: DRAFT
