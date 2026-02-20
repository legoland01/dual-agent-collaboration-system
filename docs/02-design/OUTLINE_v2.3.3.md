# 概要设计文档：oc-collab v2.3.3

**版本**: v1 (DRAFT)  
**创建日期**: 2026-02-19  
**作者**: Agent 1 (产品经理)  
**关联需求**: requirements_v2.3.3.md  
**版本号**: 2.3.3

---

## 1. 设计目标

v2.3.3的核心目标：
1. **自动流程触发** - 状态变更后自动触发下一流程
2. **测试沙箱** - 独立测试数据库隔离测试数据
3. **跨项目查询** - 支持内部子系统信息互通

---

## 2. 功能模块

### 2.1 模块划分

| 模块ID | 模块名称 | 功能ID | 优先级 |
|--------|----------|--------|--------|
| M1 | 状态监听器 | F-AT-01 | P0 |
| M2 | 流程触发器 | F-AT-02 | P0 |
| M3 | 循环路径引擎 | F-AT-03 | P1 |
| M4 | 超时预警器 | F-AT-04 | P1 |
| M5 | 反复预警器 | F-AT-05 | P1 |
| M6 | 自动TODO创建 | F-AT-06 | P0 |
| M7 | Bug自动验收 | F-AT-07 | P1 |
| M8 | 测试通过流程 | F-AT-08 | P1 |
| M9 | 测试沙箱 | F-AT-09 | P0 |
| M10 | 测试数据保护 | F-AT-10 | P0 |
| M11 | 跨项目查询 | F-AT-11 | P1 |
| M12 | 权限控制器 | F-AT-12 | P1 |
| M13 | 公共文档CLI | F-AT-13 | P1 |

---

## 3. 技术架构

### 3.1 技术选型

| 技术 | 选型 | 说明 |
|------|------|------|
| 事件驱动 | Observer模式 | 状态变更监听 |
| 定时任务 | schedule/apscheduler | 超时预警 |
| 数据库 | SQLite | 主库+测试库 |
| CLI框架 | Click | 命令行 |

### 3.2 文件结构

```
src/
├── core/
│   ├── state_listener.py       # M1: 状态监听器
│   ├── flow_trigger.py         # M2: 流程触发器
│   ├── cycle_engine.py         # M3: 循环路径引擎
│   ├── timeout_watcher.py      # M4: 超时预警器
│   ├── repeat_watcher.py       # M5: 反复预警器
│   ├── auto_todo_creator.py   # M6: 自动TODO创建
│   ├── test_sandbox.py        # M9: 测试沙箱
│   ├── test_data_guard.py     # M10: 测试数据保护
│   ├── cross_project.py        # M11: 跨项目查询
│   ├── permission_controller.py # M12: 权限控制器
│   └── docs_cli.py             # M13: 公共文档CLI
├── cli/
│   ├── flow_commands.py        # 流程命令
│   ├── docs_commands.py       # 文档命令
│   └── test_commands.py       # 测试命令(沙箱)
└── templates/
    └── flow_config.yaml.j2    # 流程配置模板

state/
├── todos.db                    # 主数据库
└── todos_test.db              # 测试沙箱数据库
```

---

## 4. 模块设计

### 4.1 M1: 状态监听器

**功能**: 监听文档/TODO状态变更

**核心方法**:
```python
class StateListener:
    def __init__(self, storage: TodoStorage):
        self.storage = storage
        self.listeners = []
    
    def register(self, event_type: str, callback: Callable):
        """注册事件监听器"""
    
    def start(self):
        """启动监听"""
    
    def on_todo_status_change(self, old_status, new_status, todo_id):
        """TODO状态变更事件"""
    
    def get_changes(self, project_id: str, since: str) -> List[Change]:
        """查询变更记录（供PM-Agent等外部系统调用）"""
```

**CLI接口**（供外部系统获取变更）：
```bash
oc-collab project <name> changes --since=2026-02-19T10:00:00Z --json
```

### 4.2 M2: 流程触发器

**功能**: 状态变更后自动触发下一流程

**核心方法**:
```python
class FlowTrigger:
    def __init__(self, config: FlowConfig):
        self.rules = config.get_rules()
    
    def trigger(self, event: Event) -> List[Action]:
        """根据事件触发相应动作"""
    
    def should_auto_trigger(self, from_state, to_state) -> bool:
        """判断是否自动触发"""
```

### 4.3 M9: 测试沙箱

**功能**: 独立测试数据库隔离测试数据

**核心方法**:
```python
class TestSandbox:
    def __init__(self):
        self.test_db = "state/todos_test.db"
        self.prod_db = "state/todos.db"
    
    def use_sandbox(self):
        """切换到测试沙箱"""
    
    def use_production(self):
        """切换到生产环境"""
    
    def cleanup_own_data(self, agent_id: str):
        """只清理自己创建的数据"""
```

