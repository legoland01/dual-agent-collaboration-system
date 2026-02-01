# 概要设计说明书：oc-collab v2.2.0

**版本**: v1
**创建日期**: 2026-02-01
**作者**: Agent 1 (产品经理/架构师)
**版本号**: 2.2.0
**状态**: 概要设计 (待 Agent 2 评审)

---

## 1. 技术架构概览

### 1.1 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         oc-collab 系统架构                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │  Agent 1    │    │  Agent 2    │    │  其他 Agent │            │
│  │ (PM/架构师)  │    │  (开发Lead) │    │  (动态添加)  │            │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘            │
│         │                  │                  │                     │
│         └──────────────────┼──────────────────┘                     │
│                            │                                        │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Git 通信协议层                            │   │
│  │  ├─ 需求文档 (requirements_*.md)                            │   │
│  │  ├─ 设计文档 (detailed_design_*.md)                         │   │
│  │  ├─ 状态文件 (project_state.yaml)                           │   │
│  │  └─ 会议纪要 (MEETING_NOTES_*.md)                           │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            │                                        │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    核心功能模块                              │   │
│  │  ├─ AgentManager: Agent 动态管理                            │   │
│  │  ├─ ProjectManager: 项目管理 (任务分配、进度)                │   │
│  │  ├─ ResourceLock: 资源锁管理                                │   │
│  │  ├─ MeetingManager: 会议管理                                │   │
│  │  └─ StoryE2ETests: 用户故事 E2E 测试                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            │                                        │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    底层支撑模块 (v2.1.0)                     │   │
│  │  ├─ StateValidator/StateMigrator                            │   │
│  │  ├─ ExceptionHandler/ResourceMonitor                        │   │
│  │  └─ GitWorkflowEnforcer                                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 1.2 技术选型

| 模块 | 技术/依赖 | 说明 |
|------|----------|------|
| Agent 管理 | 动态加载 | Agent 配置文件管理 |
| 状态管理 | YAML + StateValidator | 持久化状态 |
| Git 通信 | GitPython / subprocess | Git 操作封装 |
| 资源锁 | 文件锁 + 超时机制 | 30 分钟超时 |
| E2E 测试 | pytest + Playwright | 用户故事测试 |

---

## 2. 多 Agent 动态管理设计

### 2.1 Agent 角色体系

```python
class AgentRole(Enum):
    PRODUCT_MANAGER = "product_manager"    # 产品经理 (Agent 1)
    DEV_LEAD = "dev_lead"                  # 开发负责人 (Agent 2)
    FRONTEND_DEV = "frontend_dev"          # 前端开发
    BACKEND_DEV = "backend_dev"            # 后端开发
    DESIGNER = "designer"                  # 设计师
    TESTER = "tester"                      # 测试
```

### 2.2 Agent 配置结构

```yaml
agents:
  - id: "agent1"
    role: "product_manager"
    name: "产品经理"
    responsibilities:
      - "CREATE_REQUIREMENTS"
      - "REVIEW_DESIGN"
      - "SIGN_OFF"
      - "MANAGE_PROJECT"
    forbidden:
      - "WRITE_CODE"
  
  - id: "agent2"
    role: "dev_lead"
    name: "开发负责人"
    responsibilities:
      - "REVIEW_REQUIREMENTS"
      - "CREATE_DESIGN"
      - "WRITE_CODE"
      - "CODE_REVIEW"
    forbidden:
      - "CREATE_REQUIREMENTS"
```

### 2.3 核心类设计

