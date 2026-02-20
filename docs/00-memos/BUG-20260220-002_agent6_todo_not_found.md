# BUG报告: Agent6发送的TODO查询不到

## 基本信息

| 字段 | 值 |
|------|-----|
| Bug ID | BUG-20260220-002 |
| 日期 | 2026-02-20 |
| 报告人 | agent5 (Consultant) |
| 优先级 | P1 |
| 状态 | Open |

---

## 问题描述

用户（agent5）反馈：agent6发送了一个TODO给他，但查询不到。

- **发送方**: agent6 (test-agent产品经理)
- **接收方**: agent5 (HQ顾问)
- **现象**: 使用 `oc-collab todo list` 无法看到agent6发送的TODO

---

## 具体信息

agent6 发送给 agent5 的 TODO：
- **ID**: TODO-Noneto5-001
- **内容**: 评审统一测试平台工作流程设计文档
- **接收者**: 5 (agent5)
- **状态**: pending

**查询结果**:
```bash
# oc-collab 的数据库（无数据）
sqlite3 oc-collab/state/todos.db "SELECT ... "  # 返回空

# test-agent 的数据库（有数据）
sqlite3 test-agent/state/todos.db "SELECT ... "  
# 结果: TODO-Noneto5-001|评审统一测试平台工作流程设计文档|5|pending
```

---

## 根因

**跨子系统数据隔离**：
- 每个子系统有独立的 `state/todos.db`
- agent6 在 test-agent 创建 TODO，存储在 test-agent 的数据库
- agent5 在 oc-collab 查询，查的是 oc-collab 的数据库
- 两个数据库之间没有同步机制

---

## 影响范围

- 跨子系统TODO通信（oc-collab ↔ test-agent）
- 跨子系统TODO通信（oc-collab ↔ conf-man）
- 后续发布流程（需要统一的TODO数据）
