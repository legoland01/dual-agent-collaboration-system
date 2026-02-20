# BUG-20260219-012: todowrite创建TODO时source参数无效

**严重程度**: 中  
**类型**: CLI参数解析错误  
**发现时间**: 2026-02-19  
**发现者**: Agent1

---

## 问题描述

使用 `--source agent1` 参数创建TODO时，系统忽略该参数，创建了错误的TODO ID格式。

## 复现步骤

```bash
oc-collab todowrite --content "修复BUG-20260219-011" --to agent2 --priority high --source agent1
```

## 期望结果

- TODO ID: `TODO-1to2-011`
- 分配: agent1 → agent2

## 实际结果

- TODO ID: `TODO-2to2-007`
- 分配: agent2 → agent2

## 根本原因

`--source` 参数没有被正确解析：
- 参数名应该是 `--from` 而非 `--source`
- 或者参数解析逻辑有bug

---

**状态**: 待修复  
**优先级**: 中
