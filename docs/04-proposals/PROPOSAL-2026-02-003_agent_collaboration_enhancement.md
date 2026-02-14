# Proposal: oc-collab Agent协作增强机制

**提案人**: Agent 1  
**日期**: 2026-02-13  
**目标版本**: v2.2.9 或后续版本  
**状态**: 待评审  
**关联**:
- BUG-20260213-002
- BUG-20260213-003
- PROPOSAL-2026-02-002 (自动Bug报告机制)

---

## 1. 问题背景

### 1.1 当前协作模式

```
Agent2 → TODO → Agent1 → 完成旧 + 创建新 → Agent2继续执行
```

**痛点**：
1. Agent不知道有新TODO（无通知机制）
2. Agent不知道Skill已更新（无热更新机制）
3. 多Agent场景下协作依赖断裂

### 1.2 BUG-20260213-002/003 教训

| 问题 | 当前解决 | 缺失 |
|------|----------|------|
| Agent不自觉自检 | 创建Skill `oc_collab_todo_dependency_check` | 无自动执行机制 |
| 协作通知不及时 | 更新Skill `oc_collab_collaboration_guide` | 无新TODO自动通知机制 |
| Skill更新不生效 | 手动告知 | 无自动同步机制 |

---

## 2. 解决方案

### 2.1 核心机制

```
┌─────────────────────────────────────────────────────────┐
│                    oc-collab 协作增强机制                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────┐    ┌─────────────────┐           │
│  │ Skill更新检测    │ →  │ Agent通知        │           │
│  │ (定时/触发)      │    │ (Webhook/API)    │           │
│  └────────┬────────┘    └────────┬────────┘           │
│           │                      │                      │
│           ▼                      ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐           │
│  │ 新TODO检测     │ →  │ 启动自检        │           │
│  │ (状态监控)       │    │ (新任务前检查)   │           │
│  └─────────────────┘    └─────────────────┘           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### 2.2 机制1：Skill热更新

#### 2.2.1 触发方式

| 触发方式 | 说明 | 优点 | 缺点 |
|----------|------|------|------|
| **A. 每次任务前加载** | 执行任务前先加载最新Skill | 简单可靠 | 每次都加载，性能开销 |
| **B. Git Hook** | Skill文件变更时触发 | 实时 | 需要Git集成 |
| **C. 定时轮询** | 定时检查Skill变更 | 实时性好 | 需要后台服务 |

**推荐**：方案A（每次任务前加载）+ 方案B（Git Hook）

#### 2.2.2 实现方案

```python
# 伪代码：任务执行前加载Skill

class TaskExecutor:
    """任务执行器"""

    def execute_task(self, task):
        """执行任务"""

        # Step 1: 加载最新Skill
        skill = self._load_latest_skill(task.skill_id)
        if skill.updated_at > self.cached_skill.updated_at:
            self._notify_agents(skill)

        # Step 2: 加载依赖的TODO
        dependencies = self._load_dependencies(task)

        # Step 3: 检查是否有被阻塞的前置TODO
        blocked = self._check_blocked_dependencies(dependencies)
        if blocked:
            raise Error(f"任务被阻塞：存在未完成的TODO: {blocked}")

        # Step 4: 执行任务
        result = self._execute(task, skill)

        return result

    def _load_latest_skill(self, skill_id):
        """加载最新Skill"""
        # 从Git远程加载，或从本地文件系统加载
        return SkillLoader.load(skill_id)

    def _notify_agents(self, skill):
        """通知所有Agent Skill已更新"""
        message = {
            "type": "SKILL_UPDATED",
            "skill_id": skill.id,
            "updated_at": skill.updated_at,
            "changelog": skill.changelog
        }
        NotificationService.broadcast(message)
