# BUG-20260219-004: Agent1能看见分配给Agent2的TODO

**严重程度**: 中  
**类型**: 权限/隔离问题  
**发现时间**: 2026-02-19  
**发现者**: Agent1  

---

## 问题描述

当前Agent1执行 `oc-collab todo list` 时，可以看到分配给Agent2的TODO（如 `agent1 → agent2`）。

根据AGENTS.md规则：
- Agent1只应看到分配给自己的TODO
- Agent2只应看到分配给自己的TODO
- TODO应该在Agent之间隔离

## 复现步骤

1. 以Agent1身份登录
2. 执行 `oc-collab todo list`
3. 观察到显示 `agent1 → agent2` 的TODO

## 期望行为

- Agent1只能看到 `agent2 → agent1` 的TODO（Agent2分配给Agent1的）
- Agent1不应该看到 `agent1 → agent2` 的TODO

## 影响

- 违反Agent职责隔离原则
- 可能导致Agent1误操作Agent2的TODO

---

**状态**: 待修复  
**优先级**: 中
