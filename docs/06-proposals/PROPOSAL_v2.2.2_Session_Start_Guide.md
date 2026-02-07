# 提案：Session 启动时自动引导 Agent

**提案ID**: PROPOSAL-2026-02-002
**版本**: v1
**日期**: 2026-02-07
**作者**: Agent 2 (开发负责人)
**状态**: DRAFT

---

## 1. 问题背景

### 1.1 当前问题

新 Agent 进入项目或 Session 重启时，存在以下问题：

| 场景 | 预期体验 | 实际体验 |
|------|----------|----------|
| 新项目 | Agent 自动看到协作指南 | Agent 不知道怎么做 |
| Session 重启 | Agent 自动收到欢迎消息 | 需要手动查看 |
| Agent 困惑时 | 自动加载协作指南 | 依赖 Agent 自觉 |

### 1.2 根本原因

```
当前架构：
├── skills/oc_collab_collaboration_guide/  ← 存在，但未自动加载
├── state/project_state.yaml              ← 存在，但未自动显示
└── 问题：Agent 进入项目后，不知道去看这些文件
```

### 1.3 影响

- Agent 无法快速了解项目状态
- Agent 无法立即知道自己的角色和职责
- Agent 需要手动查找协作流程
- 新 Agent 学习曲线陡峭

---

## 2. 解决方案

### 2.1 核心功能

**Session 启动自动引导**：Agent 进入项目时，自动显示欢迎消息和协作指南摘要。

```
Agent 进入项目
    ↓
系统自动显示欢迎消息
    ↓
Agent 立即知道：
- 当前阶段
- 自己的角色
- 下一步该做什么
- 协作指南入口
```

### 2.2 功能详情

#### 2.2.1 欢迎消息

```python
def show_welcome_message(agent_id: str, project_state: dict) -> str:
    """显示欢迎消息"""

    phase = project_state.get("phase", "unknown")
    todos = get_pending_todos(agent_id)

    message = f"""=== 欢迎使用 OC-Collab ===

项目: {project_state.get('name', 'Unknown')}
当前阶段: {phase}
版本: {project_state.get('version', 'Unknown')}

你的角色: {agent_id}

待办任务 ({len(todos)} 项):
{format_todos(todos)}

下一步: {get_next_action(agent_id, phase)}

输入 'oc-collab status' 查看详情
输入 'oc-collab todo' 查看待办
"""
    return message
```

#### 2.2.2 协作指南摘要

```python
def show_guide_summary(agent_id: str) -> str:
    """显示协作指南摘要"""

    role_responsibilities = {
        "agent1": [
            "创建需求和设计文档",
            "编写黑盒测试用例",
            "执行黑盒测试",
            "部署和发布"
        ],
        "agent2": [
            "评审需求和设计",
            "开发功能代码",
            "编写白盒测试",
            "签署确认"
        ]
    }

    summary = f"""=== 协作指南摘要 ===

你的职责:
{format_list(role_responsibilities.get(agent_id, []))}

工作流程:
1. 需求评审 → 2. 设计评审 → 3. 开发测试 → 4. 部署发布

查看完整协作指南:
cat skills/oc_collab_collaboration_guide/content.md
"""
    return summary
```

#### 2.2.3 自动触发机制

```python
# 在 M5 SessionStarter 中扩展
class SessionStarter:
    """会话起始引导器"""

    def on_session_start(self, agent_id: str) -> None:
        """Session 启动时自动触发"""
        project_state = self.state_manager.load_state()

        # 1. 显示欢迎消息
        welcome = self.get_welcome_message(agent_id)
        click.echo(welcome)

        # 2. 显示协作指南摘要
        guide = self.get_guide_summary(agent_id)
        click.echo(guide)

        # 3. 询问是否需要帮助
        if click.confirm("需要查看详细协作指南吗？"):
            self.show_full_guide()
```

### 2.3 技术实现

#### 2.3.1 修改 M5 SessionStarter

```python
# src/core/cognitive_immune.py

class SessionStarter:
    """会话起始引导器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.skill_loader = SkillLoader(project_path)

    def on_session_start(self, agent_id: str) -> Dict[str, str]:
        """Session 启动时自动触发"""
        project_state = self._load_project_state()

        welcome = self._generate_welcome(agent_id, project_state)
        guide = self._generate_guide_summary(agent_id)
        actions = self._suggest_next_actions(agent_id, project_state)

        return {
            "welcome": welcome,
            "guide": guide,
            "actions": actions
        }

    def display_welcome(self, agent_id: str) -> str:
        """显示欢迎消息"""
        return self.on_session_start(agent_id)["welcome"]
```