```python
class AgentManager:
    """Agent 动态管理器。"""
    
    def __init__(self, config_path: str = "config/agents.yaml"):
        self.config_path = Path(config_path)
        self.agents: Dict[str, AgentConfig] = {}
        self._load_agents()
    
    def add_agent(self, agent_config: AgentConfig) -> bool:
        """添加 Agent。"""
        if agent_config.id in self.agents:
            return False
        self.agents[agent_config.id] = agent_config
        self._save_agents()
        return True
    
    def remove_agent(self, agent_id: str) -> bool:
        """移除 Agent。"""
        if agent_id not in self.agents:
            return False
        del self.agents[agent_id]
        self._save_agents()
        return True
    
    def get_agent(self, agent_id: str) -> Optional[AgentConfig]:
        """获取 Agent 配置。"""
        return self.agents.get(agent_id)
    
    def list_agents(self, role: AgentRole = None) -> List[AgentConfig]:
        """列出 Agent。"""
        agents = list(self.agents.values())
        if role:
            agents = [a for a in agents if a.role == role]
        return agents
    
    def check_permission(self, agent_id: str, action: str) -> bool:
        """检查权限。"""
        agent = self.get_agent(agent_id)
        if not agent:
            return False
        return action in agent.responsibilities


@dataclass
class AgentConfig:
    """Agent 配置。"""
    id: str
    role: AgentRole
    name: str
    responsibilities: List[str]
    forbidden: List[str]
    enabled: bool = True
```

### 2.4 命令设计

```bash
# 添加 Agent
oc-collab agent add --role frontend --tech react --name "React Developer"

# 移除 Agent
oc-collab agent remove --agent agent_frontend_react

# 列出 Agent
oc-collab agent list
oc-collab agent list --role backend

# 查看 Agent 详情
oc-collab agent show --agent agent2

# 检查权限
oc-collab agent check --agent agent1 --action CREATE_REQUIREMENTS
```

---

## 3. 多技术栈协同设计

### 3.1 技术栈定义

```python
@dataclass
class TechStack:
    """技术栈定义。"""
    frontend: List[str] = field(default_factory=list)  # react, vue, angular
    backend: List[str] = field(default_factory=list)   # nodejs, go, java, python
    database: List[str] = field(default_factory=list)  # postgresql, mysql, mongodb
    deployment: List[str] = field(default_factory=list) # docker, k8s
```

### 3.2 多仓库协作

```yaml
repositories:
  frontend:
    url: "https://github.com/project/frontend"
    tech_stack: "react"
    agent: "agent_frontend_react"
  
  backend:
    url: "https://github.com/project/backend"
    tech_stack: "go"
    agent: "agent_backend_go"
  
  shared:
    url: "https://github.com/project/shared"
    tech_stack: "typescript"
    agent: "agent2"
```

### 3.3 接口规范管理

```python
class APIManager:
    """API 接口管理器。"""
    
    def __init__(self, spec_path: str = "api/openapi.yaml"):
        self.spec_path = Path(spec_path)
        self.spec: Dict = {}
        self._load_spec()
    
    def generate_mock(self, output_dir: str = "mocks/") -> None:
        """生成 Mock 数据。"""
        pass
    
    def validate_implementation(self, impl_path: str) -> List[str]:
        """验证实现与接口规范一致。"""
        pass
    
    def update_from_backend(self, agent_id: str) -> None:
        """从后端 Agent 更新接口规范。"""
        pass
```

---

## 4. Git 通信协议设计

### 4.1 通信类型

| 类型 | 触发条件 | 参与者 | 说明 |
|------|----------|--------|------|
| 需求评审 | 提交需求文档 | Agent 1 → Agent 2 | Agent 1 创建，Agent 2 评审 |
| 设计评审 | 提交设计文档 | Agent 2 → Agent 1 | Agent 2 创建，Agent 1 评审 |
| 任务分配 | 分配新任务 | Agent 1 → 指定 Agent | 通过 Git Issue 通知 |
| 代码评审 | 提交 PR | Agent 2 / 其他 Agent → Agent 2 | 代码评审请求 |
| 里程碑签署 | 里程碑完成 | Agent 1 | 签署确认 |

### 4.2 通信格式

```yaml
# Git Issue 格式 (任务分配)
issue:
  title: "[Task] TASK-001 用户登录功能"
  body: |
    ## 任务描述
    实现用户登录功能
    
    ## 验收标准
    - [ ] 用户可以使用用户名密码登录
    - [ ] 登录失败显示错误提示
    - [ ] 支持记住登录状态
    
    ## 依赖
    - 无
    
    ## 分配
    @agent_frontend_react
    
  labels: ["task", "frontend"]
  assignees: ["agent_frontend_react"]

# Git Comment 格式 (签署确认)
comment:
  body: |
    ## 签署确认
    
    **里程碑**: M1
    **签署人**: Agent 1
    **日期**: 2026-02-01
    
    ### 检查项
    - [x] 代码质量检查通过
    - [x] 功能完整性检查通过
    - [x] 测试覆盖检查通过
    
    **状态**: ✅ 批准
```

