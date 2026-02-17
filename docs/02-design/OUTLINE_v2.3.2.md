# 概要设计文档：oc-collab v2.3.2

**版本**: v1 (DRAFT)  
**创建日期**: 2026-02-17  
**作者**: Agent 1 (产品经理)  
**关联需求**: requirements_v2.3.2.md  
**版本号**: 2.3.2

---

## 1. 设计目标

v2.3.2的核心目标：
1. **产品化POC成果**: 将OpenCode Question Tool通知方案集成到oc-collab
2. **简化配置**: 用户通过`notify enable`一键启用
3. **增强交互**: 支持在OpenCode界面直接操作TODO

---

## 2. 功能模块

### 2.1 模块划分

| 模块ID | 模块名称 | 功能ID | 优先级 |
|--------|----------|--------|--------|
| M1 | InstructionGenerator | F-NOTIF-001 | P0 |
| M2 | TodoInteraction | F-NOTIF-002 | P0 |
| M3 | NotifyCLI | F-NOTIF-003 | P1 |
| M4 | NotifyHistory | F-NOTIF-004 | P2 |

### 2.2 模块关系

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Instruction │     │   Notify    │     │    Todo    │
│  Generator  │────▶│    CLI      │────▶│Interaction │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────┐
│              state/notification_history.yaml         │
└─────────────────────────────────────────────────────┘
```

---

## 3. 技术架构

### 3.1 技术选型

| 技术 | 选型 | 说明 |
|------|------|------|
| 配置格式 | YAML | 与现有体系一致 |
| 指令模板 | Jinja2 | 已有依赖 |
| CLI框架 | Click | 已有依赖 |
| 文件存储 | JSON/YAML | 轻量级 |

### 3.2 文件结构

```
src/
├── core/
│   ├── instruction_generator.py   # M1: Instruction生成
│   └── notify_history.py          # M4: 通知历史
├── cli/
│   ├── notify_commands.py         # M3: notify命令
│   └── interaction_handler.py     # M2: TODO交互处理
└── templates/
    └── TODO_NOTIFY.md.j2          # Instruction模板

config/
├── notification.yaml              # 通知配置
└── instructions/
    └── TODO_NOTIFY.md             # 生成的Instruction文件
```

---

## 4. 模块设计

### 4.1 M1: InstructionGenerator

**功能**: 生成OpenCode instruction文件

**核心方法**:
```python
class InstructionGenerator:
    def generate(self, output_path: str) -> bool:
        """生成TODO_NOTIFY.md"""
        
    def validate(self, instruction_path: str) -> bool:
        """验证instruction文件"""
        
    def update_template(self, template_path: str) -> bool:
        """更新instruction模板"""
```

**Instruction内容**:
```markdown
# TODO通知处理规则

当用户告知"我有新TODO"或"查看TODO"时：
1. 读取 state/agent_adhoc_todos.yaml
2. 查找未读的TODO
3. 使用 question tool 询问用户操作

question tool 调用示例：
{
  "name": "question",
  "arguments": {
    "questions": [{
      "header": "新TODO处理",
      "question": "您有新TODO: {todo_id} - {content}",
      "options": [
        {"label": "立即执行", "description": "开始处理此TODO"},
        {"label": "稍后处理", "description": "设置提醒"},
        {"label": "查看详情", "description": "显示完整内容"}
      ]
    }]
  }
}
```

### 4.2 M2: TodoInteraction

**功能**: 处理用户在question窗口的操作

**核心方法**:
```python
class TodoInteraction:
    def handle_action(self, todo_id: str, action: str) -> bool:
        """处理用户选择的操作"""
        
    def execute(self, todo_id: str) -> bool:
        """立即执行"""
        
    def defer(self, todo_id: str, delay_minutes: int) -> bool:
        """稍后处理"""
        
    def reject(self, todo_id: str, reason: str) -> bool:
        """拒绝"""
```

**操作映射**:
| 用户操作 | 内部action | 处理逻辑 |
|----------|------------|----------|
| 立即执行 | execute | 标记status=in_progress |
| 稍后处理 | defer | 记录defer时间 |
| 查看详情 | view | 返回TODO详情 |
| 分配他人 | reassign | TODO-2toX |
| 拒绝 | reject | 标记status=rejected |

### 4.3 M3: NotifyCLI

**功能**: 提供notify命令组

**命令设计**:
```python
# oc-collab notify enable
# - 检查OpenCode配置
# - 生成TODO_NOTIFY.md
# - 提示用户配置opencode.json
# - 记录启用状态

