# 改进提案：v2.2.1 开发过程问题分析与解决方案

**提案ID**: PROPOSAL-2026-02-001
**版本**: v2
**日期**: 2026-02-07
**作者**: Agent 2 (开发负责人)
**状态**: DRAFT

---

## 1. 问题罗列

### 1.1 任务同步问题

| # | 问题描述 | 现象 |
|---|----------|------|
| P1 | 内存与文件状态不一致 | `todowrite` 工具更新了内存中的 todo list，但未同步到 `state/agent_adhoc_todos.yaml` 文件 |
| P2 | 任务状态重复标记 | Agent 1 已完成设计评审，但 TODO-008 状态仍显示 pending |
| P3 | 任务依赖不清晰 | TODO-022 依赖 TODO-021，但缺乏系统强制校验 |

### 1.2 代码实现问题

| # | 问题描述 | 现象 |
|---|----------|------|
| P4 | 文件结构损坏 | 使用 `edit` 工具修改复杂代码时，导致代码块错位（如 `change_compliance.py`） |
| P5 | 缺少必要导入 | `test_extended_checklist.py` 运行时缺少 `yaml` 模块 |
| P6 | 单元测试缺失 | `signoff.py` 初始覆盖率仅 69%，缺少拒签、摘要、检查等关键路径测试 |

### 1.3 流程合规问题

| # | 问题描述 | 现象 |
|---|----------|------|
| P7 | 职责边界违规 | Agent 2 评审了设计文档，违反职责分工（Agent 1 负责评审） |
| P8 | 文档版本混乱 | v2.2.1 存在多个需求版本（`_DRAFT.md`, `_READY.md`, `_PATCH_001.md`, `_PATCH_002.md`） |

### 1.4 评审能力问题（核心）

| # | 问题描述 | 现象 | 根因 |
|---|----------|------|------|
| **P9** | **M5 需求遗漏** | Agent 2 在需求评审时没有发现 M5 定义不完整，但设计阶段却能完整实现 M5 | **评审流于形式，只"确认"不"质疑"** |
| P9-1 | 确认式评审 | Agent 只检查"文档存在"、"格式正确"，不验证"需求完整" | 缺少深度评审机制 |
| P9-2 | 任务驱动而非需求驱动 | Agent 等待任务布置才知道做什么，缺乏独立需求分析能力 | 缺少认知引导 |
| P9-3 | 不知道什么是"好评审" | Agent 不知道评审应该检查什么、问什么问题 | 缺少评审标准外化 |

---

## 2. 问题整合分析

### 2.1 问题分类

```
问题类型分布
├── 任务管理 (P1, P2, P3)
│   └── 核心：状态同步不及时
├── 代码质量 (P4, P5, P6)
│   └── 核心：测试覆盖不足
├── 流程合规 (P7, P8)
│   └── 核心：职责边界不清晰
└── 评审能力 (P9, P9-1, P9-2, P9-3) ← 核心问题
    └── 核心：不知道什么是好评审
```

### 2.2 根因分析（5 Why）

| 问题 | 5 Why 分析 |
|------|-----------|
| P1: 状态不一致 | 1. Agent 调用 `todowrite` → 2. 只更新内存 → 3. 忘记同步文件 → 4. 缺少自动同步机制 → **5. 无同步提醒** |
| P4: 文件结构损坏 | 1. 使用 `edit` 修改复杂代码 → 2. 大块代码替换容易出错 → 3. 缺少代码块完整性校验 → **4. 无版本回滚机制** |
| P6: 单元测试缺失 | 1. 先开发后补测试 → 2. 覆盖率未强制要求 → 3. 无最小覆盖率门禁 → **4. 质量无法保障** |
| **P9: M5 遗漏** | 1. 需求评审只"确认" → 2. 不验证"完整" → 3. 不知道问什么问题 → **4. 缺少评审标准** → 5. 评审流于形式 |
| P9-2: 任务驱动 | 1. 等 Agent 1 布置任务 → 2. 不主动分析需求 → 3. 缺乏独立思考能力 → **4. 缺少认知引导机制** |

### 2.3 问题优先级

