# BUG-20260219-005: Agent未自动唤起question tool call

**严重程度**: 高  
**类型**: 流程违规  
**发现时间**: 2026-02-19  
**发现者**: Agent1  

---

## 问题描述

根据 `instructions/TODO_NOTIFY.md` 规则，当用户说"查看todo"时，Agent必须：
1. **不要**直接运行 `oc-collab todo list` 命令
2. **必须**使用 question tool 询问用户想要执行的操作

当前Agent1直接执行 `oc-collab todo list` 并输出文本，违反了规则。

## 复现步骤

1. 以Agent1身份登录
2. 用户说"查看todo"
3. Agent1直接运行 `oc-collab todo list` 并展示结果

## 期望行为

用户说"查看todo"时，Agent应立即调用：

```json
{
  "name": "question",
  "arguments": {
    "questions": [{
      "header": "待办事项",
      "question": "您有 N 个待处理TODO，请选择操作：",
      "options": [
        {"label": "查看列表", "description": "查看所有TODO详情"},
        {"label": "立即执行", "description": "开始处理第一个TODO"},
        {"label": "标记已读", "description": "将所有TODO标记为已读"}
      ]
    }]
  }
}
```

## 影响

- 违反系统定义的流程规则
- 用户体验不一致

---

**状态**: 待修复  
**优先级**: 高
