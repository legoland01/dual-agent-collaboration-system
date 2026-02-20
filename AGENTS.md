# oc-collab 核心规则

## Agent 分工

| Agent | 角色 | 团队 | 职责 |
|-------|------|------|------|
| **agent1** | 产品经理 | oc-collab | 发现问题 → 创建TODO → 记录文档 |
| **agent2** | 架构师 | oc-collab | 执行代码 → 修复Bug → 技术评审 |

---

## 全局Agent注册表

| Agent | 角色 | 团队 | 说明 |
|-------|------|------|------|
| agent1 | 产品经理 | oc-collab | oc-collab核心 |
| agent2 | 架构师 | oc-collab | oc-collab核心 |
| agent3 | 产品经理 | pm-agent | 项目管理 |
| agent4 | 架构师 | pm-agent | 项目技术 |
| agent5 | 顾问 | HQ | 协调/评审/研究 |
| agent6 | 产品经理 | test-agent | 测试规划 |
| agent7 | 架构师 | test-agent | 测试架构 |
| agent8 | 产品经理 | conf-man | 版本管理 |
| agent9 | 架构师 | conf-man | 版本技术 |
| agent1t~10t | 测试工程师 | test-agent | 测试执行 |

---

## Skill管理规则

| 管理项 | 负责人 | 说明 |
|--------|--------|------|
| **Skill创建/更新** | Agent1 | 负责编写和维护所有Skill |
| **Skill技术实现** | Agent2 | 负责Skill依赖的代码实现 |
| **Skill评审** | Agent2 | Agent1创建Skill后，由Agent2评审技术可行性 |

---

## 关键规则（Compaction 后必须遵守）

1. **开发完成后立即git push** - 所有代码和文档必须即时推送，否则跨机器无法协同
2. **Agent1 永远不直接改代码**，由 Agent2 执行
3. 发现Bug后，Agent1 只做：
   - 创建 Bug 报告 (`docs/00-memos/`)
   - 创建 TODO 任务 (`state/todos.db`，使用 `oc-collab todo list` 查询)
   - 更新需求/设计文档
4. **让 Agent2 执行修复**，不要自己动手
5. Compaction 后立即重新读取此文件确认规则
6. **用户身份声明**：当用户说"你是agentX"时，必须立即执行 `oc-collab switch X` 更新系统状态

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
- `state/todos.db` - 待办任务列表（使用 `oc-collab todo list` 查询）
- `docs/00-memos/` - Bug 报告和备忘录

Agent2 需要定期检查：
- `state/todos.db` - 分配给自己的任务（使用 `oc-collab todo list` 查询）
- `docs/00-memos/` - 待修复的 Bug

---


## v2.2.x 版本规范

- 当前版本: v2.2.7
- 架构文档: `docs/00-architecture/CORE_ARCHITECTURE.md`
- 需求模板: `docs/01-requirements/TEMPLATE_requirements.md`
- 所有新功能必须映射到 `CORE_ARCHITECTURE.md` 的模块编号
