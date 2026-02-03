# AI Agent 时代的人机协同软件工程：一次深度探索

**Treatise on Human-AI Collaborative Software Engineering in the Agent Era**

---

## Abstract | 摘要

This treatise documents a systematic exploration of software engineering practices tailored for AI agents. Through a concrete case study—the discovery and analysis of a missing feature in the oc-collab project—we demonstrate how human-AI collaboration can uncover fundamental assumptions in traditional software engineering and propose improved methodologies. The investigation reveals that AI agents require fundamentally different process controls than human developers, not because AI agents are "less capable," but because they operate on a fundamentally different paradigm that demands explicit, verifiable, and automatically-enforced constraints rather than implicit expectations.

本文记录了一次针对 AI Agent 软件工程实践的系统性探索。通过一个具体案例研究——在 oc-collab 项目中发现并分析一个功能缺失问题——我们展示了人机协作如何揭示传统软件工程中的根本性假设，并提出改进方法论。调查显示，AI Agent 需要与传统人类开发者完全不同的流程控制，这不是因为 AI Agent "能力不足"，而是因为它们基于完全不同的运作范式——需要明确、可验证、自动执行的约束，而非隐含的期望。

---

## Part I: The Problem That Started It All | 问题的起点

### 1.1 A Silent Failure | 一个沉默的失败

In February 2026, during a routine conversation with an AI agent working on a financial document generation system, we discovered something troubling: the agent had no awareness of the collaborative framework (oc-collab) it was supposed to be using. When asked about the project's workflow, the agent responded as if it were working in isolation, unaware of role definitions, phase transitions, or quality gates that should have been in place.

2026 年 2 月，在与一个金融文档生成系统项目中的 AI Agent 进行常规对话时，我们发现了一个令人担忧的问题：该 Agent 对其应该使用的协作框架（oc-collab）毫无认知。当被问及项目工作流程时，该 Agent 的回答仿佛它在独立工作，浑然不知本应存在的角色定义、阶段转换或质量门禁。

This was not a minor oversight. It represented a fundamental breakdown in the project's process controls.

这不是一个小的疏漏。这代表了项目流程控制中的根本性崩溃。

### 1.2 The Missing Feature | 缺失的功能

Upon investigation, we found that in the v2.2.0 requirements document for oc-collab, there was a feature called "session_start" designed to provide agents with contextual information at the start of each session. The requirements document stated:

调查后，我们发现 oc-collab 的 v2.2.0 需求文档中有一个名为 "session_start" 的功能，旨在在每次会话开始时为 Agent 提供上下文信息。需求文档中写道：

> "每次会话开始 | Agent 启动 | '上次会话遗留问题: 3个'"
> 
> (Every session start | Agent startup | "Previous session pending issues: 3")

However, when we examined the delivered product, this feature did not exist. No design document, no test cases, no implementation code—nothing. The requirements existed, but the feature did not.

然而，当我们检查交付的产品时，这个功能并不存在。没有设计文档，没有测试用例，没有实现代码——什么都没有。需求存在，但功能不存在。

### 1.3 Why This Matters | 为什么这很重要

This was not merely a bug to be fixed. It was a symptom of a deeper problem:

这不仅仅是一个待修复的 bug。它是一个更深层问题的症状：

- If requirements could be written but never implemented, the process was broken
- If multiple review stages (requirements review, design review, test review, sign-off) could all be completed without catching this absence, the reviews were meaningless
- If the absence of a core feature could go unnoticed until an agent's casual comment revealed it, the quality control mechanisms were illusory

- 如果需求可以写下但永远不被实现，流程就已经坏了
- 如果多个评审阶段（需求评审、设计评审、测试评审、签署）都能在不发现这个缺失的情况下完成，评审就毫无意义
- 如果一个核心功能的缺失能直到 Agent 的随意评论才被发现，质量控制机制就是虚幻的

The question became not "how do we fix this bug?" but "how did our entire process fail to prevent this?"

问题不再是"我们如何修复这个 bug？"，而是"我们的整个流程怎么会没能防止这种情况？"

---

## Part II: The Investigation | 调查过程