```

#### 2.2.3 Skill结构增强

```json
{
  "id": "oc_collab_todo_dependency_check",
  "name": "OC-Collab TODO依赖检查",
  "version": "1.1",
  "updated_at": "2026-02-13T18:00:00Z",
  "changelog": [
    {
      "version": "1.1",
      "date": "2026-02-13",
      "changes": ["新增：新TODO创建检测"]
    }
  ],
  "triggers": [
    {
      "condition": "todo_received",
      "priority": "high",
      "execution_mode": "before_task"
    }
  ]
}
```

### 2.3 机制2：新TODO创建通知

#### 2.3.1 核心原则

**根据Skill `oc_collab_collaboration_guide` v2.2.14**：
- ✅ 完成旧TODO（status: completed，result记录原因）
- ✅ 创建新TODO（包含明确要求，status: pending）
- ✅ 通知对方有新TODO

**不是"退回"，而是"完成+新建"**

#### 2.3.2 决策讨论：为何选择"完成+新建"而非"退回"

**背景**：在讨论TODO处理流程时，有两种方案：

| 方案 | 说明 |
|------|------|
| **退回方案** | 保留原TODO，标记rejection_reason + rejection_action |
| **完成+新建方案** | 完成旧TODO，创建新TODO |

**退回方案的复杂度分析**：

```
退回方案的问题：
1. Agent收到"退回"的TODO → 认为已完成
2. 完成工作后发起新版本 → Agent1可能忽视"已完成"的TODO
3. 需要额外机制标记"已完成≠已处理"
4. 需要通知体系告知Agent1有新版本

结论：退回方案需要复杂的通知和标记体系
```

**最终选择"完成+新建"的原因**：

| 维度 | 退回方案 | 完成+新建 |
|------|----------|-----------|
| 状态清晰度 | 已完成≠已处理（混淆） | 新TODO=明确下一步 |
| 通知机制 | 需要 | 不需要 |
| 依赖检测 | 复杂 | 简单 |
| Agent认知 | 需要理解"退回"语义 | 新TODO就是下一步 |

**核心原则**：新TODO本身就是最清晰的行动指引，无需额外机制。

---

#### 2.3.3 实现代码

```python
class TodoService:
    """TODO服务"""

    def complete_and_create_new(self, old_todo_id, new_content, to_agent, requirements):
        """完成旧TODO + 创建新TODO"""

        # 1. 完成旧TODO
        old_todo = self._get_todo(old_todo_id)
        old_todo.status = "completed"
        old_todo.result = f"已完成，创建新TODO继续处理"

        # 2. 创建新TODO
        new_todo = self._create_todo(
            content=new_content,
            from_agent=self.current_agent,
            to_agent=to_agent,
            requirements=requirements
        )

        # 3. 通知接收者
        NotificationService.notify(
            agent=to_agent,
            type="NEW_TODO",
            todo_id=new_todo.id,
            from_agent=self.current_agent,
            requirements=requirements
        )

        return new_todo
```

#### 2.3.4 Agent启动自检

```python
class Agent:
    """Agent基类"""

    def on_startup(self):
        """启动时自检"""

        # 1. 检查所有分配给自己的TODO
        todos = TodoService.query(to=self.id)

        # 2. 查找新创建的TODO（from != to）
        new_todos = [t for t in todos if t.from_agent != t.to_agent]
        if new_todos:
            self._log(f"收到{len(new_todos)}个新TODO")

        # 3. 按优先级处理
        for todo in new_todos:
            self._handle_new_todo(todo)

    def before_task(self, task):
        """任务执行前检查"""

        # 1. 加载最新Skill
        skill = self._load_latest_skill(task.skill_id)

        # 2. 检查是否有未完成的前置TODO
        blocked = self._check_blocked_dependencies(task)
        if blocked:
            raise Error(f"任务被阻塞：存在未完成的前置TODO: {blocked}")
```

### 2.4 机制3：多Agent依赖管理

#### 2.4.1 TODO依赖图

```python
class TodoDependency:
    """TODO依赖图"""

    def __init__(self):
        self.graph = {}  # todo_id -> [dependencies]

    def add_dependency(self, todo_id, depends_on):
        """添加依赖"""
        if todo_id not in self.graph:
            self.graph[todo_id] = []
        self.graph[todo_id].append(depends_on)

    def is_blocked(self, todo_id):
        """检查是否被阻塞"""
        deps = self.graph.get(todo_id, [])
        for dep in deps:
            dep_todo = self._get_todo(dep)
            if dep_todo.status == "rejected":
                return True
        return False

    def get_blocking_todos(self, todo_id):
        """获取阻塞的TODO"""
        deps = self.graph.get(todo_id, [])
        blocked = []
        for dep in deps:
            dep_todo = self._get_todo(dep)
            if dep_todo.status == "rejected":
                blocked.append(dep_todo)
        return blocked