### 4.3 状态同步机制

```python
class GitSyncManager:
    """Git 同步管理器。"""
    
    def __init__(self, repo_path: str = "."):
        self.repo = GitRepository(repo_path)
    
    def sync_state(self, state_file: str = "state/project_state.yaml") -> bool:
        """同步状态文件。"""
        try:
            # Pull 最新状态
            self.repo.pull(state_file)
            
            # 读取并验证
            with open(state_file, 'r') as f:
                state = yaml.safe_load(f)
            
            # 验证状态
            validator = StateValidator()
            if not validator.validate(state):
                return False
            
            return True
        except Exception as e:
            logger.error(f"状态同步失败: {e}")
            return False
    
    def push_changes(self, files: List[str], message: str) -> bool:
        """推送变更。"""
        pass
```

---

## 5. 项目管理增强设计

### 5.1 任务管理

```python
class TaskStatus(Enum):
    """任务状态。"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """任务。"""
    id: str
    title: str
    description: str
    assignee: str  # Agent ID
    status: TaskStatus
    feature_id: str  # 关联的 Feature
    dependencies: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


class ProjectManager:
    """项目管理器。"""
    
    def __init__(self, state_file: str = "state/project_state.yaml"):
        self.state_file = state_file
        self.tasks: Dict[str, Task] = {}
        self._load_tasks()
    
    def create_task(self, task: Task) -> bool:
        """创建任务。"""
        if task.id in self.tasks:
            return False
        self.tasks[task.id] = task
        self._save_tasks()
        return True
    
    def assign_task(self, task_id: str, agent_id: str) -> bool:
        """分配任务。"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        task.assignee = agent_id
        self._save_tasks()
        return True
    
    def set_dependency(self, task_id: str, depends_on: List[str]) -> bool:
        """设置依赖。"""
        task = self.tasks.get(task_id)
        if not task:
            return False
        task.dependencies = depends_on
        self._save_tasks()
        return True
    
    def check_circular_dependency(self) -> Optional[List[str]]:
        """检查循环依赖。"""
        # 使用 DFS 检测循环
        pass
    
    def get_progress(self) -> Dict[str, Any]:
        """获取进度。"""
        pass
```

### 5.2 资源锁管理

```python
class ResourceLockManager:
    """资源锁管理器。"""
    
    DEFAULT_TIMEOUT = 30 * 60  # 30 分钟
    
    def __init__(self, lock_dir: str = "state/locks"):
        self.lock_dir = Path(lock_dir)
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        self.active_locks: Dict[str, LockInfo] = {}
    
    def acquire(self, resource_type: str, resource_id: str, agent_id: str) -> bool:
        """获取锁。"""
        lock_key = f"{resource_type}:{resource_id}"
        
        if lock_key in self.active_locks:
            if self.active_locks[lock_key].agent_id != agent_id:
                return False  # 已被其他 Agent 锁定
        
        self.active_locks[lock_key] = LockInfo(
            resource_type=resource_type,
            resource_id=resource_id,
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
            timeout=self.DEFAULT_TIMEOUT
        )
        self._save_lock(lock_key, self.active_locks[lock_key])
        return True
    
    def release(self, resource_type: str, resource_id: str, agent_id: str) -> bool:
        """释放锁。"""
        lock_key = f"{resource_type}:{resource_id}"
        if lock_key not in self.active_locks:
            return False
        if self.active_locks[lock_key].agent_id != agent_id:
            return False
        
        del self.active_locks[lock_key]
        self._remove_lock(lock_key)
        return True
    
    def check_timeout(self) -> List[str]:
        """检查超时锁并自动释放。"""
        expired = []
        for lock_key, lock_info in self.active_locks.items():
            if lock_info.is_expired():
                expired.append(lock_key)
                del self.active_locks[lock_key]
                self._remove_lock(lock_key)
        return expired
    
    def get_status(self, resource_type: str = None, resource_id: str = None) -> List[LockInfo]:
        """获取锁状态。"""
        pass


@dataclass
class LockInfo:
    """锁信息。"""
    resource_type: str
    resource_id: str
    agent_id: str
    timestamp: str
    timeout: int
    
    def is_expired(self) -> bool:
        """检查是否超时。"""
        lock_time = datetime.fromisoformat(self.timestamp)
        return (datetime.now() - lock_time).total_seconds() > self.timeout
```