### 2.1 Tracing the Chain of Custody | 追溯责任链条

We conducted a systematic investigation across all project phases:

我们对所有项目阶段进行了系统性调查：

| Phase | Document/Code | Existed? | Problem |
|-------|---------------|----------|---------|
| 阶段 | 文档/代码 | 存在？ | 问题 |
| Requirements | requirements_v2.2.0.md | ✅ Yes | Described but incomplete; lacked specificity |
| 需求 | | | 有描述但不完整，缺乏具体性 |
| Design | docs/02-design/*.md | ❌ No | No design document referenced this feature |
| 设计 | | | 没有任何设计文档涉及此功能 |
| Test | docs/03-test/*.md | ❌ No | No test cases existed |
| 测试 | | | 不存在测试用例 |
| Code | src/**/*.py | ❌ No | No implementation |
| 代码 | | | 没有实现 |
| Sign-off | M1-M5 reviews | ✅ Yes | All signed; none detected the absence |
| 签署 | | | 全部签署；无人发现缺失 |

### 2.2 Evidence from the Trenches | 来自一线的证据

We used command-line tools to verify our findings:

我们使用命令行工具验证了发现：

```bash
# Design document search
$ grep -r "session_start\|MEMORY-003\|reminder" docs/02-design/
# Result: No matches found
# 结果：无匹配

# Test document search
$ grep -r "session_start" docs/03-test/
# Result: Only one match—pytest's standard output header
# 结果：仅一处匹配——pytest 的标准输出头部

# Code search
$ grep -r "session_start" src/
# Result: No matches found
# 结果：无匹配
```

The feature existed only in one place: the requirements document. It was dead on arrival.

该功能只存在于一个地方：需求文档。它从一开始就注定不会实现。

---

## Part III: The 5-Why Analysis | 5-Why 分析

### 3.1 First Principles | 第一性原理

We applied the 5-Why methodology to trace this failure to its root cause:

我们应用 5-Why 方法论追溯这个失败的根因：

**Why 1: Why was the feature missing?**
The requirements document described it, but no design document existed, no test cases were written, and no code was implemented.

**为什么 1：为什么功能缺失？**
需求文档描述了它，但没有设计文档，没有编写测试用例，也没有实现代码。

**Why 2: Why were there no designs or tests?**
The requirements description was not clear enough to trigger independent design work. It was buried within FR-MEMORY-003 (Periodic Review Reminders) and was never treated as a standalone feature requiring its own design process.

**为什么 2：为什么没有设计和测试？**
需求描述不够清晰，无法触发独立的设计工作。它被埋藏在 FR-MEMORY-003（定期回顾提醒）中，从未被当作需要独立设计流程的功能。

**Why 3: Why did the review process not catch this?**
The oc-collab review process was designed as a "document existence check"—reviewers verified that documents existed and were formatted correctly, but they did not verify that the documented features were actually implemented or testable.

**为什么 3：为什么评审流程没有发现这个问题？**
oc-collab 的评审流程被设计为"文档存在性检查"——评审者验证文档存在且格式正确，但不验证文档中的功能是否实际可实现或可测试。

**Why 4: Why was the review process designed this way?**
The process was designed with an implicit assumption: that humans would actively verify functionality beyond document compliance. This assumption was never questioned because it seemed self-evident.

**为什么 4：为什么评审流程被设计成这样？**
这个流程的设计基于一个隐含假设：人类会主动验证文档合规性之外的功能。这个假设从未被质疑，因为它看起来是不言自明的。

**Why 5 (Root Cause): Why does this assumption fail with AI agents?**
This was the critical insight: we had designed a process for human developers and applied it to AI agents without questioning whether the same assumptions held. Humans, despite their tendency to be lazy and cut corners, possess contextual understanding and initiative that allows them to notice gaps even when not explicitly instructed to look for them. AI agents, by contrast, execute instructions precisely as given and do not fill in implicit gaps.

