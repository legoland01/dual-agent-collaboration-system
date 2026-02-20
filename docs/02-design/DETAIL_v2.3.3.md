# 详细设计文档：oc-collab v2.3.3

**版本**: v1  
**创建日期**: 2026-02-19  
**作者**: Agent2 (开发负责人)  
**关联需求**: requirements_v2.3.3.md  
**关联概要设计**: OUTLINE_v2.3.3.md

---

## 1. 系统架构

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      v2.3.3 架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  状态监听器   │───▶│  流程触发器   │───▶│  循环引擎    │ │
│  │ (M1)         │    │ (M2)         │    │ (M3)         │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│         │                   │                   │          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │  超时预警器   │    │  反复预警器   │    │  自动创建TODO │ │
│  │ (M4)         │    │ (M5)         │    │ (M6)         │ │
│  └──────────────┘    └──────────────┘    └──────────────┘ │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    事件总线                            │  │
│  │  (state_changed / todo_created / phase_advanced)     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 数据流

```
用户操作 → 事件触发 → 状态监听器 → 规则匹配 → 流程触发器 → 执行动作
                                                    │
                                                    ▼
                                            [通知/创建TODO/推进阶段]
```

---

## 2. 模块详细设计

### 2.1 M1: 状态监听器

**职责**: 监听并记录状态变更事件

**实现位置**: `src/core/state_listener.py` (新建)

**核心类**:

```python
class StateListener:
    """状态变更监听器"""
    
    def __init__(self, storage: SQLiteStorage):
        self.storage = storage
    
    def on_todo_status_changed(self, todo_id: str, old_status: str, new_status: str):
        """TODO状态变更回调"""
        event = {
            "type": "todo_status_changed",
            "todo_id": todo_id,
            "old_status": old_status,
            "new_status": new_status,
            "timestamp": datetime.now().isoformat()
        }
        self.storage.add_event(event)
    
    def on_phase_advanced(self, old_phase: str, new_phase: str):
        """阶段推进回调"""
        event = {
            "type": "phase_advanced",
            "old_phase": old_phase,
            "new_phase": new_phase,
            "timestamp": datetime.now().isoformat()
        }
        self.storage.add_event(event)
```

**数据库表**:

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    data TEXT NOT NULL,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**M1.1 变更查询接口**:

```python
class StateListener:
    """状态变更监听器"""
    
    def get_changes(self, since: str = None, event_type: str = None) -> List[dict]:
        """查询变更记录
        
        Args:
            since: ISO格式时间戳，如 "2026-02-19T10:00:00Z"
            event_type: 事件类型过滤
            
        Returns:
            变更列表 [{"type": "todo", "id": "TODO-1", "old_status": "...", "new_status": "...", "timestamp": "..."}]
        """
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if since:
            query += " AND created_at > ?"
            params.append(since)
        
        if event_type:
            query += " AND type = ?"
            params.append(event_type)
        
        query += " ORDER BY created_at DESC"
        
        # 返回结构化变更
        return self._format_changes(rows)
    
    def _format_changes(self, rows) -> List[dict]:
        """格式化变更数据"""
        changes = []
        for row in rows:
            data = json.loads(row["data"])
            changes.append({
                "type": row["type"],
                "id": data.get("id"),
                "old_status": data.get("old_status"),
                "new_status": data.get("new_status"),
                "timestamp": row["created_at"]
            })
        return changes

---

### 2.2 M2: 流程触发器

**职责**: 根据配置的规则自动触发下一步操作

**实现位置**: `src/core/flow_trigger.py` (新建)

**核心类**:

```python
class FlowTrigger:
    """流程触发器"""
    
    TRIGGER_RULES = {
        "requirements_review_passed": ["signoff"],
        "design_review_passed": ["development"],
        "development_completed": ["testing"],
        "testing_passed": ["deployment"],
    }
    
    def __init__(self, event_bus, notifier, todo_manager):
        self.event_bus = event_bus
        self.notifier = notifier
        self.todo_manager = todo_manager
    
    def handle_event(self, event: dict):
        """处理事件，触发对应动作"""
        event_type = event["type"]
        
        if event_type in self.TRIGGER_RULES:
            actions = self.TRIGGER_RULES[event_type]
            for action in actions:
                self._execute_action(action, event)
    
    def _execute_action(self, action: str, event: dict):
        """执行触发动作"""
        if action == "signoff":
            self._trigger_signoff(event)
        elif action == "development":
            self._trigger_development(event)
        # ...
    
    def _trigger_signoff(self, event: dict):
        """触发签署流程"""
        # 创建签署TODO
        todo_id = self.todo_manager.create_todo(
            content=f"签署{event.get('doc_name', '文档')}",
            receiver="agent1",
            source="auto_trigger"
        )
        self.notifier.notify(f"自动创建签署TODO: {todo_id}")
