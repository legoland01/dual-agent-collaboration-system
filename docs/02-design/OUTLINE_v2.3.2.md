# 概要设计文档：oc-collab v2.3.2

**版本**: v1 (DRAFT)  
**创建日期**: 2026-02-17  
**作者**: Agent 1 (产品经理)  
**关联需求**: requirements_v2.3.2.md  
**版本号**: 2.3.2

---

## 1. 设计目标

v2.3.2的核心目标：
1. **SQLite存储** - TODO数据从YAML迁移到SQLite
2. **监听进程** - agent listen守护进程模式
3. **实时通知** - Question窗口交互

---

## 2. 功能模块

### 2.1 模块划分

| 模块ID | 模块名称 | 功能ID | 优先级 |
|--------|----------|--------|--------|
| M1 | TodoStorage | F-STORE-001 | P0 |
| M2 | DataMigration | F-STORE-002 | P1 |
| M3 | AgentListener | F-LISTEN-001 | P0 |
| M4 | Status感知 | F-LISTEN-002 | P1 |
| M5 | Online拉取 | F-LISTEN-003 | P1 |
| M6 | Notification | F-NOTIF-001 | P0 |
| M7 | Interaction | F-NOTIF-002 | P0 |
| M8 | ConfigManager | F-CONFIG-001 | P1 |

---

## 3. 技术架构

### 3.1 技术选型

| 技术 | 选型 | 说明 |
|------|------|------|
| 数据库 | SQLite | 内置、轻量级 |
| ORM | SQLite3原生 | 简单高效 |
| 进程管理 | daemonize | 守护进程 |
| 配置 | YAML | 与现有体系一致 |

### 3.2 文件结构

```
src/
├── core/
│   ├── todo_storage.py      # M1: SQLite存储
│   ├── data_migration.py     # M2: 数据迁移
│   ├── agent_listener.py    # M3: 监听进程
│   ├── status_monitor.py    # M4: 状态感知
│   └── config_manager.py    # M8: 配置管理
├── cli/
│   ├── listen_commands.py   # 监听命令
│   ├── config_commands.py   # 配置命令
│   └── notify_commands.py   # 通知命令
└── templates/
    └── TODO_NOTIFY.md.j2    # Instruction模板

state/
└── todos.db                 # SQLite数据库
```

---

## 4. 模块设计

### 4.1 M1: TodoStorage

**功能**: SQLite存储层

**核心方法**:
```python
class TodoStorage:
    def __init__(self, db_path: str = "state/todos.db"):
        """初始化数据库"""
        
    def create_table(self):
        """创建TODO表"""
        
    def add(self, todo: dict) -> bool:
        """添加TODO"""
        
    def get(self, todo_id: str) -> dict:
        """获取单个TODO"""
        
    def list(self, receiver: str = None, status: str = None) -> list:
        """列出TODO"""
        
    def update(self, todo_id: str, updates: dict) -> bool:
        """更新TODO"""
        
    def delete(self, todo_id: str) -> bool:
        """删除TODO"""
```

### 4.2 M2: DataMigration

**功能**: YAML到SQLite迁移

**核心方法**:
```python
class DataMigration:
    def migrate(self, yaml_path: str, db_path: str) -> bool:
        """执行迁移"""
        
    def backup(self, yaml_path: str) -> str:
        """备份原文件"""
        
    def rollback(self, backup_path: str, db_path: str) -> bool:
        """回滚"""
```

### 4.3 M3: AgentListener

**功能**: 监听进程

**核心方法**:
```python
class AgentListener:
    def start_daemon(self, interval: int = 5):
        """启动守护进程"""
        
    def stop(self):
        """停止监听"""
        
    def check_status(self) -> dict:
        """检查状态"""
        
    def poll_todos(self):
        """轮询检查新TODO"""
```

### 4.4 M4: StatusMonitor

**功能**: Agent状态感知