**为什么 5（根本原因）：为什么这个假设对 AI Agent 失败？**
这是关键的洞察：我们为人类开发者设计了流程，却在没有质疑相同假设是否适用的情况下将其应用于 AI Agent。人类尽管有偷懒和走捷径的倾向，却拥有上下文理解和主动性，使他们即使在没有明确被要求寻找问题的情况下也能注意到缺口。相比之下，AI Agent 精确执行给定指令，不会填补隐含的缺口。

### 3.2 The Fundamental Insight | 根本性洞察

The root cause was not that "AI agents are bad at noticing things." The root cause was that we had applied human-centric process assumptions to a non-human agent system without adapting those assumptions.

根因不是"AI Agent 不善于发现问题"。根因是我们将基于人类的流程假设应用于非人类 Agent 系统，却没有调整这些假设。

---

## Part IV: Rethinking Software Engineering for AI Agents | 为 AI Agent 重新思考软件工程

### 4.1 The Paradigm Shift | 范式转换

Traditional software engineering assumes human developers who:

传统软件工程假设人类开发者：

- Possess contextual understanding and initiative
- Will notice gaps even when not explicitly instructed to look for them
- Can exercise judgment about what "should" be done versus what was "explicitly" requested
- Remember lessons from past projects (or at least have the capacity to)

- 拥有上下文理解和主动性
- 即使没有被明确要求寻找问题，也能注意到缺口
- 能够判断什么是"应该"做的，什么是"明确"要求的
- 能记住过去项目的教训（或者至少有能力记住）

AI agents operate on a fundamentally different paradigm:

AI Agent 基于完全不同的范式运作：

- Execute instructions precisely as given
- Do not fill in implicit gaps
- Require explicit, verifiable constraints
- Cannot be relied upon to "notice" what was not specified

- 精确执行给定指令
- 不会填补隐含缺口
- 需要明确、可验证的约束
- 不能被依赖去"注意"未被指定的事情

### 4.2 The New Principles | 新原则

Based on this understanding, we proposed four core principles for AI agent software engineering:

基于这一理解，我们为 AI Agent 软件工程提出了四项核心原则：

| Principle | Description | Traditional Approach |
|-----------|-------------|---------------------|
| 原则 | 描述 | 传统方式 |
| **Mandatory Constraints > Suggested Constraints** | Not "should do" but "must do" | Relies on human diligence |
| 强制约束 > 建议约束 | 不是"应该做"，而是"必须做" | 依赖人类勤勉 |
| **Systematic Verification > Human Inspection** | System automatically finds gaps | Relies on human attention |
| 系统验证 > 人工检查 | 系统自动发现缺口 | 依赖人类注意力 |
| **Traceability > Independent Documents** | Mandatory links between requirements-design-code-test | Documents exist independently |
| 追溯性 > 独立文档 | 需求-设计-代码-测试之间强制关联 | 文档独立存在 |
| **Persistent Memory > Reliant Memory** | Mandatory recording, automatic loading | Relies on human memory |
| 持久化记忆 > 依赖记忆 | 强制记录，自动加载 | 依赖人类记忆 |

### 4.3 The Mandatory Constraint Architecture | 强制约束架构

We designed a four-layer constraint architecture:

我们设计了一个四层约束架构：