```

**配置化触发规则** (config/triggers.yaml):

```yaml
triggers:
  - name: "需求评审通过后自动签署"
    condition:
      type: "todo_status_changed"
      new_status: "completed"
      source: "requirements_review"
    actions:
      - type: "create_todo"
        template: "signoff"
      - type: "notify"
        message: "需求评审已完成，请进行签署"

  - name: "开发完成后自动测试"
    condition:
      type: "phase_advanced"
      new_phase: "development_completed"
    actions:
      - type: "create_todo"
        template: "testing"
```

---

### 2.3 M3: 循环路径引擎

**职责**: 处理评审/签署不通过后的循环流程

**实现位置**: `src/core/loop_engine.py` (新建)

**核心逻辑**:

```python
class LoopEngine:
    """循环路径引擎"""
    
    MAX_LOOP_COUNT = 10
    
    LOOPS = {
        "review_rejected": {
            "next_action": "requirements_review",
            "counter_field": "review_count"
        },
        "signoff_rejected": {
            "next_action": "signoff",
            "counter_field": "signoff_count"
        },
        "bug_rejected": {
            "next_action": "bug_fix",
            "counter_field": "fix_count"
        }
    }
    
    def handle_rejection(self, source_type: str, todo_id: str):
        """处理被拒绝的情况"""
        loop_config = self.LOOPS.get(source_type)
        if not loop_config:
            return
        
        # 获取当前循环次数
        count = self._get_loop_count(todo_id, loop_config["counter_field"])
        
        if count >= self.MAX_LOOP_COUNT:
            self._send_warning(todo_id, count)
        else:
            # 自动重新触发
            self._trigger_next_action(todo_id, loop_config["next_action"])
    
    def _get_loop_count(self, todo_id: str, field: str) -> int:
        """获取循环次数"""
        # 从TODO metadata中获取
        pass
    
    def _send_warning(self, todo_id: str, count: int):
        """发送循环预警"""
        notifier.notify_warning(
            f"TODO {todo_id} 已循环 {count} 次，请人工介入"
        )
```

---

### 2.4 M4: 超时预警器

**职责**: 监控TODO超时并发送预警

**实现位置**: `src/core/timeout_watcher.py` (新建)

**数据库表修改**:

```sql
ALTER TABLE todos ADD COLUMN timeout_at TIMESTAMP;
ALTER TABLE todos ADD COLUMN timeout_notified INTEGER DEFAULT 0;
```

**核心逻辑**:

```python
class TimeoutWatcher:
    """TODO超时预警器"""
    
    DEFAULT_TIMEOUT_HOURS = 24
    
    def __init__(self, storage, notifier):
        self.storage = storage
        self.notifier = notifier
    
    def check_timeouts(self):
        """检查超时TODO"""
        timeout_todos = self.storage.get_timeout_todos()
        
        for todo in timeout_todos:
            if not todo.get("timeout_notified"):
                self._notify_timeout(todo)
                self.storage.mark_timeout_notified(todo["id"])
    
    def _notify_timeout(self, todo: dict):
        """发送超时预警"""
        self.notifier.notify(
            f"TODO {todo['id']} 已超时: {todo['content']}",
            receiver=todo["receiver"],
            priority="high"
        )