**核心方法**:
```python
class StatusMonitor:
    def detect_online(self, agent_id: str):
        """检测上线"""
        
    def detect_offline(self, agent_id: str):
        """检测下线"""
        
    def get_last_seen(self, agent_id: str) -> datetime:
        """获取最后在线时间"""
```

### 4.5 M5: OnlinePuller

**功能**: 上线拉取积压TODO

**核心方法**:
```python
class OnlinePuller:
    def pull_pending(self, agent_id: str) -> list:
        """拉取积压TODO"""
        
    def notify_user(self, todos: list):
        """通知用户"""
```

### 4.6 M6: Notification

**功能**: 实时通知

**核心方法**:
```python
class Notification:
    def generate_instruction(self, output_path: str) -> bool:
        """生成instruction文件"""
        
    def notify(self, todo: dict):
        """触发通知"""
```

### 4.7 M7: Interaction

**功能**: TODO交互操作

**核心方法**:
```python
class Interaction:
    def handle_action(self, todo_id: str, action: str) -> bool:
        """处理用户操作"""
        
    def execute(self, todo_id: str):
        """立即执行"""
        
    def defer(self, todo_id: str):
        """留待空闲"""
        
    def dismiss(self, todo_id: str):
        """不用执行"""
```

### 4.8 M8: ConfigManager

**功能**: 配置管理

**核心方法**```python
class ConfigManager:
    def set(self, key: str, value: str):
        """设置配置"""
        
    def get(self, key: str) -> str:
        """获取配置"""
        
    def list(self) -> dict:
        """列出所有配置"""
```

---

## 5. 数据流设计

### 5.1 TODO存储流程

```
用户执行 todowrite
     │
     ▼
TodoStorage.add()
     │
     ▼
写入 SQLite todos.db
     │
     ▼
返回成功
```

### 5.2 监听流程

```
agent listen --daemon
     │
     ▼
后台轮询 (interval秒)
     │
     ▼
检测新TODO
     │
     ├── 是 → 触发Notification
     │
     └── 否 → 继续轮询
```

### 5.3 通知流程

```
检测到新TODO
     │
     ▼
生成/更新Instruction
     │
     ▼
用户告知LLM"我有新TODO"
     │
     ▼
LLM调用question tool
     │
     ▼
用户选择操作
     │
     ▼
Interaction.handle_action()
     │
     ▼
更新TODO状态
```

---

## 6. 接口设计

### 6.1 CLI接口

```bash
# 监听命令
oc-collab agent listen --daemon          # 启动守护进程
oc-collab agent listen --stop            # 停止
oc-collab agent listen --status          # 状态

# 配置命令
oc-collab config set <key> <value>       # 设置
oc-collab config list                    # 列表

# 通知命令
oc-collab notify enable                   # 启用
oc-collab notify disable                 # 禁用
oc-collab notify status                  # 状态
```

### 6.2 内部接口

| 接口 | 模块 | 方法 |
|------|------|------|
| 存储 | M1 | add/get/update/delete |
| 迁移 | M2 | migrate/rollback |
| 监听 | M3 | start/stop/poll |
| 状态 | M4 | detect_online/offline |
| 拉取 | M5 | pull_pending |
| 通知 | M6 | notify |
| 交互 | M7 | handle_action |
| 配置 | M8 | set/get |

---

## 7. 错误处理

| 场景 | 处理 |
|------|------|
| 数据库锁定 | 重试机制 |
| 迁移失败 | 回滚到YAML |
| 监听进程崩溃 | 自动重启 |
| 配置错误 | 提示用户 |

---

## 8. 测试策略

| 模块 | 测试类 |
|------|--------|
| M1 | TestTodoStorage |
| M2 | TestDataMigration |
| M3 | TestAgentListener |
| M4 | TestStatusMonitor |
| M5 | TestOnlinePuller |
| M6 | TestNotification |
| M7 | TestInteraction |
| M8 | TestConfigManager |

---

## 9. 兼容性

- 现有CLI命令保持兼容
- YAML文件可迁移到SQLite
- 迁移后原YAML自动备份

---

**状态**: DRAFT  
**待评审**: Agent2

