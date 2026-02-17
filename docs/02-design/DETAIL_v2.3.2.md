# 详细设计说明书：oc-collab v2.3.2

**版本**: v1
**创建日期**: 2026-02-17
**作者**: Agent 2 (开发负责人)
**关联概要设计**: OUTLINE_v2.3.2.md
**版本号**: 2.3.2
**状态**: DRAFT → READY

---

## 1. 功能模块映射

### 1.1 映射表

| 功能模块 (概要设计) | 技术模块 (详细设计) | 对应文件 |
|---------------------|---------------------|----------|
| M1: TodoStorage | TodoStorage / TodoRepository | src/core/todo_storage.py |
| M2: DataMigration | DataMigrationService | src/core/data_migration.py |
| M3: AgentListener | AgentListenerService | src/core/agent_listener.py |
| M4: StatusMonitor | AgentStatusMonitor | src/core/status_monitor.py |
| M5: OnlinePuller | OnlinePullerService | src/core/online_puller.py |
| M6: Notification | NotificationService | src/core/notification.py |
| M7: Interaction | InteractionHandler | src/core/interaction_handler.py |
| M8: ConfigManager | ConfigManager | src/core/config_manager.py |

### 1.2 新增/变更文件

| 文件路径 | 功能 | 工时 |
|----------|------|------|
| src/core/todo_storage.py | SQLite存储层 | 4h |
| src/core/data_migration.py | YAML→SQLite迁移 | 2h |
| src/core/agent_listener.py | 守护进程监听 | 3h |
| src/core/status_monitor.py | Agent状态感知 | 2h |
| src/core/online_puller.py | 上线拉取TODO | 2h |
| src/core/notification.py | 实时通知 | 3h |
| src/core/interaction_handler.py | TODO交互处理 | 3h |
| src/core/config_manager.py | 配置管理 | 2h |
| src/cli/listen_commands.py | listen命令 | 1h |
| src/cli/config_commands.py | config命令 | 1h |
| src/cli/notify_commands.py | notify命令 | 1h |
| src/templates/TODO_NOTIFY.md.j2 | Instruction模板 | 0.5h |

---

## 2. 技术架构

### 2.1 模块架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLI Layer                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │ listen_cmds  │ │ config_cmds  │ │   notify_cmds        │  │
│  └──────────────┘ └──────────────┘ └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Core Service Layer                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │TodoStorage   │ │DataMigration │ │   AgentListener      │  │
│  └──────────────┘ └──────────────┘ └──────────────────────┘  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │StatusMonitor │ │Notification   │ │InteractionHandler   │  │
│  └──────────────┘ └──────────────┘ └──────────────────────┘  │
│  ┌──────────────┐ ┌──────────────┐                            │
│  │OnlinePuller  │ │ConfigManager │                            │
│  └──────────────┘ └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐  │
│  │  SQLite DB   │ │   YAML文件   │ │   config/           │  │
│  │  todos.db   │ │ (legacy)     │ │   notification.yaml │  │
│  └──────────────┘ └──────────────┘ └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术选型

| 模块 | 技术/库 | 版本 | 选型依据 |
|------|---------|------|----------|
| 数据库 | SQLite3 | 内置 | 轻量级、内置无需额外依赖 |
| ORM | sqlite3 (原生) | - | 简单高效、减少依赖 |
| 进程管理 | daemonize / subprocess | - | 守护进程模式 |
| 配置 | PyYAML | >=6.0 | 与现有体系一致 |
| 模板 | Jinja2 | >=3.0 | 已有依赖 |

---

## 3. 数据库设计

### 3.1 数据库文件

| 文件路径 | 说明 |
|----------|------|
| state/todos.db | SQLite数据库文件 |
| state/todos.db-journal | SQLite日志文件（自动生成） |

### 3.2 表结构

#### 3.2.1 todos 表 - TODO主表