| 优先级 | 问题 | 影响范围 |
|--------|------|----------|
| **P0** | **P9: 评审能力** | **跨 Agent 协作质量** |
| P0 | P1: 状态同步 | 跨 Agent 协作 |
| P0 | P6: 单元测试缺失 | 代码质量 |
| P1 | P4: 文件结构损坏 | 开发效率 |
| P1 | P7: 职责边界 | 流程合规 |
| P2 | P3: 依赖不清晰 | 任务管理 |
| P2 | P8: 版本混乱 | 文档管理 |

### 2.4 P9 深度分析：M5 遗漏的真相

#### 2.4.1 我的行为轨迹

| 阶段 | 我的行为 | 实际情况 |
|------|----------|----------|
| 需求评审 | "确认"M5 存在 | 只看了标题/目录，没验证需求完整性 |
| 设计阶段 | 完整设计 M5 | 依赖 Agent 1 布置任务时才"知道"M5 要做什么 |
| 实现阶段 | 写了 M5 代码 | 基于"任务描述"而非独立需求分析 |

#### 2.4.2 核心问题

```
我能写出 M5 设计，不是因为我在需求评审时"看到了"，
而是因为 Agent 1 布置任务时"提到了"M5"。
```

#### 2.4.3 问题本质

| 我的认知 | 实际情况 |
|----------|----------|
| "我知道 M5" | 我只知道"M5 这个词" |
| "M5 需求存在" | 我没验证 M5 的需求是否完整 |
| "设计基于需求" | 设计基于"任务描述"，而非独立需求分析 |

---

## 3. 解决方案

### 3.1 功能建议总览

| 功能 ID | 功能名称 | 解决问题 | 优先级 |
|---------|----------|----------|--------|
| **F-AUTO-001** | 任务状态自动同步 | P1, P2 | P0 |
| **F-AUTO-002** | 最小测试覆盖率门禁 | P6 | P0 |
| **F-REVIEW-001** | **动态评审 Checklist** | **P9, P9-1, P9-2, P9-3** | **P0** |
| **F-AUTO-003** | 代码变更完整性校验 | P4 | P1 |
| **F-AUTO-004** | 职责边界检测器 | P7 | P1 |
| **F-AUTO-005** | 任务依赖自动校验 | P3 | P2 |
| **F-AUTO-006** | 文档版本自动清理 | P8 | P2 |

### 3.2 核心功能设计：F-REVIEW-001 动态评审 Checklist

#### 3.2.1 问题背景

**Agent 不知道"好的评审长什么样"**

| 当前状态 | 问题 |
|----------|------|
| Agent 收到"评审需求文档"任务 | 不知道要检查什么 |
| Agent 收到"评审设计文档"任务 | 不知道评审标准是什么 |
| Agent 只能靠"自觉" | 评审质量无法保证 |

#### 3.2.2 解决方案

**动态评审 Checklist = 评审标准的外化 + 认知引导工具**

```
任务类型              自动生成的评审 checklist
─────────────────────────────────────────
评审需求文档      →   □ 需求完整性检查
                    □ 验收标准是否明确
                    □ 依赖关系是否清晰
                    □ 风险是否识别
                    
评审设计文档      →   □ 设计是否覆盖需求
                    □ 技术方案是否可行
                    □ 边界条件是否考虑
                    □ 是否有替代方案
```

#### 3.2.3 评审类型识别