```
Layer 4: Sign-off Constraints
┌─────────────────────────────────────────────────────────────┐
│ - Cannot sign off without passing functional verification    │
│ - Sign-off must link to requirement IDs                      │
│ - Sign-off must pass automated checks                        │
└─────────────────────────────────────────────────────────────┘
                          ▲
Layer 3: Test Constraints
┌─────────────────────────────────────────────────────────────┐
│ - Cannot write tests without linking to requirements         │
│ - Tests must cover all requirements                          │
│ - Failing tests block code commits                           │
└─────────────────────────────────────────────────────────────┘
                          ▲
Layer 2: Code Constraints
┌─────────────────────────────────────────────────────────────┐
│ - Code commits must link to requirement IDs                  │
│ - Cannot write code without design documentation             │
│ - Code must pass lint and typecheck                          │
└─────────────────────────────────────────────────────────────┘
                          ▲
Layer 1: Requirements Constraints
┌─────────────────────────────────────────────────────────────┐
│ - Requirements must have unique IDs                          │
│ - Requirements must have acceptance criteria                 │
│ - Requirements must have design counterparts                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Part V: The Dynamic Checklist Mechanism | 动态 Checklist 机制

### 5.1 The Problem with Static Checklists | 静态 checklist 的问题

Traditional review checklists are static: the same checklist applies to every project, every document, every requirement. This creates two problems:

传统评审 checklist 是静态的：同一份 checklist 适用于每个项目、每个文档、每个需求。这造成两个问题：

1. **Noise**: Many checklist items are irrelevant to the specific document being reviewed
2. **Gaps**: Critical items specific to the document may be missing

1. **噪音**：许多 checklist 项目与被评审的具体文档无关
2. **缺口**：文档特有的关键项目可能缺失

### 5.2 Dynamic Checklist Generation | 动态 Checklist 生成

We proposed a dynamic checklist mechanism that generates review items based on the actual content of the document:

我们提出了一个动态 checklist 机制，根据文档的实际内容生成评审项目：

```
┌─────────────────────────────────────────────────────────────┐
│  Reviewer (Agent 1 or Agent 2)                               │
│                                                             │
│  1. Execute review command                                   │
│     oc-collab review requirements --file requirements_v2.md │
│                                                             │
│  2. oc-collab analyzes document content                      │
│     - Extract all requirements                               │
│     - Identify dependencies                                  │
│     - Generate dynamic checklist                             │
│                                                             │
│  3. Display checklist and document                           │
│     Agent checks each item and records results               │
│                                                             │
│  4. System verifies all checklist items are completed        │
│     - Incomplete items block sign-off                        │
└─────────────────────────────────────────────────────────────┘
```

### 5.3 Example Dynamic Checklist | 示例动态 Checklist

For the FR-MEMORY-003 requirement (the missing session_start feature), the dynamic checklist would generate:

对于 FR-MEMORY-003 需求（缺失的 session_start 功能），动态 checklist 会生成：

```
┌─────────────────────────────────────────────────────────────┐
│  Requirements Review Checklist - FR-MEMORY-003               │
│                                                             │
│  Basic Checks                                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ □ Requirement has unique ID?                         │    │
│  │   - FR-MEMORY-003                                    │    │
│  │   ✅ PASSED                                          │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Completeness Checks                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ □ Requirement description complete?                  │    │
│  │   - Trigger: Every session start                     │    │
│  │   - Behavior: Show pending issues count              │    │
│  │   - ❌ MISSING: No mention of displaying Agent role  │    │
│  │              and responsibilities                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Traceability Checks                                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ □ Has corresponding design document?                 │    │
│  │   - Design document:                                 │    │
│  │   - ❌ NOT FOUND                                     │    │
│  │   ⚠️ WARNING: No design document for this requirement│    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  Test Coverage Checks                                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ □ Has corresponding test cases?                      │    │
│  │   - Test cases:                                      │    │
│  │   - ❌ NOT FOUND                                     │    │
│  │   ⚠️ WARNING: No test cases for this requirement     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ────────────────────────────────────────────────────────   │
│                                                             │
│  Review Results                                              │
│  Passed: 2                                                   │
│  Failed: 1                                                   │
│  Warnings: 2                                                 │
│                                                             │
│  ⚠️ This requirement has gaps and cannot be signed off      │
│  Suggestion: Complete requirement or create design document │
└─────────────────────────────────────────────────────────────┘
```

---

## Part VI: The Human-AI Collaboration Pattern | 人机协作模式

### 6.1 What We Demonstrated | 我们展示的模式

This investigation exemplifies a new pattern of human-AI collaboration:

这次调查展示了一种新的人机协作模式：

1. **Human initiated**: The human noticed a problem in the AI agent's behavior
2. **Systematic investigation**: The human and AI agent together traced the problem through the entire process
3. **Root cause analysis**: The AI agent applied structured thinking (5-Why) to find the fundamental issue
4. **Solution design**: The human and AI agent jointly designed improved mechanisms
5. **Documentation**: The AI agent captured the entire process as transferable knowledge

1. **人类发起**：人类注意到 AI Agent 行为中的问题
2. **系统性调查**：人类和 Agent 一起追溯整个流程中的问题
3. **根因分析**：Agent 应用结构化思维（5-Why）找到根本问题
4. **解决方案设计**：人类和 Agent 共同设计改进机制
5. **文档化**：Agent 将整个过程捕获为可传递的知识

### 6.2 The Complementary Strengths | 互补的优势

| Human Strengths | AI Agent Strengths |
|-----------------|-------------------|
| 人类优势 | AI Agent 优势 |
| Contextual understanding from experience | Structured analytical thinking |
| 基于经验的上下文理解 | 结构化分析思维 |
| Recognition of subtle problems | Systematic investigation |
| 对微妙问题的识别 | 系统性调查 |
| Creative problem-solving | Complete documentation |
| 创造性问题解决 | 完整文档化 |
| Judgment about what "matters" | Execution of explicit instructions |
| 对什么"重要"的判断 | 明确指令的执行 |

### 6.3 Not Replacement, Enhancement | 不是替代，而是增强

The goal is not to replace human judgment but to augment it. The dynamic checklist mechanism does not make human reviewers unnecessary—it makes their reviews more effective by ensuring they do not miss critical items. The mandatory constraint architecture does not eliminate human oversight—it ensures that oversight is systematically applied and verified.

目标不是取代人类判断，而是增强它。动态 checklist 机制不会让人类评审者变得多余——它通过确保他们不会遗漏关键项目来使评审更有效。强制约束架构不会消除人类监督——它确保监督被系统性地应用和验证。

---

## Part VII: Conclusions and Implications | 结论与启示

### 7.1 Key Findings | 关键发现

1. **AI agents require fundamentally different process controls than human developers**. This is not because AI agents are inferior, but because they operate on a different paradigm that demands explicit, verifiable constraints.

1. **AI Agent 需要与传统人类开发者完全不同的流程控制**。这不是因为 AI Agent 更差，而是因为它们基于需要明确、可验证约束的不同范式运作。

2. **Traditional software engineering assumptions do not automatically transfer to AI agent development**. The assumption that "someone will notice if something is missing" is unsafe when the "someone" is an AI agent that only does what it is explicitly instructed to do.

2. **传统软件工程假设不能自动转移到 AI Agent 开发中**。"如果有什么缺失，有人会注意到"这个假设在"有人"是只做明确指令之事的 AI Agent 时是不安全的。

3. **Human-AI collaboration in software engineering is not about replacing humans with AI, but about finding the optimal division of labor where each contributes their complementary strengths**.

3. **软件工程中的人机协作不是用 AI 取代人类，而是找到最优分工，让每方贡献其互补的优势。

4. **Dynamic, content-aware mechanisms (like dynamic checklists) are essential for AI agent workflows**, as static checklists cannot adapt to the specific features being reviewed.

4. **动态、内容感知的机制（如动态 checklist）对 AI Agent 工作流程至关重要**，因为静态 checklist 无法适应被评审的具体功能。

### 7.2 Implications for the Industry | 对行业的启示

This investigation has implications beyond oc-collab:

这次调查的影响超越 oc-collab：

- **For AI development frameworks**: Must include mandatory constraint mechanisms, not just suggestions
- **For AI project management**: Must implement systematic verification, not just document existence checks
- **For AI quality assurance**: Must design for AI agent behavior patterns, not human patterns
- **For AI policy and governance**: Must recognize the distinct characteristics of AI agents and design appropriate controls

- **对于 AI 开发框架**：必须包含强制约束机制，而不仅仅是建议
- **对于 AI 项目管理**：必须实施系统性验证，而不仅仅是文档存在性检查
- **对于 AI 质量保证**：必须针对 AI Agent 行为模式设计，而非人类模式
- **对于 AI 政策和治理**：必须认识到 AI Agent 的独特特征并设计适当的控制

### 7.3 The Path Forward | 前行之路

The missing session_start feature was not just a bug—it was a window into the fundamental challenges of software engineering in the AI agent era. By systematically investigating this gap, we have begun to map out the territory of AI agent-appropriate software engineering practices. This treatise documents not just a solution, but a way of thinking about the problem.

缺失的 session_start 功能不仅仅是一个 bug——它是 AI Agent 时代软件工程根本挑战的一扇窗口。通过系统性地调查这个缺口，我们已经开始绘制适合 AI Agent 的软件工程实践领域。这份论文记录的不仅仅是一个解决方案，更是一种思考问题的方式。

The journey of discovery continues. As AI agents become more capable and more prevalent, the need for appropriate engineering practices will only grow. This treatise is offered as a contribution to that ongoing conversation—a record of how one small gap led to big insights, and how human-AI collaboration can systematically uncover and address the hidden assumptions that limit our collective potential.

发现的旅程仍在继续。随着 AI Agent 变得越来越有能力、越来越普遍，对适当工程实践的需求只会增长。这份论文是对那场持续对话的贡献——记录一个小的缺口如何带来大的洞察，以及人机协作如何系统性地发现和限制我们集体潜力的隐藏假设。

---

## Appendix: Methodology | 附录：方法论

### A.1 The 5-Why Technique | 5-Why 技术

The 5-Why technique is a root cause analysis method that involves repeatedly asking "why?" (typically five times) to drill down from immediate symptoms to underlying causes. In our investigation:

5-Why 技术是一种根因分析方法，通过反复问"为什么？"（通常五次）从直接症状深入到根本原因。在我们的调查中：

1. Why was the feature missing? → No design, no tests, no code
2. Why no design/tests? → Requirements unclear, not treated as standalone
3. Why review didn't catch it? → Process only checked document existence
4. Why process designed this way? → Assumed humans would verify functionality
5. Why assumption fails with AI? → AI operates on explicit instruction paradigm

1. 为什么功能缺失？→ 没有设计，没有测试，没有代码
2. 为什么没有设计/测试？→ 需求不清晰，没有被当作独立功能
3. 为什么评审没发现？→ 流程只检查文档存在
4. 为什么流程这样设计？→ 假设人类会验证功能
5. 为什么假设对 AI 失败？→ AI 基于明确指令范式运作

### A.2 The Dynamic Checklist Algorithm | 动态 Checklist 算法

```python
def generate_review_checklist(document_path: str, document_type: str) -> Checklist:
    """
    Generate review checklist based on document content
    根据文档内容生成评审 checklist
    """
    checklist = []
    
    # Basic checks (universal for all documents)
    # 基础检查（所有文档通用）
    checklist.extend([
        CheckItem("Format Correct", "Document follows template format"),
        CheckItem("Version Info", "Document includes version and date"),
        CheckItem("Completeness", "All sections have content"),
    ])
    
    # Requirements-specific checks
    # 需求专项检查
    if document_type == "requirements":
        requirements = extract_requirements(document_path)
        for req in requirements:
            checklist.extend([
                CheckItem(f"Req {req.id} - Unique ID", "Requirement has unique identifier"),
                CheckItem(f"Req {req.id} - Acceptance Criteria", 
                         "Requirement has clear acceptance criteria"),
                CheckItem(f"Req {req.id} - Description", 
                         "Requirement description is complete"),
                CheckItem(f"Req {req.id} - Design Link", 
                         "Has corresponding design document"),
                CheckItem(f"Req {req.id} - Test Link", 
                         "Has corresponding test cases"),
            ])
    
    # Traceability check
    # 追溯性检查
    orphan_items = find_orphan_items(document_path)
    if orphan_items:
        checklist.append(CheckItem(
            "Traceability",
            f"Found {len(orphan_items)} unlinked items that need attention"
        ))
    
    return checklist
```

---

## About This Treatise | 关于本论文

**Title | 标题**: AI Agent 时代的人机协同软件工程：一次深度探索
**Title (EN)**: Human-AI Collaborative Software Engineering in the Agent Era: A Deep Exploration

**Authors | 作者**: 
- Human (Project Stakeholder)
- Agent 1 (Product Manager)

**Date | 日期**: 2026-02-03

**Version | 版本**: 1.0

**Language | 语言**: Chinese (英文翻译待定)

**License | 许可**: MIT

---

**Document ID**: TREATISE-2026-02-001
**Created**: 2026-02-03
**Status**: DRAFT