# oc-collab notify disable
# - 删除TODO_NOTIFY.md
# - 更新配置状态

# oc-collab notify status
# - 显示通知开关状态
# - 显示最后通知时间
# - 显示instruction文件路径

# oc-collab notify test
# - 创建测试TODO
# - 触发通知流程
```

### 4.4 M4: NotifyHistory

**功能**: 记录通知历史

**数据结构**:
```yaml
# state/notification_history.yaml
version: "1.0"
notifications:
  - id: notif-001
    todo_id: TODO-2to1-010
    created_at: 2026-02-17T10:00:00
    user_action: executed
    user_action_at: 2026-02-17T10:01:00
    response_time_seconds: 60
```

**核心方法**:
```python
class NotifyHistory:
    def add(self, notification: dict) -> bool:
        """添加通知记录"""
        
    def query(self, filters: dict) -> list:
        """查询通知历史"""
        
    def get_stats(self) -> dict:
        """获取统计信息"""
```

---

## 5. 数据流设计

### 5.1 通知触发流程

```
Agent创建TODO
     │
     ▼
写入 agent_adhoc_todos.yaml
     │
     ▼
生成通知记录 (NotifyHistory.add)
     │
     ▼
用户告知LLM"有新TODO"
     │
     ▼
LLM读取TODO（根据instruction）
     │
     ▼
LLM调用question tool
     │
     ▼
用户选择操作
     │
     ▼
TodoInteraction.handle_action()
     │
     ▼
更新TODO状态/记录操作结果
```

### 5.2 配置启用流程

```
用户执行 notify enable
     │
     ▼
检查Python环境
     │
     ▼
生成 TODO_NOTIFY.md
     │
     ▼
显示配置指导
     │
     ▼
提示用户重启OpenCode
```

---

## 6. 接口设计

### 6.1 内部接口

| 接口 | 模块 | 方法 | 说明 |
|------|------|------|------|
| 生成Instruction | M1 | generate() | 生成md文件 |
| 处理操作 | M2 | handle_action() | 处理用户操作 |
| 启用通知 | M3 | enable() | 启用功能 |
| 添加记录 | M4 | add() | 添加历史 |

### 6.2 CLI接口

```bash
# 启用通知
oc-collab notify enable

# 禁用通知
oc-collab notify disable

# 状态查询
oc-collab notify status

# 测试通知
oc-collab notify test
```

---

## 7. 错误处理

### 7.1 异常场景

| 场景 | 处理 | 提示 |
|------|------|------|
| Instruction文件已存在 | 询问是否覆盖 | "文件已存在，是否覆盖？" |
| OpenCode配置不存在 | 警告但继续 | "请手动配置opencode.json" |
| 文件写入失败 | 报错退出 | "写入失败，检查权限" |
| TODO不存在 | 忽略操作 | "TODO不存在" |

### 7.2 日志设计

- 级别: DEBUG/INFO/WARNING/ERROR
- 输出: stdout + 日志文件

---

## 8. 测试策略

### 8.1 单元测试

| 模块 | 测试类 | 覆盖目标 |
|------|--------|----------|
| M1 | TestInstructionGenerator | 生成/验证/更新 |
| M2 | TestTodoInteraction | 5种操作 |
| M3 | TestNotifyCLI | 4个命令 |
| M4 | TestNotifyHistory | 增/查/统计 |

### 8.2 E2E测试

| 场景 | 测试步骤 |
|------|----------|
| 启用通知 | enable → 生成文件 → status确认 |
| 禁用通知 | disable → 文件删除 → status确认 |
| 通知交互 | 创建TODO → 用户操作 → 状态更新 |

---

## 9. 部署与配置

### 9.1 依赖

```toml
# pyproject.toml
dependencies = [
    "click>=8.0",
    "pyyaml>=6.0",
    "jinja2>=3.0",
]
```

### 9.2 新增文件

| 文件 | 说明 |
|------|------|
| src/core/instruction_generator.py | Instruction生成器 |
| src/core/notify_history.py | 通知历史管理 |
| src/cli/notify_commands.py | notify命令组 |
| src/cli/interaction_handler.py | 交互处理器 |
| config/notification.yaml | 默认配置 |

---

## 10. 兼容性

### 10.1 向后兼容

- v2.3.1的agent listen功能保持不变
- 新旧通知机制可共存
- 配置文件可迁移

### 10.2 版本号

- 当前版本: 2.3.1
- 目标版本: 2.3.2

---

**状态**: DRAFT  
**待评审**: Agent2