### 4.4 M11: 跨项目查询

**功能**: 支持内部子系统查询其他项目状态

**CLI接口设计**：

```bash
# 查询项目状态 - 返回结构化JSON
oc-collab project <name> status --json

# 查询项目TODO - 支持过滤
oc-collab project <name> todos --json --status=completed

# 查询项目变更（用于PM-Agent轮询）
oc-collab project <name> changes --since=2026-02-19T10:00:00Z --json

# 查询项目进度（用于Dashboard）
oc-collab project <name> progress --json
```

**认证机制**：
```bash
# 方式1: 环境变量（推荐）
export OC_COLLAB_INTERNAL=PM-Agent

# 方式2: CLI参数
oc-collab project <name> status --internal
```

**内部子系统清单** (config/internal_subsystems.yaml):
```yaml
internal_subsystems:
  - PM-Agent
  - Report-Generator
  - Dashboard-Service
```

**核心方法**:
```python
class CrossProjectQuery:
    def __init__(self, storage: TodoStorage):
        self.storage = storage
    
    def query_todos(self, project_id: str, filters: dict) -> List[Todo]:
        """查询项目TODO"""
    
    def query_project_status(self, project_id: str) -> ProjectStatus:
        """查询项目状态"""
    
    def query_changes(self, project_id: str, since: str) -> List[Change]:
        """查询变更记录"""
    
    def query_progress(self, project_id: str) -> Progress:
        """查询项目进度"""
    
    def check_permission(self, requester: str) -> bool:
        """权限校验"""
```

### 4.5 M13: 公共文档CLI

**功能**: oc-collab docs query/list/architecture

**CLI接口设计**：
```bash
# 搜索包含关键字的文档
oc-collab docs query "PM-Agent" --json

# 列出文档
oc-collab docs list [--category <category>] [--json]

# 查看架构
oc-collab docs architecture [--json]
```

**公共文档管理**：

| 文档 | 存放位置 | 维护者 |
|------|----------|--------|
| oc-collab能力清单 | `templates/docs/` | Consultant |
| PM-Agent协同建议 | `templates/docs/` | Consultant |
| 核心架构文档 | `templates/docs/` | Agent1 |
| 其他公共文档 | `templates/docs/` | 按需 |

**文档维护机制**：
1. 文档统一存放在 `templates/docs/` 目录
2. 新增/更新文档需提交PR并经过评审
3. 文档格式要求：Markdown
4. 文档命名规范：`{类别}_{名称}.md`

**CLI命令**:
```bash
# 查询文档
oc-collab docs query <keyword>

# 列出文档
oc-collab docs list [--category <category>]

# 查看架构
oc-collab docs architecture
```

---

## 5. 自动化决策类型

| 类型 | 处理方式 | 实现 |
|------|----------|------|
| 循环类 | 自动触发下一次 | M3 循环路径引擎 |
| 预警类 | 自动+人工确认 | M4/M5 预警器 |
| 签署类 | 必须人工确认 | M2 流程触发器(配置) |

---

## 6. 配置文件

### 6.1 流程配置 (flow_config.yaml)

```yaml
flows:
 评审通过后签署:
   trigger: 评审通过
   auto: true
   timeout: 24h

 签署通过后开发:
   trigger: 签署通过
   auto: false  # 需要人工确认
   requires: [评审通过]

超时配置:
  default_timeout: 72h
  warning_threshold: 0.8

反复配置:
  max_repeats: 3
  warn_after: 2
```

---

## 7. 工时预估

| 模块 | 工时 |
|------|------|
| M1-M5 (自动化流程) | 8h |
| M6-M8 (自动创建) | 4h |
| M9-M10 (测试沙箱) | 4h |
| M11-M12 (跨项目) | 4h |
| M13 (公共文档CLI) | 3h |
| 测试与调试 | 8h |
| 文档 | 2h |
| **总计** | **33h** |

---

## 8. 依赖关系

| 模块 | 依赖 |
|------|------|
| M2 流程触发器 | M1 状态监听器 |
| M3 循环路径引擎 | M2 流程触发器 |
| M4/M5 预警器 | M1 状态监听器 |
| M6 自动TODO创建 | M2 流程触发器 |
| M9 测试沙箱 | v2.3.2 SQLite存储 |
| M11 跨项目查询 | 权限控制器 M12 |

---

## 9. 验收标准

| 模块 | 验收标准数 |
|------|-----------|
| M1-M5 | 9 |
| M6-M8 | 6 |
| M9-M10 | 6 |
| M11-M13 | 9 |
| **总计** | **30** |

---

## 10. 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-02-19 | 初始版本 |
| v2 | 2026-02-19 | 补充M13公共文档存放位置和维护机制 |
| v3 | 2026-02-19 | PM-Agent评审补充：CLI返回JSON格式、认证机制、变更通知、进度查询 |