```

---

### 2.5 M5: 反复预警器

**职责**: 统计同一事项处理次数，达到阈值预警

**实现位置**: `src/core/retry_watcher.py` (新建)

**数据库表修改**:

```sql
ALTER TABLE todos ADD COLUMN retry_count INTEGER DEFAULT 0;
ALTER TABLE todos ADD COLUMN last_rejected_at TIMESTAMP;
```

**核心逻辑**:

```python
class RetryWatcher:
    """反复次数预警器"""
    
    RETRY_THRESHOLD = 3
    
    def __init__(self, storage, notifier):
        self.storage = storage
        self.notifier = notifier
    
    def on_rejection(self, todo_id: str):
        """记录被拒绝，增加计数"""
        self.storage.increment_retry_count(todo_id)
        
        todo = self.storage.get(todo_id)
        if todo["retry_count"] >= self.RETRY_THRESHOLD:
            self._notify_retry_warning(todo)
    
    def _notify_retry_warning(self, todo: dict):
        """发送反复预警"""
        self.notifier.notify(
            f"警告: TODO {todo['id']} 已反复 {todo['retry_count']} 次未通过",
            receiver=todo["receiver"],
            priority="high"
        )
```

---

### 2.6 M6: 自动创建TODO

**职责**: 根据事件自动创建关联TODO

**实现位置**: `src/core/auto_todo_creator.py` (新建)

**核心逻辑**:

```python
class AutoTodoCreator:
    """自动创建TODO"""
    
    TEMPLATES = {
        "signoff": {
            "content": "签署 {doc_name}",
            "receiver": "agent1",
            "priority": "high"
        },
        "testing": {
            "content": "测试 {feature_name}",
            "receiver": "agent2", 
            "priority": "high"
        },
        "bug_verify": {
            "content": "验证Bug修复: {bug_id}",
            "receiver": "agent1",
            "priority": "high"
        }
    }
    
    def create_from_event(self, event: dict):
        """根据事件自动创建TODO"""
        template_name = event.get("template")
        if template_name not in self.TEMPLATES:
            return None
        
        template = self.TEMPLATES[template_name].copy()
        template["content"] = template["content"].format(**event.get("data", {}))
        template["source"] = "auto_create"
        
        return self.todo_manager.create_todo(**template)
```

---

## 3. CLI命令设计

### 3.1 新增命令

```bash
# 查看事件历史
oc-collab event list
oc-collab event list --type todo_status_changed
oc-collab event list --since "2026-02-19"

# 查看触发规则
oc-collab trigger list
oc-collab trigger validate

# 配置超时设置
oc-collab config set timeout.hours 48
oc-collab config set retry.threshold 3
```

### 3.2 修改命令

```bash
# 创建TODO时设置超时
oc-collab todowrite --content "任务" --timeout 24

# 查看TODO超时状态
oc-collab todo list --timeout
```

---

## 4. 事件定义

### 4.1 事件类型

| 事件类型 | 说明 | 数据 |
|----------|------|------|
| todo_created | TODO创建 | todo_id, content, receiver |
| todo_status_changed | TODO状态变更 | todo_id, old_status, new_status |
| todo_completed | TODO完成 | todo_id |
| phase_advanced | 阶段推进 | old_phase, new_phase |
| signoff_completed | 签署完成 | doc_id, status |
| review_completed | 评审完成 | doc_id, status |

### 4.2 事件总线

```python
class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.listeners = defaultdict(list)
    
    def subscribe(self, event_type: str, callback):
        self.listeners[event_type].append(callback)
    
    def publish(self, event: dict):
        event_type = event["type"]
        for callback in self.listeners[event_type]:
            callback(event)
