# Memo: Agent2任务获取流程不规范

**日期**: 2026-02-15
**类型**: 流程规范问题
**状态**: Open

---

## 问题

Agent2没有遵循自动获取TODO的流程，仍在使用"传统方法"（手动查找任务）。

## 分析

**预期流程**：
```
Agent1创建TODO → Agent2从YAML获取 → 执行任务
```

**实际流程**：
```
Agent1创建TODO → Agent2手动查找/询问 → 执行任务
```

## 根因

1. **Skill缺失**：没有明确规定Agent2如何获取任务
2. **显示问题**：session_manager不显示TODO（BUG-015）
3. **无主动推送**：Agent2切换时没有主动显示待办

## 解决方案

1. 修复BUG-015：让session_manager显示TODO
2. 更新Skill：明确Agent2获取任务的方式
3. 增强`switch 2`命令：切换时主动显示TODO

---

**建议**：这个不需要创建新BUG，而是需要：
1. 修复BUG-015（让TODO可见）
2. 更新Skill规范Agent2行为
