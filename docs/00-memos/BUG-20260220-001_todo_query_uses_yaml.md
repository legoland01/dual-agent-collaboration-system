# BUG报告: TODO查询使用错误的数据库

## 基本信息

| 字段 | 值 |
|------|-----|
| Bug ID | BUG-20260220-001 |
| 日期 | 2026-02-20 |
| 报告人 | agent5 (Consultant) |
| 优先级 | P0 |
| 状态 | Open |

---

## 问题描述

当前 TODO 查询机制存在问题：

1. **各子系统有独立的数据库**：
   - `oc-collab/state/todos.db`
   - `test-agent/state/todos.db`
   - `conf-man/` (待创建)

2. **跨子系统TODO无法查询**：
   - agent6 在 test-agent 创建 TODO
   - agent5 在 oc-collab 查询
   - 查不到（查的是自己的数据库）

3. **CLI 从错误的数据库查询**：
   - `oc-collab todo list` 只查 oc-collab 的数据库
   - 查不到其他子系统创建的 TODO

---

## 预期行为

- TODO 数据应统一存储或同步
- 任何 agent 查询能看到所有发给自己的 TODO（不论发送方来自哪个子系统）

---

## 实际行为

- 各子系统各自维护独立的 todos.db
- 跨子系统 TODO 无法查询
- 需要手动切换到对应子系统查询

---

## 影响范围

- 跨子系统 TODO 通信
- 发布流程（需要准确的 TODO 数据）

---

## 根因分析

1. 缺乏统一的 TODO 存储层
2. 缺乏跨子系统同步机制
3. CLI 只查询当前子系统数据库

---

## 修复建议

方案A（推荐）：统一存储
- 所有子系统的 TODO 存储到同一个数据库
- 或使用共享存储

方案B：跨系统同步
- 各子系统数据库定时同步
- 或实时推送通知

---

## 相关文件

- `oc-collab/state/todos.db`
- `test-agent/state/todos.db`
- `conf-man/` (待创建)