```

---

## 5. 测试设计

### 5.1 单元测试

| 模块 | 测试用例 |
|------|----------|
| StateListener | on_todo_status_changed, on_phase_advanced |
| FlowTrigger | handle_event, trigger_signoff, trigger_development |
| LoopEngine | handle_rejection, check_max_loop |
| TimeoutWatcher | check_timeouts, notify_timeout |
| RetryWatcher | on_rejection, check_threshold |
| AutoTodoCreator | create_from_event |

### 5.2 E2E测试

| 场景 | 测试步骤 |
|------|----------|
| 评审通过自动创建签署 | requirements review pass → signoff TODO created |
| 超时预警 | create TODO → wait timeout → notification sent |
| 反复预警 | reject 3 times → warning notification |
| 循环路径 | review reject → fix → review again → count increment |

---

## 6. 验收标准

| 功能ID | 验收标准 | 测试方法 |
|--------|----------|----------|
| F-AT-01 | 状态变更事件可捕获 | 手动触发+日志验证 |
| F-AT-02 | 配置化的触发规则 | 修改config验证 |
| F-AT-03 | 循环次数限制10次 | 模拟10次循环 |
| F-AT-04 | 超时自动通知 | 设置超时+等待 |
| F-AT-05 | 反复3次预警 | 模拟3次拒绝 |
| F-AT-06 | 事件触发自动创建TODO | 评审通过验证 |
| F-AT-07 | Bug修复后自动创建验收TODO | Bug修复验证 |

---

## 7. M11: 跨项目信息查询

**职责**: 支持内部子系统查询其他项目状态/TODO

**实现位置**: `src/core/project_query.py` (新建)

### 7.1 CLI接口

```bash
# 查询项目状态
oc-collab project <name> status --json

# 查询项目TODO
oc-collab project <name> todos --json --status=completed

# 查询项目变更（用于PM-Agent轮询）
oc-collab project <name> changes --since=2026-02-19T10:00:00Z --json

