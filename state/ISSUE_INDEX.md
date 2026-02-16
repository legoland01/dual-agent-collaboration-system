# oc-collab 问题追踪索引

**最后更新**: 2026-02-16
**版本**: v1.0
**维护者**: Agent1

---

## 索引规则

| 前缀 | 类型 | 说明 | 存储位置 |
|------|------|------|----------|
| BUG-YYYYMMDD-XXX | Bug | 代码缺陷、功能错误 | docs/00-memos/ |
| PROPOSAL-YYYY-MM-XXX | 提案 | 新功能提案 | docs/04-proposals/ |
| TODO-XXX | 任务 | 待办任务 | state/agent_adhoc_todos.yaml |
| MEMO-YYYY-MM-XXX | 备忘录 | 会议记录、临时记录 | docs/00-memos/ |

---

## 活跃问题

### P0 - Critical

| ID | 问题 | 状态 | 负责人 | 创建日期 |
|----|------|------|--------|----------|

### P1 - High

| ID | 问题 | 状态 | 负责人 | 创建日期 |
|----|------|------|--------|----------|
| BUG-20260216-025 | ISSUE_INDEX版本状态缺乏自动更新机制 | OPEN | Agent2 | 2026-02-16 |

---

## 待评审文档

| ID | 文档 | 状态 | 评审人 | 创建日期 |
|----|------|------|--------|----------|
| PROPOSAL-2026-02-001 | 规则自动加载机制 | PENDING | - | 2026-02-10 |

---

## 已修复 BUG

| ID | 问题 | 解决方案 | 修复人 | 关闭日期 |
|----|------|----------|--------|----------|
| BUG-20260210-001 | skill enforce未强制执行 | 集成SkillEnforcer到todowrite/signoff/advance | Agent2 | 2026-02-10 |
| BUG-20260210-002 | todowrite未写入文件 | 修复文件格式兼容 | Agent2 | 2026-02-10 |

---

## v2.2.x 开发进度

| 版本 | 状态 | 说明 |
|------|------|------|
| v2.3.0 | 开发中 | 概要设计DRAFT，质量保证工具集 |
| v2.2.12 | 已完成 | - |

---

## 相关文件

- 问题追踪规范: `skills/oc_collab_issue_tracker/content.md`
- 待办任务: `state/agent_adhoc_todos.yaml`
- Bug报告: `docs/00-memos/BUG-*.md`
- 提案: `docs/04-proposals/PROPOSAL-*.md`