#### 2.3.2 CLI 集成

```python
# src/cli/main.py

@click.command()
def status():
    """查看项目状态"""
    # ... 现有逻辑

@main.command()
def start():
    """开始协作会话（自动触发欢迎消息）"""
    agent_id = detect_agent_id()
    project_state = load_state()

    starter = SessionStarter(project_path)
    starter.on_session_start(agent_id)
```

#### 2.3.3 触发时机

| 时机 | 触发条件 | 动作 |
|------|----------|------|
| Session 启动 | Agent 进入项目目录 | 自动显示欢迎消息 |
| 手动触发 | 运行 `oc-collab start` | 显示欢迎消息 |
| 困惑检测 | Agent 表达困惑 | 加载协作指南 |

---

## 3. 用户体验设计

### 3.1 场景一：新 Agent 加入项目

```
$ cd financial-case-generator-system

=== 欢迎使用 OC-Collab ===

项目: 金融案件证据集生成系统
当前阶段: testing
版本: v3.0.0

你的角色: Agent 2

待办任务 (1 项):
1. [P0] 执行黑盒测试 - pending

下一步: 执行测试用例 tests/blackbox/

协作指南摘要:
你的职责:
- 评审需求和设计
- 开发功能代码
- 编写白盒测试
- 签署确认

输入 'oc-collab status' 查看详情
输入 'oc-collab todo' 查看待办
```

### 3.2 场景二：Session 重启

```
$ oc-collab start

=== OC-Collab 会话启动 ===

欢迎回来！

当前状态:
- 项目: 金融案件证据集生成系统
- 阶段: testing
- 你的角色: Agent 2

继续上次工作...
待办任务: 1 项

输入 'oc-collab todo' 查看详情
```

### 3.3 场景三：Agent 困惑时

```
Human: 我不知道该做什么

=== 协作指南建议 ===

根据当前阶段 (testing)，你的下一步是:

1. 执行黑盒测试
   文件: tests/blackbox/test_v3_evidence_flow.py
   命令: pytest tests/blackbox/

2. 查看待办
   命令: oc-collab todo

3. 查看协作指南
   文件: skills/oc_collab_collaboration_guide/content.md
```

---

## 4. 验收标准

| 验收项 | 标准 |
|--------|------|
| 自动触发 | Agent 进入项目目录时自动显示欢迎消息 |
| 消息完整性 | 欢迎消息包含项目状态、角色、待办、下一步 |
| 协作指南 | 显示协作指南摘要，提供入口 |
| CLI 命令 | `oc-collab start` 命令可用 |
| 测试覆盖 | 单元测试覆盖欢迎消息生成逻辑 |

---

## 5. 实施建议

### 5.1 版本规划

| 版本 | 功能 | 说明 |
|------|------|------|
| v2.2.2 | Session 启动自动引导 | 本提案功能 |

### 5.2 依赖关系

| 依赖 | 说明 |
|------|------|
| M5 CognitiveImmuneSystem | SessionStarter 扩展 |
| M4 ExtendedChecklistGenerator | Checklist 生成 |
| Skill Loader | 协作指南加载 |

### 5.3 工时预估

| 任务 | 工时 |
|------|------|
| SessionStarter 扩展 | 4h |
| CLI start 命令 | 2h |
| 单元测试 | 2h |
| E2E 测试 | 2h |
| **合计** | **10h** |

---

## 6. 价值总结

### 6.1 用户体验提升

| 方面 | 改进前 | 改进后 |
|------|--------|--------|
| 新 Agent 加入 | 不知道怎么做 | 自动引导 |
| Session 重启 | 需要手动查看 | 自动恢复 |
| 困惑时 | 依赖自觉查找 | 自动建议 |

### 6.2 核心价值

```
Session 启动自动引导 = 新 Agent 的"入门教程"
```

**解决的问题**：
- Agent 无法快速上手的问题
- Agent 不知道协作流程的问题
- Agent 学习曲线陡峭的问题

---

## 签署确认

### Agent 2 确认

| 确认项 | 内容 |
|--------|------|
| 文档版本 | v1 |
| 创建日期 | 2026-02-07 |
| 核心功能 | Session 启动自动引导 Agent |

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-07 | ✅ |

### Agent 1 评审

Agent 1 可选择性提出意见，无需强制回复。

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | | ⏳ （开放讨论） |

---

**文档版本**: v1
**创建日期**: 2026-02-07
**状态**: 待评审（开放讨论，可选择性回应）
