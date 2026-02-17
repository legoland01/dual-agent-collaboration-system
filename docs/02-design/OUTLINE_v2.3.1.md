# 概要设计说明书：oc-collab v2.3.1

**版本**: v1  
**创建日期**: 2026-02-16  
**作者**: Agent 1 (产品经理)  
**版本号**: v2.3.1  
**状态**: DRAFT → READY

**关联需求**: requirements_v2.3.1.md

**关联Proposal**: 
- `PROPOSAL_2026-02-026_agent_id_and_role_rename.md` (Agent身份体系)
- `PROPOSAL_2026-02-017_todo_communication_system.md` (通信系统)

---

## 1. 功能模块概览

### 1.1 功能模块清单

| 模块 | 子功能 | 描述 | 优先级 |
|------|--------|------|--------|
| TODO应用层 | 编号优化 | 多Agent编号格式 TODO-XtoY-xxx | P0 |
| TODO应用层 | 向后兼容 | 旧格式自动识别 | P0 |
| TODO应用层 | 来源标签 | source字段区分来源 | P0 |
| TODO应用层 | 模板系统 | 内容模板标准化 | P1 |
| 通信层 | 自动Git同步 | 文档变更自动sync | P0 |
| 通信层 | Agent注册表 | 多Agent信息管理 | P0 |
| 通信层 | ACK确认 | commit message确认 | P1 |

### 1.2 功能模块图

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI 命令层                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ todowrite│  │ todo list│  │ agent    │  │ todo ack │    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘    │
└───────┼─────────────┼─────────────┼─────────────┼──────────┘
        │             │             │             │
┌───────┼─────────────┼─────────────┼─────────────┼──────────┐
│       ▼             ▼             ▼             ▼           │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              TODO 应用层                              │     │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐     │     │
│  │  │TodoIdGen   │ │SourceTag   │ │Template    │     │     │
│  │  │(编号生成)   │ │(来源标签)   │ │(模板系统)   │     │     │
│  │  └────────────┘ └────────────┘ └────────────┘     │     │
│  └─────────────────────────────────────────────────────┘     │
│                              │                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              通信层                                   │     │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐     │     │
│  │  │GitSync     │ │AgentRegistry│ │ACKConfirm  │     │     │
│  │  │(自动同步)   │ │(注册表)    │ │(确认)      │     │     │
│  │  └────────────┘ └────────────┘ └────────────┘     │     │
│  └─────────────────────────────────────────────────────┘     │
│                              │                               │
│  ┌─────────────────────────────────────────────────────┐     │
│  │              状态管理层                                │     │
│  │  ┌────────────────────────────────────────────┐     │     │
│  │  │         project_state.yaml                 │     │     │
│  │  │  - agents: {...}                          │     │     │
│  │  │  - todos: [...]                           │     │     │
│  │  └────────────────────────────────────────────┘     │     │
│  └─────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 功能模块关系

### 2.1 调用关系

| 调用方 | 被调用方 | 说明 |
|--------|----------|------|
| CLI todowrite | TodoIdGenerator | 生成新编号 |
| CLI todowrite | SourceTag | 添加来源 |
| CLI todowrite | Template | 应用模板 |
| CLI agent register | AgentRegistry | 注册Agent |
| CLI todo ack | ACKConfirm | 确认TODO |
| TodoIdGenerator | AgentRegistry | 查询接收者 |

### 2.2 数据依赖

| 数据提供方 | 数据使用方 | 数据类型 |
|------------|------------|----------|
| AgentRegistry | TodoIdGenerator | Agent信息 |
| project_state.yaml | 所有模块 | 状态数据 |
| GitSync | 所有模块 | 变更同步 |

### 2.3 时序关系

| 功能A | 功能B | 说明 |
|-------|-------|------|
| Agent注册 | TODO创建 | 注册完成后才能创建多Agent TODO |
| TODO创建 | ACK确认 | 创建后才能确认 |
| 自动Git同步 | 所有变更 | 先有变更才能同步 |

---

## 3. 详细模块设计

### 3.1 TodoIdGenerator (编号生成)

**职责**: 生成多Agent编号格式

**数据存储**:
- 存储位置: `project_state.yaml` → `todo_id_counters`
- 格式:
```yaml
todo_id_counters:
  "1to2": 5    # Agent1->Agent2的下一个序号
  "1to1": 12   # Agent1->Agent1的序号
  "2to1": 8    # Agent2->Agent1的序号
```

**并发锁机制**:
- 使用文件锁: `state/.todo_id.lock`
- 乐观锁: 读取→修改→写入前检查文件修改时间

**CLI接口**:
```python
# todowrite命令参数
@click.command()
@click.option('--to', '--receiver', 'receiver', required=True, help='接收者Agent ID')
@click.option('--source', '-s', default='MANUAL', help='来源标签')
def todowrite(content, priority, receiver, source):
    # 1. 获取当前Agent (creator)
    # 2. 调用 TodoIdGenerator.generate(creator, receiver)
```