```

#### 2.4.2 创建TODO时检查依赖

```python
class TodoService:
    def create_todo(self, task, depends_on=None):
        """创建TODO"""

        # 1. 如果有前置依赖，检查前置状态
        if depends_on:
            dep_todo = self._get_todo(depends_on)
            if dep_todo.status == "rejected":
                raise Error(f"无法创建TODO：前置TODO-{depends_on}未完成")

        # 2. 创建TODO
        todo = self._create(task)

        # 3. 添加依赖关系
        if depends_on:
            DependencyGraph.add_dependency(todo.id, depends_on)

        return todo
```

---

## 3. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     oc-collab Agent协作增强系统                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │ Skill管理器      │    │ TODO管理器       │                   │
│  │ ├─ 加载          │    │ ├─ 创建          │                   │
│  │ ├─ 版本控制       │    │ ├─ 状态管理      │                   │
│  │ └─ 变更检测       │    │ └─ 依赖图       │                   │
│  └────────┬────────┘    └────────┬────────┘                   │
│           │                       │                             │
│           ▼                       ▼                             │
│  ┌─────────────────────────────────────────────────┐          │
│  │              通知服务 (NotificationService)        │          │
│  │ ├─ Skill更新通知                                  │          │
│  │ ├─ 新TODO创建通知                                  │          │
│  │ └─ 阻塞解除通知                                   │          │
│  └────────────────┬────────────────┬────────────────┘          │
│                   │                │                           │
│                   ▼                ▼                           │
│           ┌─────────────┐  ┌─────────────┐                  │
│           │ Agent 1     │  │ Agent 2     │                  │
│           │ ├─ 启动自检  │  │ ├─ 启动自检  │                  │
│           │ └─ 任务前检查 │  │ └─ 任务前检查 │                  │
│           └─────────────┘  └─────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. 验收标准

- [ ] Skill更新后，Agent能自动加载最新版本
- [ ] 创建新TODO时，接收者能收到通知
- [ ] Agent启动时能检查新TODO
- [ ] 任务执行前能检查依赖状态
- [ ] 被阻塞的任务能清晰显示原因

---

## 5. 工时估算

| 阶段 | 任务 | 工时 |
|------|------|------|
| 需求分析 | 协作增强机制需求 | 1h |
| 概要设计 | 通知服务架构设计 | 2h |
| 详细设计 | 通知协议、依赖图设计 | 2h |
| 开发 | Skill管理器（热更新） | 3h |
| 开发 | 新TODO创建通知 | 2h |
| 开发 | Agent自检机制 | 2h |
| 开发 | 依赖图管理 | 2h |
| 测试 | 集成测试 | 2h |
| **合计** | | **16h** |

---

## 6. 与PROPOSAL-2026-02-002的关系

| 提案 | 范围 | 关系 |
|------|------|------|
| PROPOSAL-2026-02-002 | 自动Bug报告机制 | 独立 |
| **本提案** | **Agent协作增强机制** | 独立，但可互补 |

**本提案解决的问题**：
1. Skill更新不生效 → Skill热更新
2. 协作通知不及时 → 新TODO创建时自动通知 + 启动自检
3. 多Agent依赖断裂 → 依赖图 + 阻塞检测

---

## 7. 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| 通知延迟 | Agent不能及时知道新TODO | 实时WebSocket通知 |
| 循环依赖 | TODO依赖环 | 依赖图检测循环 |
| 性能开销 | 每次任务加载Skill | 增量加载 + 缓存 |

---

**创建人**: Agent 1  
**日期**: 2026-02-13  
**状态**: 待评审