```sql
CREATE TABLE todos (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled', 'deferred')),
    priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
    sender TEXT,
    receiver TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    completed_at TIMESTAMP,
    deferred_until TIMESTAMP,
    is_read INTEGER DEFAULT 0,
    metadata TEXT
);

-- 索引
CREATE INDEX idx_todos_receiver ON todos(receiver);
CREATE INDEX idx_todos_status ON todos(status);
CREATE INDEX idx_todos_sender ON todos(sender);
CREATE INDEX idx_todos_created_at ON todos(created_at);
CREATE INDEX idx_todos_deferred_until ON todos(deferred_until);
```

**字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | TEXT | TODO唯一标识，格式: TODO-XtoY-NNN |
| content | TEXT | TODO内容 |
| status | TEXT | 状态: pending/in_progress/completed/cancelled/deferred |
| priority | TEXT | 优先级: low/medium/high |
| sender | TEXT | 发送者Agent ID |
| receiver | TEXT | 接收者Agent ID |
| source | TEXT | 来源: MANUAL/AUTO_BUG/SKILL等 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| completed_at | TIMESTAMP | 完成时间 |
| deferred_until | TIMESTAMP | 延迟处理时间 |
| is_read | INTEGER | 是否已读: 0/1 |
| metadata | TEXT | 额外元数据(JSON格式) |

#### 3.2.2 agent_status 表 - Agent在线状态

```sql
CREATE TABLE agent_status (
    agent_id TEXT PRIMARY KEY,
    status TEXT DEFAULT 'offline' CHECK(status IN ('online', 'offline')),
    last_seen_at TIMESTAMP,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| agent_id | TEXT | Agent唯一标识 |
| status | TEXT | 在线状态: online/offline |
| last_seen_at | TIMESTAMP | 最后在线时间 |
| registered_at | TIMESTAMP | 注册时间 |

#### 3.2.3 notifications 表 - 通知历史

```sql
CREATE TABLE notifications (
    id TEXT PRIMARY KEY,
    todo_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_action TEXT,
    user_action_at TIMESTAMP,
    response_time_seconds INTEGER,
    FOREIGN KEY (todo_id) REFERENCES todos(id)
);