**类设计**:
```python
class TodoIdGenerator:
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.lock_file = "state/.todo_id.lock"
    
    def generate(self, creator: str, receiver: str) -> str:
        """生成 TODO-XtoY-xxx 格式编号"""
        with FileLock(self.lock_file):
            counter = self._get_next_counter(creator, receiver)
            return f"TODO-{creator}to{receiver}-{counter:03d}"
    
    def parse(self, todo_id: str) -> dict:
        """解析编号，返回 dict{creator, receiver, seq, is_legacy}"""
        # 新格式: TODO-(\d+)to(\d+)-(\d+)
        # 旧格式: TODO-(\d+)-(\d+) → receiver = creator
    
    def is_legacy_format(self, todo_id: str) -> bool:
        """判断是否旧格式 TODO-X-xxx"""
        # 正则: TODO-(\d+)-(\d+)
```

### 3.2 SourceTag (来源标签)

**职责**: 管理TODO来源

**自动推断规则**:
- 内容包含"BUG"开头 → BUG
- 内容包含"需求"/"实现" → REQUIREMENT
- 内容包含"反馈" → FEEDBACK
- 其他 → MANUAL

**类设计**:
```python
class SourceTag:
    VALID_SOURCES = ["REQUIREMENT", "BUG", "FEEDBACK", "MANUAL"]
    
    def __init__(self):
        pass
    
    def validate(self, source: str) -> bool:
        """验证来源有效性"""
    
    def get_source_from_context(self, content: str) -> str:
        """自动推断来源"""
        content_lower = content.lower()
        if "bug" in content_lower:
            return "BUG"
        if any(kw in content_lower for kw in ["需求", "实现", "功能"]):
            return "REQUIREMENT"
        if "反馈" in content_lower:
            return "FEEDBACK"
        return "MANUAL"
```

### 3.3 Template (模板系统)

**职责**: TODO内容模板

**配置文件**: `config/templates.yaml`

**模板数据结构** (config/templates.yaml):
```yaml
templates:
  REQUIREMENT:
    content_prefix: "实现"
    required_fields:
      - requirement_id
    optional_fields:
      - acceptance_criteria
  BUG_FIX:
    content_prefix: "修复"
    required_fields:
      - bug_id
      - root_cause
    optional_fields:
      - fix_plan
      - test_case
  MANUAL:
    content_prefix: ""
    required_fields: []
    optional_fields: []
```

**自定义模板**: 支持用户扩展config/templates.yaml

**类设计**:
```python
class TodoTemplate:
    def __init__(self, config_file: str = "config/templates.yaml"):
        self.config_file = config_file
        self._load_templates()
    
    def _load_templates(self):
        """从配置文件加载模板"""
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                self.templates = yaml.safe_load(f)
        else:
            self.templates = DEFAULT_TEMPLATES
    
    def apply(self, template_type: str, context: dict) -> dict:
        """应用模板，返回填充后的字段"""
    
    def list_templates(self) -> list[str]:
        """列出可用模板"""
```

### 3.4 AgentRegistry (Agent注册表)

**职责**: 管理Agent信息

**Role可选值**:
- PRODUCT_MANAGER
- DEVELOPMENT_LEAD
- FRONTEND_DEV
- BACKEND_DEV
- QA_ENGINEER

**环境变量优先级**: CLI参数 > 环境变量 OC_AGENT_ID > Git config

**CLI命令**:
```bash
# 手动注册
oc-collab agent register --id agent3 --role FRONTEND_DEV --team frontend

# 自动注册
oc-collab agent auto-register
# 从 OC_AGENT_ID 环境变量获取 agent_id
# 从 git config user.name 获取 git_name
```

**数据结构** (project_state.yaml):
```yaml
agents:
  agent1:
    id: agent1
    role: DEVELOPMENT_LEAD
    team: internal
    status: active
    git_name: "zhangsan"
    registered_at: "2026-02-16T10:00:00"
```

**并发处理**:
- 重复注册: 覆盖更新
- 已分配TODO的Agent注销: 检查todo列表，有pending则拒绝

**类设计**:
```python
class AgentRegistry:
    def __init__(self, state_file: str):
        self.state_file = state_file
    
    def get_current_agent_id(self) -> str:
        """获取当前Agent ID，优先级: CLI > ENV > Git config"""
        # 1. 检查环境变量 OC_AGENT_ID
        # 2. 检查 git config user.email
    
    def auto_register(self) -> bool:
        """自动注册"""
        agent_id = self.get_current_agent_id()
        role = "DEVELOPMENT_LEAD"  # 默认
        return self.register(agent_id, role)
    
    def register(self, agent_id: str, role: str, team: str = "internal") -> bool:
        """注册Agent"""
    
    def can_unregister(self, agent_id: str) -> bool:
        """检查是否可以注销"""
        # 检查是否有分配给该Agent的pending TODO
    
    def list_agents(self) -> list[dict]:
        """列出所有Agent"""
```

### 3.5 GitSync (自动Git同步)

**职责**: 自动同步变更到远程

**配置文件**: `config/git_sync.yaml`

**触发机制**:
- 文件监控: 使用watchdog库监控state目录文件变化
- 手动触发: `oc-collab sync` 命令