```python
class ReviewChecklistGenerator:
    """评审用动态 checklist 生成器"""

    CHECKLIST_TEMPLATES = {
        "review_requirements": {
            "base": [
                {"id": "R-001", "question": "这个需求的**前置条件**是什么？", "required": True},
                {"id": "R-002", "question": "这个需求的**边界条件**是什么？", "required": True},
                {"id": "R-003", "question": "这个需求和**其他需求**有冲突吗？", "required": True},
                {"id": "R-004", "question": "这个需求的**验收标准**是否**可验证**？", "required": True},
                {"id": "R-005", "question": "这个需求有什么**潜在风险**？", "required": True},
                {"id": "R-006", "question": "有没有**更简单**的实现方式？", "required": False},
            ],
            "reverse_check": [  # 逆向检查项（核心机制）
                {"id": "R-REV-001", "question": "这个需求**漏掉了**什么？（不是"有什么"，而是"没什么"）", "required": True},
                {"id": "R-REV-002", "question": "什么情况下这个需求**无法实现**？", "required": True},
                {"id": "R-REV-003", "question": "这个需求的**逻辑闭环**吗？", "required": True},
            ]
        },
        "review_design": {
            "base": [
                {"id": "D-001", "question": "设计是否**完整覆盖**了需求？", "required": True},
                {"id": "D-002", "question": "技术方案是否**可行**？", "required": True},
                {"id": "D-003", "question": "边界条件是否**全面考虑**？", "required": True},
                {"id": "D-004", "question": "是否有**更简单的替代方案**？", "required": False},
            ],
            "reverse_check": [
                {"id": "D-REV-001", "question": "这个设计**漏掉了**需求的哪些部分？", "required": True},
                {"id": "D-REV-002", "question": "什么情况下这个设计会**失败**？", "required": True},
            ]
        }
    }

    def generate(self, task_type: str, doc_path: str) -> List[CheckItem]:
        """生成评审用动态 checklist"""
        template = self.CHECKLIST_TEMPLATES.get(task_type, {})

        # 1. 获取基础检查项
        checklist = [CheckItem(**item) for item in template.get("base", [])]

        # 2. 添加逆向检查项（核心机制）
        reverse_items = [CheckItem(**item) for item in template.get("reverse_check", [])]
        checklist.extend(reverse_items)

        # 3. 根据文档内容动态调整
        checklist = self._customize_for_content(checklist, doc_path)

        return checklist
```

#### 3.2.4 评审执行流程

```
Agent 收到评审任务
        ↓
系统生成动态评审 checklist（含逆向检查项）
        ↓
Agent 逐项回答（强制）
        ↓
检查回答质量（不能太短、不能太笼统）
        ↓
生成评审结论
        ↓
签署
```

#### 3.2.5 回答质量校验

```python
class ReviewAnswerValidator:
    """评审回答质量验证"""

    MIN_LENGTH = 20  # 最少 20 字
    FORBIDDEN_PATTERNS = [
        "看起来没问题",
        "我没有问题",
        "同意",
        "确认",
    ]

    def validate(self, question: str, answer: str) -> ValidationResult:
        if len(answer) < self.MIN_LENGTH:
            return ValidationResult(
                valid=False,
                message=f"回答太短，请深入分析（最少 {self.MIN_LENGTH} 字）"
            )

        for pattern in self.FORBIDDEN_PATTERNS:
            if pattern in answer:
                return ValidationResult(
                    valid=False,
                    message="回答过于笼统，请给出具体分析"
                )

        return ValidationResult(valid=True)
```

#### 3.2.6 与现有 M4 集成

**M4 ExtendedChecklistGenerator 扩展支持评审场景**

```python
class ExtendedChecklistGenerator:
    def generate_review_checklist(self, doc_type: str, doc_path: str) -> List[CheckItem]:
        """生成评审用动态 checklist（复用 M4 架构）"""
        # 复用 M4 的 CheckItem 结构
        # 复用 M4 的动态生成逻辑
        # 新增：评审专用检查项
        # 新增：逆向检查机制
```

#### 3.2.7 评审 checklist 模板示例

```yaml
# review_requirements_checklist.yaml
type: review_requirements
items:
  # 基础检查项
  - id: R-001
    question: "这个需求的**前置条件**是什么？"
    type: open-ended
    required: true
    
  - id: R-002
    question: "这个需求的**边界条件**是什么？"
    type: open-ended
    required: true
    
  - id: R-003
    question: "这个需求和**其他需求**有冲突吗？"
    type: yes-no
    required: true
    
  - id: R-004
    question: "这个需求的**验收标准**是否**可验证**？"
    type: yes-no
    required: true
    
  - id: R-005
    question: "这个需求有什么**潜在风险**？"
    type: open-ended
    required: true

  # 逆向检查项（核心）
  - id: R-REV-001
    question: "这个需求**漏掉了**什么？（不是"有什么"，而是"没什么"）"
    type: open-ended
    required: true
    warning: "如果没有发现任何遗漏，说明检查不够深入"
    
  - id: R-REV-002
    question: "什么情况下这个需求**无法实现**？"
    type: open-ended
    required: true
    
  - id: R-REV-003
    question: "这个需求的**逻辑闭环**吗？"
    type: yes-no
    required: true
    if_no: "请说明哪个环节缺失"
```

### 3.3 其他功能设计

#### F-AUTO-001: 任务状态自动同步

**功能描述**: 每次 `todowrite` 或 `todoedit` 操作后，自动将状态同步到 yaml 文件。