---

## 6. 会议管理设计

### 6.1 会议结构

```python
@dataclass
class Meeting:
    """会议。"""
    id: str  # MTG-001
    title: str
    participants: List[str]
    version: str  # 关联版本
    date: str
    decisions: List[str]  # 关键决策
    action_items: List[str]  # 待办事项
    attachments: List[str]  # 附件路径


class MeetingManager:
    """会议管理器。"""
    
    MEETINGS_DIR = "state/meetings"
    
    def __init__(self):
        self.meetings_dir = Path(self.MEETINGS_DIR)
        self.meetings_dir.mkdir(parents=True, exist_ok=True)
        self.meetings: Dict[str, Meeting] = {}
        self._load_meetings()
    
    def create_meeting(self, title: str, participants: List[str], version: str) -> Meeting:
        """创建会议。"""
        meeting_id = f"MTG-{len(self.meetings) + 1:03d}"
        meeting = Meeting(
            id=meeting_id,
            title=title,
            participants=participants,
            version=version,
            date=datetime.now().isoformat(),
            decisions=[],
            action_items=[],
            attachments=[]
        )
        self.meetings[meeting_id] = meeting
        self._save_meeting(meeting)
        return meeting
    
    def upload_attachment(self, meeting_id: str, file_path: str) -> bool:
        """上传会议附件。"""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return False
        
        # 复制文件到会议目录
        dest_path = self.meetings_dir / meeting_id / Path(file_path).name
        shutil.copy(file_path, dest_path)
        meeting.attachments.append(str(dest_path))
        self._save_meeting(meeting)
        return True
    
    def generate_summary(self, meeting_id: str) -> str:
        """生成会议纪要。"""
        meeting = self.meetings.get(meeting_id)
        if not meeting:
            return ""
        
        summary = f"""# 会议纪要: {meeting.title}

**会议编号**: {meeting.id}
**日期**: {meeting.date}
**版本**: {meeting.version}
**参与者**: {', '.join(meeting.participants)}

## 关键决策
{chr(10).join(f'- {d}' for d in meeting.decisions)}

## 待办事项
{chr(10).join(f'- [ ] {item}' for item in meeting.action_items)}

## 附件
{chr(10).join(f'- {a}' for a in meeting.attachments)}
"""
        return summary
    
    def list_by_version(self, version: str) -> List[Meeting]:
        """按版本列出会议。"""
        return [m for m in self.meetings.values() if m.version == version]
```

### 6.2 命令设计

```bash
# 创建会议
oc-collab meeting create --title "v2.2.0 需求讨论" --version v2.2.0 --participants agent1,agent2

# 上传会议录音
oc-collab meeting upload --meeting MTG-001 --file recording.mp3

# 列出会议
oc-collab meeting list
oc-collab meeting list --version v2.2.0

# 显示会议详情
oc-collab meeting show --meeting MTG-001

# 生成会议纪要
oc-collab meeting summary --meeting MTG-001 --output MEETING_NOTES_MTG-001.md
```

---

## 7. 用户故事 E2E 测试设计

### 7.1 测试组织结构

```
tests/
└── test_stories/
    ├── __init__.py
    ├── conftest.py              # fixtures (login, session, etc.)
    ├── test_story_S001_login.py
    ├── test_story_S002_register.py
    └── test_story_S003_xxx.py
```

### 7.2 测试模板