**配置**:
```yaml
# config/git_sync.yaml
enabled: false  # 默认关闭
remotes:
  - origin
  - backup
retry:
  max_attempts: 3
  delay_seconds: 1
```

**失败处理**:
- 单个仓库失败: 继续推送其他仓库，记录失败日志
- 全部失败: 抛出警告但不阻塞主流程
- 重试机制: 最多3次，指数退避

**CLI命令**:
```bash
oc-collab sync          # 手动同步
oc-collab sync --force  # 强制同步
```

**类设计**:
```python
class GitSync:
    def __init__(self, config_file: str = "config/git_sync.yaml"):
        self.config_file = config_file
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            with open(self.config_file) as f:
                self.config = yaml.safe_load(f)
    
    def sync(self, message: str) -> bool:
        """执行 git add + commit + push"""
        if not self.config.get("enabled", False):
            return True  # 跳过
    
    def watch(self):
        """启动文件监控"""
        # 使用watchdog监控state目录
    
    def _push_with_retry(self, remote: str) -> bool:
        """带重试的push"""
```

### 3.6 ACKConfirm (确认机制)

**职责**: TODO确认

**状态机**:
```
draft → pending → acknowledged → completed
                  ↓
               cancelled
```

**ACK触发时机**:
- 自动: `oc-collab todo show <todo_id>` 时自动ACK
- 手动: `oc-collab todo ack <todo_id>`

**Commit标记格式**: `[ACK] TODO-1to2-001 acknowledged by agent2`

**CLI命令**:
```bash
oc-collab todo show <todo_id>  # 查看详情，自动ACK
oc-collab todo ack <todo_id>    # 手动ACK
```

**类设计**:
```python
class ACKConfirm:
    def __init__(self, state_file: str):
        self.state_file = state_file
    
    def auto_ack_on_show(self, todo_id: str, viewer_id: str) -> bool:
        """查看TODO详情时自动ACK"""
        # 检查todo的target_agent是否等于viewer_id
        # 如果是，自动调用acknowledge
    
    def acknowledge(self, todo_id: str, agent_id: str) -> bool:
        """确认收到TODO"""
        # 更新TODO状态为acknowledged
        # 记录acknowledged_by和acknowledged_at
        # commit message: f"[ACK] {todo_id} acknowledged by {agent_id}"
    
    def is_acknowledged(self, todo_id: str) -> bool:
        """检查是否已确认"""
    
    def get_ack_status(self, todo_id: str) -> dict:
        """获取确认状态详情"""
```

### 3.7 合规检查 (ComplianceChecker)

**职责**: 验证TODO操作符合规则

**检查规则**:
- Agent1创建TODO → 必须分配给Agent2
- Agent2创建TODO → 可分配给自己或Agent1
- 新编号格式: TODO-XtoY-xxx
- 旧编号格式: TODO-X-xxx → 视为TODO-XtoX-xxx

**类设计**:
```python
class ComplianceChecker:
    def __init__(self, current_agent: str):
        self.current_agent = current_agent
    
    def check_todo_create(self, todo: dict) -> tuple[bool, str]:
        """检查TODO创建是否符合规则"""
        # 1. 编号格式检查
        # 2. 创建者/接收者关系检查
        # 3. 权限检查
```

---

## 4. 数据流设计

### 4.1 TODO创建流程

```
User → CLI todowrite 
           ↓
    ComplianceChecker.check_todo_create()  ← 新增合规检查
           ↓
    SourceTag.get_source_from_context() / 手动指定
           ↓
    Template.apply()
           ↓
    AgentRegistry.get_agent() 验证接收者
           ↓
    TodoIdGenerator.generate()  获取编号
           ↓ (文件锁)
    StateManager.save()
           ↓
    GitSync.sync()  可选，不阻塞
```

**异常回滚**:
- 如果StateManager.save()失败 → 不推送Git
- 如果GitSync.sync()失败 → 警告但不阻塞

### 4.2 Agent注册流程

```
User → CLI agent register
           ↓
    AgentRegistry.register()
           ↓
    检查是否有pending TODO分配给该Agent
           ↓
    StateManager.update_agents()
           ↓
    GitSync.sync()
```

---

## 5. 产品路线图定位

### 5.1 路线图位置

| 版本 | 功能 | 状态 |
|------|------|------|
| v2.3.0 | 质量保证工具集 | 已完成 |
| v2.3.1 | TODO多Agent支持 | 当前版本 |
| v2.4.0 | Agent扩展 + Skill系统 | 待开发 |

### 5.2 本版本解决的问题

| 问题 | 解决方案 |
|------|----------|
| TODO编号歧义 | TODO-XtoY-xxx 格式明确创建者/接收者 |
| 多Agent协作 | Agent注册表支持动态管理 |
| 任务送达确认 | ACK确认机制 |
| 任务来源不明 | 来源标签追溯 |

---

## 6. 签署确认

### Agent 1 签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | 2026-02-16 | ✅ 创建 |

### Agent 2 签署

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | | |

---

**状态**: DRAFT → READY (Agent1创建) → APPROVED (Agent2评审通过)