```python
def todowrite(todos: list):
    # 1. 更新内存状态
    memory_state = update_memory(todos)
    # 2. 自动同步到文件
    sync_to_file(memory_state)
    # 3. 发送同步确认
    notify(f"已同步 {len(todos)} 个任务到文件")
```

#### F-AUTO-002: 最小测试覆盖率门禁

**功能描述**: 在 CI/CD 流程中强制要求新代码的单元测试覆盖率不低于阈值（如 80%）。

```yaml
# .github/workflows/ci.yml
- name: Coverage Gate
  run: |
    coverage_threshold=80
    current_coverage=$(echo "$report" | grep "TOTAL" | awk '{print $4}')
    if [ $current_coverage -lt $coverage_threshold ]; then
      echo "Coverage $current_coverage < $coverage_threshold"
      exit 1
    fi
```

#### F-AUTO-003: 代码变更完整性校验

**功能描述**: 在 `edit` 工具中增加代码块完整性校验，防止结构损坏。

```python
def edit(file_path, old_string, new_string):
    validate_old_string_exists(file_path, old_string)  # 验证 old_string 存在且唯一
    validate_syntax(new_string)  # 验证 new_string 语法完整性
    create_backup(file_path)  # 创建备份
    execute_edit(file_path, old_string, new_string)  # 执行替换
    validate_parsing(file_path)  # 验证文件可解析
```

#### F-AUTO-004: 职责边界检测器

**功能描述**: 在 Agent 执行操作前，检测是否越界。

```python
class ResponsibilityDetector:
    RESPONSIBILITY_MATRIX = {
        "agent1": {"can": ["review", "signoff"], "cannot": ["code", "implement"]},
        "agent2": {"can": ["code", "implement", "test"], "cannot": ["signoff_requirements"]}
    }

    def check_action(agent_id, action) -> bool:
        if action in self.RESPONSIBILITY_MATRIX[agent_id]["cannot"]:
            raise ResponsibilityViolation(f"Agent {agent_id} cannot perform {action}")
```

#### F-AUTO-005: 任务依赖自动校验

**功能描述**: 在创建任务时自动校验依赖关系，在完成任务时自动检查并更新依赖任务。

#### F-AUTO-006: 文档版本自动清理

**功能描述**: 当新版本文档发布后，自动标记旧版本为过期或废弃。

---

## 7. 深入洞察：上下文混同与逆向验证

### 7.1 P9 问题的本质

**v2.2.1 P9 问题回顾**：
- Agent 2 在需求评审时只"确认"不"质疑"
- M5 需求定义不完整，但 Agent 2 没有发现
- 原因：Agent 2 与 Agent 1 共享上下文太深，失去了独立视角

**深层原因分析**：

```
传统协作模式下的上下文演化：

Agent1 写需求 → Agent2 评审需求
     ↓                    ↓
  "应该怎么做"       "嗯，对的"
     ↓                    ↓
  多轮协作             上下文逐渐趋同
     ↓                    ↓
  Agent2 内化         失去了批判性思维
  Agent1 的思维
```

**核心洞察**：
> 不是"看不懂"，而是"太认同"
> 不是"不知道标准"，而是"标准被同化了"

### 7.2 Checklist 的局限性

```
正向检查项（Agent2 自问自答）：
├── R-001: 前置条件是什么？      ✓ 能回答
├── R-002: 边界条件是什么？    ✓ 能回答
└── R-REV-001: 漏掉了什么？    ❓ Agent2 已经被同化，他觉得"没漏掉"

根本矛盾：
├── Agent2 已经被深度影响
├── 他真诚地认为"没问题"
├── Checklist 只能检查"有没有"
└── 无法检查"对不对"
```

### 7.3 逆向验证机制

**核心思路**：不是问"有什么问题"，而是问"如何证明这是错的"。

```
传统评审（正向）:
Q: 这个需求有什么问题？
A: 看起来没问题

逆向验证（反向）:
Q: 如果这个需求是错的，什么证据可以证明？
A: ... 等等，如果 X 情况发生，就会出问题！
```

### 7.4 逆向验证检查项设计

