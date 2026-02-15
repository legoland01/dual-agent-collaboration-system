# BUG-20260215-006: AutoBugDetector self_review 产生误报

**BUG编号**：BUG-20260215-006
**发现日期**：2026-02-15
**发现者**：Agent 1
**优先级**：P1
**状态**：open

---

## 问题描述

AutoBugDetector 的 `self_review()` 方法产生误报。

### 复现场景

```
$ oc-collab todowrite --content "再次测试AutoBugDetector" --agent 2
✅ 待办已创建: [TODO-2-368]
⚠️  自检发现问题:
   📄 Bug报告: BUG-20260215-005
      任务自检不完整: 发现问题记录, 用户反馈确认
```

### 问题分析

这是一个简单的测试任务，内容为"再次测试AutoBugDetector"：
- 目标：测试 AutoBugDetector 功能
- 不需要"发现问题记录"（因为没有真实问题）
- 不需要"用户反馈确认"（因为不是生产任务）

但 `self_review()` 硬编码检查所有项，导致误报。

---

## 根因分析

### 当前 self_review() 实现

```python
# src/core/auto_bug_detector.py

def self_review(self, completed_todo_id: str, agent_id: int) -> List[BugReport]:
    checklist = [
        ("任务目标明确", completed_todo.content and len(completed_todo.content) > 5),
        ("执行步骤记录", True),  # ❌ 总是通过
        ("发现问题记录", False), # ❌ 总是失败
        ("用户反馈确认", False), # ❌ 总是失败
    ]
```

### 问题

| 检查项 | 问题 |
|--------|------|
| 执行步骤记录 | 硬编码 `True`，无法真正检查 |
| 发现问题记录 | 对简单测试任务也要求，误报来源 |
| 用户反馈确认 | 同上 |

---

## 影响范围

1. 所有简单测试/验证任务都会产生误报
2. 用户体验下降，失去对 AutoBugDetector 的信任
3. 产生大量无意义的 Bug 报告和 TODO

---

## 修复方案

### 方案：调用 LLM 智能判断

**核心思路：** 将任务内容发送给 LLM，让它智能判断是否需要自检。

**实现：**

```python
def self_review(self, todo_content: str, agent_id: int) -> List[BugReport]:
    bugs = []

    # 调用 LLM 智能判断
    llm_result = self._analyze_with_llm(todo_content)

    if llm_result.needs_review:
        # 根据 LLM 返回的问题生成 Bug 报告
        for issue in llm_result.issues:
            bug = BugReport(...)
            bugs.append(bug)

    return bugs

def _analyze_with_llm(self, todo_content: str) -> LLMResult:
    """
    使用 LLM 分析任务是否需要自检

    Returns:
        LLMResult: {
            "needs_review": bool,
            "issues": List[str],
            "reason": str
        }
    """
    prompt = f"""
任务内容：「{todo_content}」

请判断：
1. 这是一个需要详细自检的正式任务吗？
2. 是否存在可能的问题或风险？

注意：
- 简单的测试、验证、检查类任务不需要完整自检
- 正式开发、修复 Bug、实现功能等需要自检

请返回 JSON：
{{
    "needs_review": true/false,
    "issues": ["问题1", "问题2"],  // 如果需要Review
    "reason": "判断理由"
}}
"""
    # 调用 LLM API
    return call_llm(prompt)
```

---

## 验收标准

- [ ] LLM 能够智能区分简单任务和正式任务
- [ ] 简单测试任务不再产生误报
- [ ] 正式任务能够发现真实问题
- [ ] 自检结果有 LLM 的判断理由

---

## 关联文档

| 文档 | 说明 |
|------|------|
| `src/core/auto_bug_detector.py` | self_review() 方法 |
| `BUG-20260215-002` | AutoBugDetector CLI 集成 |
| `docs/00-memos/BUG-20260215-005.md` | 误报案例 |

---

**报告人**：Agent 1
**日期**：2026-02-15
**状态**：待修复
