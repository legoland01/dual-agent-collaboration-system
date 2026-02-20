# Bug报告：查看TODO后未使用question tool交互

**Bug ID**: BUG-20260219-003  
**版本**: v2.3.2  
**报告日期**: 2026-02-19  
**报告人**: Agent2  
**优先级**: high  
**类型**: 功能缺失  

---

## 问题描述

用户执行"查看TODO"后，Agent只是简单地列出TODO列表，没有使用question tool让用户选择操作。

期望行为（根据TODO_NOTIFY.md）：
1. 读取未读TODO
2. 使用question tool询问用户操作

实际行为：
1. 直接执行`oc-collab todo list`输出文本列表
2. 没有弹出交互式选项

---

## 复现步骤

1. 切换到Agent2: `oc-collab switch 2`
2. 用户告知"查看TODO"
3. Agent仅输出文本列表，未调用question tool

---

## 根因分析

TODO_NOTIFY.md 规则存在于 `config/instructions/`，但：
1. OpenCode启动时未正确加载该instruction
2. Agent不知道需要使用question tool进行交互

---

## 期望行为

当检测到用户有未读TODO时，应调用question tool：

```json
{
  "name": "question",
  "arguments": {
    "questions": [{
      "header": "待办事项",
      "question": "您有 N 个待处理TODO",
      "options": [
        {"label": "立即执行", "description": "开始处理第一个TODO"},
        {"label": "查看详情", "description": "查看所有TODO详情"}
      ]
    }]
  }
}
```

---

## 修复建议

1. 确认OpenCode加载instruction的机制
2. 或在Agent代码中添加显式的question tool调用逻辑

---

**状态**: completed  
**修复内容**:
- 更新 `instructions/TODO_NOTIFY.md`，强化指令格式，使用 ⚠️ 和 ❌ 标记
- 明确禁止直接执行 `oc-collab todo list`，必须使用 question tool
- 更新 `config/instructions/TODO_NOTIFY.md` 保持一致
- **注意**: 需要重启OpenCode或刷新session使新instruction生效
