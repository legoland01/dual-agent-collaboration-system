# oc-collab 核心规则（永不变）

## Agent 分工

| Agent | 职责 | 原则 |
|-------|------|------|
| **Agent1** | 发现问题 → 创建TODO → 记录文档 | 原则上不直接改代码 |
| **Agent2** | 执行代码 → 修复Bug → 合并到分支 | 负责所有代码实现 |

---

## 关键规则（Compaction 后必须遵守）

1. **Agent1 永远不直接改代码**，由 Agent2 执行
2. 发现Bug后，Agent1 只做：
   - 创建 Bug 报告 (`docs/00-memos/`)
   - 创建 TODO 任务 (`state/agent_adhoc_todos.yaml`)
   - 更新需求/设计文档
3. **让 Agent2 执行修复**，不要自己动手
4. Compaction 后立即重新读取此文件确认规则

---

## 引用文件

Agent1 需要定期检查：
- `state/agent_adhoc_todos.yaml` - 待办任务列表
- `docs/00-memos/` - Bug 报告和备忘录

Agent2 需要定期检查：
- `state/agent_adhoc_todos.yaml` - 分配给自己的任务
- `docs/00-memos/` - 待修复的 Bug

---

## v2.2.x 版本规范

- 当前版本: v2.2.7
- 架构文档: `docs/00-architecture/CORE_ARCHITECTURE.md`
- 需求模板: `docs/01-requirements/TEMPLATE_requirements.md`
- 所有新功能必须映射到 `CORE_ARCHITECTURE.md` 的模块编号
