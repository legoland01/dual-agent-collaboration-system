# BUG报告：AutoBugDetector从未自动工作

**BUG编号**：BUG-20260215-002
**发现日期**：2026-02-15
**发现者**：Agent 1
**优先级**：P0
**状态**：open

---

## 问题描述

AutoBugDetector（v2.2.9开发的功能）**从未自动工作过**。

历史上所有问题（B-003、B-007、B-008等）都是由Agent人工发现并创建BUG报告，AutoBugDetector从未自动检测并生成报告。

## 复现场景

### 历史问题（均为人工发现）

| BUG | 发现方式 | AutoBugDetector |
|-----|----------|-----------------|
| BUG-20260213-003 todowrite调用失败 | Agent人工 | ❌ 无报告 |
| BUG-20260213-007 TODO编号冲突 | Agent人工 | ❌ 无报告 |
| BUG-20260213-008 Agent2认知错误 | Agent人工 | ❌ 无报告 |
| BUG-20260215-001 TODO编号生成逻辑 | Agent人工 | ❌ 无报告 |

### AutoBugDetector预期行为

```
Agent执行关键操作
    │
    ▼
┌─────────────────────┐
│ AutoBugDetector    │  ← 期望：自动调用
│ (自动检测异常)     │
└─────────┬───────────┘
          │
          ▼
    检测到问题 ──→ 生成Bug报告
          │
          ▼
    docs/00-memos/BUG-*.md
```

### 实际行为

```
Agent执行关键操作
    │
    ▼
┌─────────────────────┐
│ 无检测              │  ← 实际：未调用
└─────────────────────┘
          │
          ▼
    Agent人工发现
```

## 根因分析

### 代码存在，但未集成

| 组件 | 状态 | 说明 |
|------|------|------|
| `src/core/auto_bug_detector.py` | ✅ 存在 | 检测逻辑完整 |
| `signoff` 命令集成 | ❌ 缺失 | 未调用AutoBugDetector |
| `phase` 命令集成 | ❌ 缺失 | 未调用AutoBugDetector |
| `todowrite` 集成 | ❌ 缺失 | 未调用AutoBugDetector |

### 当前唯一调用点

仅在 `todoedit --status completed` 时调用：

```python
# enhanced_commands.py:222
if status == "completed":
    detector = AutoBugDetector(state_manager=state_manager)
    bugs = detector.check_todo_completion(todo_id)
```

### 设计文档 vs 实现

| 文档要求 | 实现状态 |
|---------|---------|
| 检测TODO完成时文档状态 | ✅ 已实现 |
| 检测签署不完整 | ❌ 未集成 |
| 检测命令执行失败 | ❌ 未集成 |
| 检测阶段推进无效 | ❌ 未集成 |

**问题类型**：需求-实现不一致

- 需求文档定义了功能
- 代码实现了核心检测逻辑
- **但CLI命令集成未完成**

## 影响范围

1. 所有历史BUG均为人工发现
2. AutoBugDetector功能形同虚设
3. Agent协作缺少自动化监督

## 修复方案

### 短期：完成CLI集成

在关键命令中调用AutoBugDetector：

```python
# signoff 命令后
detector = AutoBugDetector()
bugs = detector.check_signoff_completion(phase)

# phase 命令后
detector = AutoBugDetector()
bugs = detector.check_phase_transition(from_phase, to_phase)

# todowrite 后（新增）
detector = AutoBugDetector()
bugs = detector.check_todo_format(todo_id)
```

### 长期：完善需求文档

更新 `PROPOSAL-2026-02-002_auto_bug_detection.md`，
明确所有触发点和集成方式。

---

## 修复记录

### 1. 新增 self_review() 方法

**文件**: `src/core/auto_bug_detector.py`

```python
def self_review(self, completed_todo_id: str, agent_id: int) -> List[BugReport]:
    """
    任务后自检 - 每次任务完成后自动检查

    检查项：
    - 任务目标明确
    - 执行步骤记录
    - 发现问题记录
    - 用户反馈确认
    """

def check_todo_id_format(self, todo_id: str, agent_id: int) -> Optional[BugReport]:
    """检查TODO编号格式是否符合Agent独立编号规则"""
```

### 2. 集成到 todowrite 命令

**文件**: `src/cli/enhanced_commands.py`

```python
# v2.2.15: AutoBugDetector集成 - 任务后自检
if agent_id:
    detector = AutoBugDetector()
    bugs = detector.self_review(todo.id, agent_id)
    if bugs:
        # 生成Bug报告
        file_path = detector.generate_bug_report(bug)
        # 自动创建修复TODO
        fix_todo = sync_manager.add_todo(
            f"修复{bug.bug_id}: {bug.description[:50]}...",
            agent_id=2,
            priority="high"
        )
```

### 测试结果

```
$ oc-collab todowrite --content "测试" --agent 1
✅ 待办已创建: [TODO-1-367] 测试
⚠️  自检发现问题:
   📄 Bug报告: BUG-20260215-004
      任务自检不完整: 发现问题记录, 用户反馈确认
      📄 docs/00-memos/BUG-20260215-004.md
      ✅ 自动创建修复TODO: BUG-20260215-005
      📋 TODO-2-369 已创建
```

**生成的文件**: `docs/00-memos/BUG-20260215-004.md`

---

## 验收标准

- [x] `todowrite` 命令触发AutoBugDetector
- [x] 自检能发现问题
- [x] 发现问题后自动生成Bug报告
- [x] Bug报告自动创建修复TODO
- [ ] `signoff` 命令触发AutoBugDetector（待实现）
- [ ] `phase` 命令触发AutoBugDetector（待实现）

## 关联文档

| 文档 | 说明 |
|------|------|
| `src/core/auto_bug_detector.py` | 检测逻辑代码 |
| `PROPOSAL-2026-02-002_auto_bug_detection.md` | 需求定义 |
| `DETAIL_v2.2.9.md` | 详细设计 |

---

**报告人**：Agent 1
**日期**：2026-02-15
**状态**：待修复