| ID | 问题类型 | 核心问题 |
|-----|---------|---------|
| RV-001 | 找风险 | 什么情况下这个需求会导致**返工**？ |
| RV-002 | 找痛点 | 如果你是**最后一个接盘的人**，你会骂娘的点是什么？ |
| RV-003 | 找漏洞 | 提出一个**最可能的反驳意见**，然后反驳它 |
| RV-004 | 找滥用 | 如果这个需求被**恶意执行**，会发生什么？ |
| RV-005 | 找歧义 | 把需求**翻译成最笨的人也能听懂的话**，然后检查是否还是对的？ |

### 7.5 心理学依据

| 机制 | 心理学原理 | 作用 |
|------|------------|------|
| 逆向验证 | 反事实思维 | 想象替代方案，发现盲点 |
| 角色扮演 | 观点采择 | 从不同角度看问题 |
| 找证据反驳 | 证实偏见对抗 | 主动找反例 |

### 7.6 与正向检查项的对比

| 类型 | 问题模式 | 心理模式 | 有效性 |
|------|---------|----------|--------|
| 正向 | 有什么问题？ | 验证确认 | ❌ 被同化后无效 |
| 逆向 | 如何证明错了？ | 反证反驳 | ✅ 强制对抗性思考 |

**结论**：F-REVIEW-001 应该同时包含正向和逆向检查项，且**逆向检查项应该作为核心机制**。

---

## 4. 实施建议

### 4.1 版本规划

| 版本 | 功能 | 说明 |
|------|------|------|
| **v2.2.2** | F-REVIEW-001 + F-AUTO-001 + F-AUTO-002 | 评审能力 + 状态同步 + 测试门禁 |
| v2.2.3 | F-AUTO-003 + F-AUTO-004 | 代码完整性 + 职责边界 |
| v2.2.4 | F-AUTO-005 + F-AUTO-006 | 依赖校验 + 版本清理 |

### 4.2 v2.2.2 详细实施

| 功能 | 预估工时 | 依赖 |
|------|----------|------|
| F-REVIEW-001: 动态评审 Checklist | 8h | M4 ExtendedChecklistGenerator |
| F-AUTO-001: 任务状态自动同步 | 2h | todowrite 工具 |
| F-AUTO-002: 测试覆盖率门禁 | 4h | CI/CD 流水线 |

### 4.3 验收标准

每个功能需满足：
- [ ] 单元测试覆盖率 ≥ 90%
- [ ] E2E 测试覆盖关键路径
- [ ] 文档更新
- [ ] Agent 1 评审签署

---

## 5. 价值总结

### 5.1 转变对比

| 方面 | 改进前 | 改进后 |
|------|--------|--------|
| **评审** | 不知道什么是好评审 | checklist 告诉你 |
| **同步** | 手动同步易遗漏 | 自动同步 |
| **测试** | 覆盖率无保证 | 门禁强制 |
| **执行** | 凭自觉 | 按清单执行 |

### 5.2 核心价值

```
动态评审 Checklist = 把"好的评审"变成"可执行的步骤"
```

**解决的根本问题**：
- Agent 不再"只会确认，不会质疑"
- Agent 不再"任务驱动，而是需求驱动"
- Agent 不再"不知道问什么问题"

---

## 6. 风险与应对

| 风险 | 可能性 | 影响 | 应对措施 |
|------|--------|------|----------|
| 自动同步导致状态覆盖 | 低 | 中 | 增加确认提示 |
| 覆盖率门禁阻碍开发 | 中 | 低 | 设置合理阈值 |
| 职责边界误判 | 低 | 中 | 支持人工豁免 |
| 评审 checklist 流于形式 | 中 | 中 | 强制回答质量校验 |

---

## 6.1 Agent 1 评审说明

**说明**：问题反思和需求讨论是一个开放过程，Agent 1 可以根据实际情况选择性地提出意见。

**如果需要 Agent 1 做具体任务**，将通过正式的 TODO 任务布置。

---

## 签署确认

### Agent 2 确认

| 确认项 | 内容 |
|--------|------|
| 文档版本 | v2 |
| 创建日期 | 2026-02-07 |
| 核心问题 | P9: M5 需求遗漏 - 评审流于形式 |
| 核心解决方案 | F-REVIEW-001: 动态评审 Checklist（含逆向检查项） |

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-07 | ✅ |

### Agent 1 评审

Agent 1 可选择性提出意见，无需逐条回应。

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | | ⏳ |

---

**文档版本**: v2
**创建日期**: 2026-02-07
**状态**: 待 Agent 1 评审（开放讨论，可选择性回应）