```python
import pytest
from src.core.story_runner import StoryRunner


class TestStoryS001Login:
    """Story S-001: 用户登录"""
    
    @pytest.fixture
    def story_runner(self):
        return StoryRunner()
    
    def test_login_success(self, story_runner):
        """测试登录成功场景。"""
        result = story_runner.run(
            story_id="S001",
            scenario="login_success",
            user_data={
                "username": "test_user",
                "password": "correct_password"
            }
        )
        assert result.success
        assert result.message == "登录成功"
    
    def test_login_wrong_password(self, story_runner):
        """测试密码错误场景。"""
        result = story_runner.run(
            story_id="S001",
            scenario="login_wrong_password",
            user_data={
                "username": "test_user",
                "password": "wrong_password"
            }
        )
        assert not result.success
        assert "密码错误" in result.message
    
    def test_login_account_locked(self, story_runner):
        """测试账户锁定场景。"""
        result = story_runner.run(
            story_id="S001",
            scenario="login_account_locked",
            user_data={
                "username": "locked_user",
                "password": "any_password"
            }
        )
        assert not result.success
        assert "账户已锁定" in result.message
```

### 7.3 Story 运行器

```python
class StoryRunner:
    """Story 运行器。"""
    
    def __init__(self):
        self.stories_dir = Path("docs/stories")
    
    def run(self, story_id: str, scenario: str, user_data: Dict) -> StoryResult:
        """运行 Story 场景。"""
        # 加载 Story 定义
        story = self._load_story(story_id)
        
        # 找到场景定义
        scenario_def = story.get_scenario(scenario)
        
        # 执行场景
        result = StoryResult(story_id=story_id, scenario=scenario)
        for step in scenario_def.steps:
            step_result = self._execute_step(step, user_data)
            result.add_step_result(step_result)
            if not step_result.success:
                break
        
        return result
    
    def _execute_step(self, step: StoryStep, user_data: Dict) -> StepResult:
        """执行步骤。"""
        pass
```

---

## 8. 待确认问题清单

### 8.1 技术决策问题

| 问题 | 说明 | 负责人 |
|------|------|--------|
| Agent 动态添加的实现方式 | 使用配置文件还是数据库？ | Agent 2 |
| 资源锁的存储方式 | 文件还是 Redis？ | Agent 2 |
| E2E 测试框架选择 | Playwright vs Selenium？ | Agent 2 |
| 多仓库协作的同步机制 | 手动还是自动？ | Agent 2 |

### 8.2 设计问题

| 问题 | 说明 | 负责人 |
|------|------|--------|
| Story 的详细模板 | 是否需要更复杂的结构？ | Agent 1 |
| 会议导入的自动化程度 | 录音转写是否需要集成 ASR？ | Agent 1 |
| 反馈自动路由的规则 | 是否有机器学习空间？ | Agent 1 |

---

## 9. 依赖关系

### 9.1 内部依赖

| 模块 | 依赖 | 说明 |
|------|------|------|
| AgentManager | StateValidator | Agent 状态验证 |
| ProjectManager | ResourceLock | 任务锁定 |
| MeetingManager | StateManager | 状态持久化 |
| StoryE2ETests | StateValidator | 状态验证 |

### 9.2 外部依赖

| 依赖 | 用途 | 最低版本 |
|------|------|---------|
| GitPython | Git 操作 | 3.1.0 |
| pytest | 测试框架 | 7.0.0 |
| PyYAML | 配置解析 | 6.0 |

---

## 10. 里程碑规划

| 里程碑 | 内容 | 交付物 |
|--------|------|--------|
| M1 | Agent 动态管理 | agent_manager.py, tests |
| M2 | 项目管理增强 | project_manager.py, resource_lock.py, tests |
| M3 | 会议管理 | meeting_manager.py, tests |
| M4 | 用户故事 E2E | story_e2e_tests.py |
| M5 | 集成测试 | 完整测试套件 |

---

## 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|-----|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-01 | 待签署 |
| 开发负责人 | Agent 2 | 2026-02-01 | 待签署 |

---

**创建人**: Agent 1
**日期**: 2026-02-01
**状态**: 概要设计 (待 Agent 2 评审)