# 查询项目进度（用于Dashboard）
oc-collab project <name> progress --json
```

### 7.2 核心类

```python
class ProjectQuery:
    """跨项目查询"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.storage = TodoStorage(f"{project_path}/state/todos.db")
        self.state_manager = StateManager(project_path)
    
    def get_status(self) -> dict:
        """获取项目状态"""
        state = self.state_manager.load_state()
        
        todos = self.storage.list()
        
        return {
            "project": state.get("project", "unknown"),
            "requirements": self._count_requirements(state),
            "bugs": self._count_bugs(todos),
            "todos": self._count_todos(todos),
            "last_updated": datetime.now().isoformat()
        }
    
    def get_changes(self, since: str) -> dict:
        """获取项目变更"""
        # 复用M1的get_changes接口
        listener = StateListener(self.storage)
        return {"changes": listener.get_changes(since)}
    
    def get_progress(self) -> dict:
        """获取项目进度"""
        state = self.state_manager.load_state()
        phase = state.get("phase", "unknown")
        
        progress_map = {
            "project_init": 5,
            "requirements_draft": 15,
            "requirements_review": 25,
            "requirements_approved": 35,
            "design_draft": 45,
            "design_review": 55,
            "design_approved": 65,
            "development": 75,
            "testing": 85,
            "deployment": 95,
            "completed": 100
        }
        
        return {
            "project_name": state.get("project", "unknown"),
            "progress": progress_map.get(phase, 0),
            "current_phase": phase
        }
```

### 7.3 权限控制

```python
class ProjectQueryPermission:
    """项目查询权限控制"""
    
    INTERNAL_SUBSYSTEMS = ["PM-Agent", "Report-Generator", "Dashboard-Service"]
    
    def check_permission(self) -> bool:
        """检查是否有权限查询"""
        # 方式1: 环境变量
        subsystem = os.environ.get("OC_COLLAB_INTERNAL")
        if subsystem in self.INTERNAL_SUBSYSTEMS:
            return True
        
        # 方式2: CLI参数
        if "--internal" in sys.argv:
            return True
        
        return False
```

---

## 8. M13: 公共文档查询CLI

**职责**: 提供文档查询、列表、架构查看功能

**实现位置**: `src/cli/docs_commands.py` (新建)

### 8.1 CLI接口

```bash
# 搜索包含关键字的文档
oc-collab docs query "PM-Agent" --json

# 列出文档
oc-collab docs list [--category <category>] [--json]

# 查看架构
oc-collab docs architecture [--json]
```

### 8.2 核心类

```python
class DocsQuery:
    """文档查询"""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.docs_dir = Path(project_path) / "docs"
    
    def query(self, keyword: str) -> List[dict]:
        """搜索文档内容"""
        results = []
        
        for md_file in self.docs_dir.rglob("*.md"):
            try:
                content = md_file.read_text()
                if keyword.lower() in content.lower():
                    results.append({
                        "file": str(md_file.relative_to(self.project_path)),
                        "snippet": self._get_snippet(content, keyword)
                    })
            except Exception:
                continue
        
        return results
    
    def list_docs(self, category: str = None) -> List[dict]:
        """列出文档"""
        docs = []
        
        categories = [category] if category else ["00-memos", "01-requirements", "02-design", "03-test"]
        
        for cat in categories:
            cat_dir = self.docs_dir / cat
            if cat_dir.exists():
                for md_file in cat_dir.glob("*.md"):
                    docs.append({
                        "category": cat,
                        "file": md_file.name,
                        "path": str(md_file.relative_to(self.project_path))
                    })
        
        return docs
    
    def get_architecture(self) -> dict:
        """获取架构信息"""
        arch_file = self.docs_dir / "00-architecture" / "CORE_ARCHITECTURE.md"
        if arch_file.exists():
            return {"content": arch_file.read_text()}
        return {"error": "架构文档不存在"}
```

---

## 附录A: 39个场景详细实现

### A.1 需求阶段场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S1.1 | 评审通过 | requirements review pass | 发出签署通知 | 确认签署 | ReviewWatcher监听→SignoffCreator创建签署TODO |
| S1.2 | 评审要求补充 | requirements review need-clarification | 发出补充TODO | 确认补充内容 | ReviewWatcher监听→TodoCreator创建补充TODO |
| S1.3 | 评审不通过 | requirements review reject | 发出修正TODO | 确认修正方案 | ReviewWatcher监听→TodoCreator创建修正TODO |
| S1.4 | 补充后再次评审 | supplemental review submitted | 自动触发 | 确认 | LoopEngine重置计数器→触发新评审 |
| S1.5 | 多次反复(3次+) | loop count >= 3 | 预警 | 人工介入 | LoopEngine检测阈值→TimeoutWatcher发送预警 |

### A.2 需求签署场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S2.1 | Agent1签署 | agent1 signoff | 自动 | 确认签署 | SignoffWatcher检测→更新状态 |
| S2.2 | Agent2签署 | agent2 signoff | 自动 | 确认签署 | SignoffWatcher检测→更新状态 |
| S2.3 | 双方签署完成 | both signed | 自动触发下一阶段 | - | SignoffWatcher检测→StageTransitioner切换阶段 |

### A.3 概要设计评审场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S3.1 | 评审通过 | outline review pass | 发出签署通知 | 确认签署 | ReviewWatcher监听→SignoffCreator |
| S3.2 | 要求补充设计 | outline review need-clarification | 发出补充TODO | 确认补充内容 | ReviewWatcher→TodoCreator |
| S3.3 | 评审不通过 | outline review reject | 发出修正TODO | 确认修正方案 | ReviewWatcher→TodoCreator |
| S3.4 | 补充后再次评审 | supplemental outline submitted | 自动触发 | - | LoopEngine→重新评审 |

### A.4 详细设计场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S4.1 | 详细设计完成 | detail design completed | 发出评审TODO | - | EventWatcher→TodoCreator |
| S4.2 | 评审通过 | detail review pass | 发出签署通知 | 确认签署 | ReviewWatcher→SignoffCreator |
| S4.3 | 评审要求修改 | detail review need-change | 发出修改TODO | 确认修改内容 | ReviewWatcher→TodoCreator |
| S4.4 | 多次反复 | loop count >= 3 | 预警 | 人工介入 | LoopEngine→TimeoutWatcher预警 |

### A.5 任务分配场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S5.1 | 创建TODO | todo created | 自动 | - | TodoCreator直接创建 |
| S5.2 | TODO分配给Agent | todo assigned | 自动推送给Agent | - | TodoAssigner→Notification |
| S5.3 | TODO被拒绝 | todo rejected | 通知创建者 | 确认重新分配 | EventWatcher→Notifier→TodoAssigner |
| S5.4 | TODO超时未处理 | todo timeout | 预警 | 确认处理方式 | TimeoutWatcher→Notifier→用户确认 |

### A.6 代码开发场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S6.1 | 开发完成 | code completed | 触发自检 | - | EventWatcher→AutoChecker |
| S6.2 | 自检通过 | self-check pass | 自动提测 | - | AutoChecker→TestRunner |
| S6.3 | 自检不通过 | self-check fail | 发出修复TODO | 确认 | AutoChecker→TodoCreator |
| S6.4 | 代码冲突 | merge conflict | 预警 | 人工解决 | GitWatcher→TimeoutWatcher→Notifier |

### A.7 Bug处理场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S7.1 | 发现Bug | bug detected | 自动创建修复TODO | - | AutoBugDetector→TodoCreator |
| S7.2 | Bug修复完成 | bug fixed | 自动创建验收TODO | - | EventWatcher→TodoCreator |
| S7.3 | 验收通过 | bug verified | 关闭Bug | - | VerifyWatcher→BugCloser |
| S7.4 | 验收不通过 | verify fail | 重新修复 | 确认 | VerifyWatcher→TodoCreator |
| S7.5 | Bug反复出现(3次+) | bug recurs 3+ | 预警 | 人工介入 | LoopEngine→TimeoutWatcher |

### A.8 测试执行场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S8.1 | 测试通过 | test pass | 自动记录 | - | TestWatcher→RecordKeeper |
| S8.2 | 测试失败 | test fail | 自动创建Bug TODO | - | TestWatcher→TodoCreator |
| S8.3 | 回归测试失败 | regression fail | 预警 | 确认 | TestWatcher→TimeoutWatcher |
| S8.4 | 测试完成(全部通过) | all tests pass | 发出验收TODO | - | TestWatcher→TodoCreator |

### A.9 测试验收场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S9.1 | 验收通过 | acceptance pass | 自动进入下一阶段 | - | VerifyWatcher→StageTransitioner |
| S9.2 | 验收不通过 | acceptance fail | 发出修复TODO | 确认 | VerifyWatcher→TodoCreator |
| S9.3 | 部分通过 | partial pass | 列出未通过项 | 确认处理方式 | VerifyWatcher→Notifier |

### A.10 部署阶段场景

| 场景ID | 场景名称 | 触发条件 | 自动处理 | 需用户确认 | 实现逻辑 |
|--------|----------|----------|----------|------------|----------|
| S10.1 | 验收通过 | acceptance pass | 准备发布 | 确认版本号 | VerifyWatcher→ReleasePreparer |
| S10.2 | 发布成功 | release success | 自动记录 | - | DeployWatcher→RecordKeeper |
| S10.3 | 发布失败 | release fail | 自动回滚 | 预警 | DeployWatcher→Rollbacker→Notifier |

### A.11 场景统计与关键原则

| 阶段 | 场景数 | 可自动 | 需确认 |
|------|--------|--------|--------|
| 需求评审 | 5 | 3 | 5 |
| 需求签署 | 3 | 2 | 3 |
| 概要设计 | 4 | 2 | 4 |
| 详细设计 | 4 | 2 | 4 |
| 任务分配 | 4 | 2 | 4 |
| 代码开发 | 4 | 2 | 4 |
| Bug处理 | 5 | 3 | 5 |
| 测试执行 | 4 | 3 | 4 |
| 测试验收 | 3 | 1 | 3 |
| 发布 | 3 | 1 | 3 |
| **总计** | **39** | **21** | **39** |

**关键原则**：
1. 循环类（补充后再次评审、修正后再次评审、Bug修复后再次验收）：自动触发下一次
2. 预警类（多次反复、TODO超时、代码冲突、发布失败）：自动+人工确认
3. 签署类（需求签署、设计签署、验收签署）：必须人工确认

---

**签字**: 
- Agent2 ✅ 2026-02-19
- Agent1 ✅ 2026-02-19