CREATE INDEX idx_notifications_todo_id ON notifications(todo_id);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
```

**字段说明**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | TEXT | 通知唯一标识: notif-NNN |
| todo_id | TEXT | 关联的TODO ID |
| created_at | TIMESTAMP | 通知创建时间 |
| user_action | TEXT | 用户操作: executed/deferred/dismissed/viewed |
| user_action_at | TIMESTAMP | 用户操作时间 |
| response_time_seconds | INTEGER | 响应时间(秒) |

### 3.3 数据库初始化

```python
# 首次启动时自动创建表
def init_database(db_path: str = "state/todos.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建todos表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            priority TEXT DEFAULT 'medium',
            sender TEXT,
            receiver TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            completed_at TIMESTAMP,
            deferred_until TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            metadata TEXT
        )
    """)
    
    # 创建agent_status表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_status (
            agent_id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'offline',
            last_seen_at TIMESTAMP,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建notifications表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            todo_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_action TEXT,
            user_action_at TIMESTAMP,
            response_time_seconds INTEGER
        )
    """)
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_receiver ON todos(receiver)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_status ON todos(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_todos_deferred_until ON todos(deferred_until)")
    
    conn.commit()
    conn.close()
```

---

## 4. 核心模块设计

### 4.1 TodoStorage (M1)

```python
class TodoStorage:
    """SQLite存储层"""
    
    def __init__(self, db_path: str = "state/todos.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """初始化数据库和表"""
        conn = sqlite3.connect(self.db_path)
        # 创建表...
        conn.close()
    
    def add(self, todo: dict) -> tuple[bool, str]:
        """
        添加TODO
        Returns: (success, todo_id/error_message)
        """
        pass
    
    def get(self, todo_id: str) -> dict | None:
        """获取单个TODO"""
        pass
    
    def list(
        self, 
        receiver: str = None, 
        status: str = None,
        unread_only: bool = False
    ) -> list[dict]:
        """列出TODO"""
        pass
    
    def update(self, todo_id: str, updates: dict) -> bool:
        """更新TODO"""
        pass
    
    def delete(self, todo_id: str) -> bool:
        """删除TODO"""
        pass
    
    def mark_read(self, todo_id: str) -> bool:
        """标记为已读"""
        pass
    
    def count_unread(self, receiver: str) -> int:
        """统计未读TODO数量"""
        pass
```

### 4.2 DataMigration (M2)

```python
class DataMigrationService:
    """YAML到SQLite迁移服务"""
    
    def __init__(self, storage: TodoStorage):
        self.storage = storage
    
    def migrate(self, yaml_path: str = "state/agent_adhoc_todos.yaml") -> tuple[bool, str]:
        """
        执行迁移
        Returns: (success, message)
        """
        pass
    
    def _parse_yaml(self, yaml_path: str) -> list[dict]:
        """
        解析YAML文件
        Returns: TODO列表
        """
        pass
    
    def _transform_todo(self, todo: dict) -> dict:
        """
        转换TODO格式
        - agent_id -> sender
        - 推断receiver
        - 添加缺失字段
        """
        pass
    
    def _infer_sender_receiver(self, todo: dict) -> tuple[str, str]:
        """
        推断sender和receiver
        - 有agent_id: 使用agent_id作为sender
        - 无agent_id: 标记为unknown
        """
        pass
    
    def backup(self, yaml_path: str) -> str:
        """
        备份原YAML文件
        Returns: 备份文件路径
        """
        pass
    
    def rollback(self, backup_path: str) -> bool:
        """
        回滚迁移
        Returns: success
        """
        pass
```

### 4.2.1 迁移详细流程

```
1. 备份阶段
   ├── 复制 state/agent_adhoc_todos.yaml
   └── 保存为 state/backup/agent_adhoc_todos_YYYYMMDD_HHMMSS.yaml

2. 解析阶段
   ├── 读取YAML文件
   ├── 解析为dict列表
   └── 验证基本结构

3. 转换阶段
   ├── 字段映射:
   │   ├── id → id
   │   ├── content → content
   │   ├── status → status
   │   ├── priority → priority
   │   ├── agent_id → sender (null时为"unknown")
   │   ├── created_at → created_at
   │   └── updated_at → updated_at
   │
   └── 推断sender/receiver:
       ├── agent_id有值 → sender=agent_id, receiver=推算
       └── agent_id=null → sender="unknown", receiver="unknown"

4. 写入阶段
   ├── 连接SQLite
   ├── 开启事务
   ├── 逐条写入
   └── 提交/回滚

5. 验证阶段
   ├── 对比数量
   ├── 抽样校验
   └── 生成报告
```

### 4.2.2 字段映射表

| YAML字段 | SQLite字段 | 转换说明 |
|----------|-----------|----------|
| id | id | 直接复制 |
| content | content | 直接复制 |
| status | status | 直接复制 |
| priority | priority | 直接复制 |
| agent_id | sender | null→"unknown" |
| - | receiver | 推断或"unknown" |
| created_at | created_at | 直接复制 |
| updated_at | updated_at | 直接复制 |
| - | source | 默认为"legacy" |
| - | is_read | 默认为0 |

### 4.2.3 旧TODO处理策略

对于YAML中 `agent_id: null` 的历史TODO：

| 情况 | 处理方式 |
|------|----------|
| TODO编号可解析 | 尝试从编号推断（如TODO-1-xxx → sender=1） |
| 无法推断 | sender="unknown", receiver="unknown" |
| 保留原样 | 不删除，允许后续手动修正 |

### 4.2.4 迁移命令

```bash
# 执行迁移（带确认）
oc-collab migrate --to-sqlite

# 预览迁移（不执行）
oc-collab migrate --preview

# 回滚
oc-collab migrate --rollback --backup <backup_file>

# 查看备份列表
oc-collab migrate --list-backups
```

### 4.3 AgentListener (M3)

```python
class AgentListenerService:
    """监听进程服务"""
    
    def __init__(self, storage: TodoStorage, interval: int = 5):
        self.storage = storage
        self.interval = interval
        self._daemon_process = None
    
    def start_daemon(self, interval: int = None) -> bool:
        """
        启动守护进程
        Returns: success
        """
        pass
    
    def stop(self) -> bool:
        """
        停止监听
        Returns: success
        """
        pass
    
    def check_status(self) -> dict:
        """
        检查监听状态
        Returns: {running: bool, pid: int|None, interval: int}
        """
        pass
    
    def poll_todos(self) -> list[dict]:
        """
        轮询检查新TODO
        Returns: 新TODO列表
        """
        pass
    
    def _save_pid(self, pid: int):
        """保存PID到文件"""
        pass
    
    def _load_pid(self) -> int | None:
        """从文件加载PID"""
        pass
    
    def _is_running(self, pid: int) -> bool:
        """检查进程是否运行"""
        pass
```

### 4.4 StatusMonitor (M4)

```python
class AgentStatusMonitor:
    """Agent状态感知"""
    
    def __init__(self, db_path: str = "state/todos.db"):
        self.db_path = db_path
    
    def detect_online(self, agent_id: str) -> bool:
        """检测Agent上线"""
        pass
    
    def detect_offline(self, agent_id: str) -> bool:
        """检测Agent下线"""
        pass
    
    def get_last_seen(self, agent_id: str) -> datetime | None:
        """获取最后在线时间"""
        pass
    
    def is_online(self, agent_id: str) -> bool:
        """检查Agent是否在线"""
        pass
    
    def list_online_agents(self) -> list[str]:
        """列出所有在线Agent"""
        pass
```

### 4.5 OnlinePuller (M5)

```python
class OnlinePullerService:
    """上线拉取TODO"""
    
    def __init__(self, storage: TodoStorage, status_monitor: AgentStatusMonitor):
        self.storage = storage
        self.status_monitor = status_monitor
    
    def pull_pending(self, agent_id: str) -> list[dict]:
        """
        拉取积压TODO
        Returns: 未处理TODO列表
        """
        pass
    
    def notify_user(self, todos: list[dict]) -> bool:
        """
        通知用户有待办
        Returns: success
        """
        pass
    
    def get_deferred_todos(self, agent_id: str) -> list[dict]:
        """获取已到期的延迟TODO"""
        pass
```

### 4.6 Notification (M6)

```python
class NotificationService:
    """实时通知服务"""
    
    def __init__(self, storage: TodoStorage):
        self.storage = storage
    
    def generate_instruction(
        self, 
        output_path: str = "config/instructions/TODO_NOTIFY.md"
    ) -> bool:
        """
        生成Instruction文件
        Returns: success
        """
        pass
    
    def notify(self, todo: dict) -> str:
        """
        触发通知
        Returns: notification_id
        """
        pass
    
    def enable(self) -> bool:
        """启用通知"""
        pass
    
    def disable(self) -> bool:
        """禁用通知"""
        pass
    
    def get_status(self) -> dict:
        """
        获取通知状态
        Returns: {enabled: bool, last_notification: str}
        """
        pass
```

### 4.7 InteractionHandler (M7)

```python
class InteractionHandler:
    """TODO交互处理"""
    
    def __init__(self, storage: TodoStorage, notification: NotificationService):
        self.storage = storage
        self.notification = notification
    
    def handle_action(self, todo_id: str, action: str) -> tuple[bool, str]:
        """
        处理用户操作
        Actions: execute, defer, dismiss, view, reassign
        Returns: (success, message)
        """
        pass
    
    def execute(self, todo_id: str) -> bool:
        """立即执行 - 标记为进行中"""
        pass
    
    def defer(self, todo_id: str, delay_minutes: int = 0) -> bool:
        """
        留待空闲 - 移入延迟队列
        delay_minutes: 延迟分钟数，0表示用户确认后处理
        """
        pass
    
    def dismiss(self, todo_id: str, reason: str = None) -> bool:
        """不用执行 - 标记为cancelled"""
        pass
    
    def reassign(self, todo_id: str, new_receiver: str) -> bool:
        """转给其他Agent"""
        pass
    
    def view(self, todo_id: str) -> dict:
        """查看详情"""
        pass
```

### 4.8 ConfigManager (M8)

```python
class ConfigManager:
    """配置管理"""
    
    def __init__(self, config_path: str = "config/notification.yaml"):
        self.config_path = config_path
        self._ensure_config()
    
    def _ensure_config(self):
        """确保配置文件存在"""
        pass
    
    def set(self, key: str, value: str) -> bool:
        """设置配置"""
        pass
    
    def get(self, key: str, default: str = None) -> str | None:
        """获取配置"""
        pass
    
    def list(self) -> dict:
        """列出所有配置"""
        pass
    
    def delete(self, key: str) -> bool:
        """删除配置"""
        pass
```

---

## 5. CLI命令设计

### 5.1 agent listen 命令组

| 命令 | 函数 | 描述 |
|------|------|------|
| `oc-collab agent listen --daemon` | `start_daemon()` | 守护进程模式启动 |
| `oc-collab agent listen --stop` | `stop()` | 停止监听 |
| `oc-collab agent listen --status` | `check_status()` | 查看状态 |

### 5.2 config 命令组

| 命令 | 函数 | 描述 |
|------|------|------|
| `oc-collab config set <key> <value>` | `set(key, value)` | 设置配置 |
| `oc-collab config get <key>` | `get(key)` | 获取配置 |
| `oc-collab config list` | `list()` | 列出配置 |

### 5.3 notify 命令组

| 命令 | 函数 | 描述 |
|------|------|------|
| `oc-collab notify enable` | `enable()` | 启用通知 |
| `oc-collab notify disable` | `disable()` | 禁用通知 |
| `oc-collab notify status` | `get_status()` | 查看状态 |

### 5.4 todo 命令变更

| 命令 | 变更说明 |
|------|----------|
| `oc-collab todowrite` | 底层存储从YAML改为SQLite |
| `oc-collab todo list` | 从SQLite读取 |
| `oc-collab todo show` | 从SQLite读取 |

---

## 6. 数据流设计

### 6.1 TODO存储流程

```
用户执行 todowrite
     │
     ▼
CLI命令解析
     │
     ▼
TodoStorage.add()
     │
     ├── 验证数据
     │
     ├── 写入 SQLite
     │
     └── 返回 TODO-ID
```

### 6.2 监听流程

```
agent listen --daemon
     │
     ▼
后台轮询 (interval秒)
     │
     ├── 读取最新TODO
     │
     ├── 检测新增TODO
     │
     ├── 是 → Notification.notify()
     │         │
     │         └── 触发LLM交互
     │
     └── 否 → 继续轮询
```

### 6.3 迁移流程

```
oc-collab migrate
     │
     ├── 备份YAML文件
     │
     ├── 解析YAML结构
     │
     ├── 转换为SQLite记录
     │
     ├── 写入todos表
     │
     ├── 验证迁移结果
     │
     ├── 成功 → 删除原YAML
     │
     └── 失败 → 回滚
```

---

## 7. 错误处理

### 7.1 异常类型

| 异常类型 | 触发条件 | 处理方式 |
|----------|----------|----------|
| DatabaseError | 数据库连接/操作失败 | 重试3次，报错退出 |
| MigrationError | 迁移失败 | 自动回滚，提示用户 |
| ValidationError | 数据验证失败 | 拒绝操作，提示原因 |
| ConfigError | 配置错误 | 提示用户检查配置 |
| DaemonError | 守护进程异常 | 记录日志，尝试重启 |

### 7.2 重试机制

```python
def retry_operation(func, max_retries: int = 3, delay: float = 1.0):
    """重试装饰器"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            time.sleep(delay * (i + 1))
```

---

## 8. 测试策略

### 8.1 单元测试

| 模块 | 测试类 | 测试内容 |
|------|--------|----------|
| TodoStorage | TestTodoStorage | CRUD操作、索引 |
| DataMigration | TestDataMigration | 迁移、回滚 |
| AgentListener | TestAgentListener | 守护进程启停 |
| StatusMonitor | TestStatusMonitor | 在线状态检测 |
| Notification | TestNotification | Instruction生成 |
| InteractionHandler | TestInteractionHandler | 各种操作 |
| ConfigManager | TestConfigManager | 配置CRUD |

### 8.2 E2E测试

| 测试场景 | 测试步骤 | 验收标准 |
|----------|----------|----------|
| SQLite存储 | 创建/查询/更新/删除TODO | 数据正确 |
| 数据迁移 | 执行迁移，检查数据完整性 | 数据不丢失 |
| 守护进程 | 启动/停止/状态检查 | 正常运行 |
| 通知启用 | enable → 生成Instruction | 文件存在 |
| 配置管理 | set/get/list | 正确持久化 |

---

## 9. 兼容性设计

### 9.1 迁移兼容性

- 首次启动自动创建SQLite数据库
- 旧YAML文件保留，迁移后可手动删除
- 迁移前自动备份

### 9.2 CLI兼容性

- 所有现有命令保持不变
- 仅底层存储从YAML改为SQLite

---

## 11. 边界条件与验证

### 11.1 TODO ID格式验证

| 格式 | 示例 | 合法性 |
|------|------|--------|
| 旧格式 | TODO-1-001 | ✅ 合法 |
| 新格式Agent内部 | TODO-1-001 | ✅ 合法 |
| 新格式跨Agent | TODO-1to2-001 | ✅ 合法 |
| 未知Agent | TODO-1to9-001 | ⚠️ 警告 |
| 非法格式 | TODO-abc-001 | ❌ 拒绝 |

### 11.2 状态流转

```
┌──────────┐     execute     ┌─────────────┐
│ pending  │ ───────────────▶ │ in_progress │
└──────────┘                  └─────────────┘
     │                              │
     │                    complete  │
     │◀─────────────────────────────┘
     │
     │ defer              ┌──────────┐
     ├───────────────────▶│ deferred │
     │                    └──────────┘
     │                         │
     │                    execute │
     │◀─────────────────────────┘
     │
     │ dismiss              ┌──────────┐
     └────────────────────▶│ cancelled│
                           └──────────┘
```

### 11.3 边界条件

| 场景 | 处理方式 |
|------|----------|
| 空content | 拒绝，提示"内容不能为空" |
| 超长content | 截断或拒绝（>5000字符） |
| 重复TODO ID | 拒绝，提示ID已存在 |
| 未知receiver | 警告但允许创建 |
| 并发写入 | SQLite锁重试 |
| 数据库损坏 | 提示修复或重建 |

---

## 12. 配置文件

### 12.1 notification.yaml

```yaml
# config/notification.yaml
version: "1.0"

# 通知开关
enabled: true

# OpenCode配置
opencode:
  url: "http://localhost:11411"
  api_key: ""

# 监听配置
listener:
  interval: 5  # 秒
  auto_start: false
  daemon_pid_file: "state/listener.pid"

# 通知规则
rules:
  notify_on_new: true
  notify_on_update: false
  notify_deferred_reminder: true
```

### 12.2 config/instructions/TODO_NOTIFY.md

```markdown
# TODO通知处理规则

## 触发条件
当用户告知"我有新TODO"或"查看TODO"时，执行以下操作：

## 操作流程
1. 读取 state/todos.db 中的未读TODO
2. 查找当前用户的未处理TODO
3. 使用 question tool 询问用户操作

## Question Tool 调用示例
```

### 12.3 数据库配置

```yaml
# config/database.yaml
db:
  path: "state/todos.db"
  timeout: 30
  journal_mode: "WAL"
```

---

## 13. 错误码定义

### 13.1 数据库错误 (1000-1099)

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 1001 | 数据库连接失败 | 重试3次，提示检查文件权限 |
| 1002 | 数据库锁定 | 等待后重试 |
| 1003 | 数据验证失败 | 拒绝写入，提示原因 |
| 1004 | 记录不存在 | 提示检查ID |

### 13.2 迁移错误 (2000-2099)

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 2001 | YAML文件不存在 | 提示文件路径 |
| 2002 | YAML格式错误 | 显示解析错误位置 |
| 2003 | 迁移中断 | 自动回滚 |
| 2004 | 数据不完整 | 提示缺失字段 |

### 13.3 守护进程错误 (3000-3099)

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 3001 | PID文件损坏 | 清理后重试 |
| 3002 | 进程已运行 | 提示查看状态 |
| 3003 | 权限不足 | 提示检查权限 |

### 13.4 配置错误 (4000-4099)

| 错误码 | 含义 | 处理方式 |
|--------|------|----------|
| 4001 | 配置文件不存在 | 自动创建默认配置 |
| 4002 | 配置格式错误 | 提示YAML语法错误 |
| 4003 | 无效值 | 提示有效值范围 |

---

## 14. 文件清单

### 14.1 新增文件

| 文件路径 | 说明 | 行数预估 |
|----------|------|----------|
| src/core/todo_storage.py | SQLite存储层 | ~200 |
| src/core/data_migration.py | 迁移服务 | ~150 |
| src/core/agent_listener.py | 监听服务 | ~180 |
| src/core/status_monitor.py | 状态监控 | ~120 |
| src/core/online_puller.py | 上线拉取 | ~100 |
| src/core/notification.py | 通知服务 | ~150 |
| src/core/interaction_handler.py | 交互处理 | ~200 |
| src/core/config_manager.py | 配置管理 | ~100 |
| src/cli/listen_commands.py | listen命令 | ~80 |
| src/cli/config_commands.py | config命令 | ~80 |
| src/cli/notify_commands.py | notify命令 | ~80 |
| src/templates/TODO_NOTIFY.md.j2 | Instruction模板 | ~50 |

### 14.2 变更文件

| 文件路径 | 变更内容 |
|----------|----------|
| src/core/todo_sync_manager.py | 适配SQLite存储 |
| src/cli/enhanced_commands.py | 适配新存储层 |

### 14.3 新增配置

| 文件路径 | 说明 |
|----------|------|
| config/notification.yaml | 通知配置 |
| config/database.yaml | 数据库配置 |
| config/instructions/TODO_NOTIFY.md | Instruction文件 |

---

## 15. 部署与迁移

### 15.1 首次部署

1. 创建 state/ 目录
2. 初始化 todos.db
3. 创建 config/notification.yaml
4. 注册Agent

### 15.2 升级迁移

1. 备份 state/agent_adhoc_todos.yaml
2. 执行 DataMigration.migrate()
3. 验证数据完整性
4. 删除原YAML（可选）

### 15.3 回滚

1. 使用备份的YAML恢复
2. 删除 todos.db
3. 恢复旧版本代码

---

## 16. 性能考虑

| 场景 | 预期性能 | 优化措施 |
|------|----------|----------|
| TODO创建 | <100ms | 索引、预编译 |
| TODO查询 | <50ms | 索引、缓存 |
| 列表查询 | <200ms | 分页、延迟加载 |
| 数据库大小 | <10MB | 定期清理历史 |

---

## 10. 签署确认

### Agent 2 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-17 | ✅ |

### Agent 1 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-17
**状态**: DRAFT
