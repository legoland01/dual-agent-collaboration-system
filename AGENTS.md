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


## Skill 查询规则 ⭐

**永远不要直接问用户，先查Skill**

1. **遇到问题时的处理顺序**：
   - Step 1: 查阅 `skills/` 目录下的相关Skill
   - Step 2: 使用 `oc-collab skill search --keywords <关键词>` 搜索
   - Step 3: 如果Skill有SOP四要素，按照步骤执行
   - Step 4: 如果Skill找不到或觉得困惑，再问用户

2. **禁止行为**：
   - ❌ 直接问用户"要怎么做？"
   - ❌ 不查Skill就凭经验操作
   - ❌ 跳过Skill中规定的流程步骤

3. **强制要求**：
   - 每次部署发布前必须查阅 `oc_collab_deployment_guide`
   - 每次处理Bug前必须查阅 `oc_collab_bug_management_guide`
   - 每次创建需求前必须查阅 `oc_collab_requirements_guide`

4. **例外情况**：
   - Skill明显过时或不适用（需注明）
   - 全新场景，Skill不存在（需创建新Skill）

**示例**：
- ❌ 错误："需要发布到PyPI吗？"（未查Skill）
- ✅ 正确：根据 `oc_collab_deployment_guide`，部署阶段必须发布到PyPI，直接执行

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
