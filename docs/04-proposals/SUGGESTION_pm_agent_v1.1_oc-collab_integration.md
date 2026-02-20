# PM-Agent 与 oc-collab 协同建议

**致**: PM-Agent 产品经理  
**日期**: 2026-02-19  
**角色**: Consultant

---

## 一、协同逻辑

```
PM-Agent (入口层)
      │
      ├── 客户材料输入 → 问题识别
      │
      ▼
oc-collab (执行层) ◄─── 调用CLI ─── PM-Agent
      │
      ├── Agent1: 创建TODO
      ├── Agent2: 执行任务
      └── 状态回传 → PM-Agent
```

**核心原则**：
- PM-Agent 是**入口**，负责接收客户材料、识别问题
- oc-collab 是**执行框架**，负责任务分配、执行、跟踪
- 两者通过 **CLI调用** + **Git同步** 协同

---

## 二、协同路径

### 路径1：问题下发（PM-Agent → oc-collab）

```
客户材料 → PM-Agent识别问题 → 调用oc-collab todowrite创建TODO → oc-collab执行 → 状态回传
```

### 路径2：状态同步（双向）

```
oc-collab执行中 ←→ Git状态同步 ←→ PM-Agent查询
```

### 路径3：Agent管理

```
PM-Agent → oc-collab agent register/listen → 启动Agent进程
```

---

## 三、V1.1 功能对照

| PM-Agent功能 | 是否需要oc-collab | 调用的CLI |
|-------------|------------------|----------|
| **1.1 Agent管理** | | |
| Agent ID分配 | ✅ | `oc-collab agent register` |
| TODO寻址 | ✅ | `oc-collab agent list` |
| 启动/关闭 | ✅ | `oc-collab agent listen -- `--daemon` /stop` |
| **1.2 Prompt模板** | | |
| 启动模板管理 | ❌ | 配置管理 |
| agent.md生成 | ❌ | 配置管理 |
| **1.3 问题同步** | | |
| 自动推送问题 | ✅ | `oc-collab todowrite --content "..." --to agent2 --source REQUIREMENT/BUG` |
| 状态同步 | ✅ | `oc-collab todo list` + Git轮询 |
| **2.2 文件同步** | | |
| 自动同步 | ⚠️ 可选 | `oc-collab push` / 直接Git |
| **2.3 自动功能** | | |
| 自动创问题 | ✅ | `oc-collab todowrite` |
| **V1.2 跨项目查询** | ✅ v2.3.3 | `oc-collab project list/status/todos` |

---

## 三、V1.1 功能对照（修正版）

### 4.1 问题下发示例

```python
import subprocess

# PM-Agent识别到BUG，转发给oc-collab
result = subprocess.run([
    "oc-collab", "todowrite",
    "--content", "修复用户登录失败问题",
    "--priority", "high",
    "--source", "BUG",
    "--to", "agent2"  # 指派给Agent2处理
], capture_output=True, text=True)

# 解析返回的TODO编号
todo_id = result.stdout.strip()  # 例如: TODO-3to2-001
```

### 4.2 状态查询示例

```python
# 查询待处理的TODO
result = subprocess.run([
    "oc-collab", "todo", "list",
    "--status", "pending"
], capture_output=True, text=True)

# 查看具体TODO详情
result = subprocess.run([
    "oc-collab", "todo", "show", "TODO-3to2-001"
], capture_output=True, text=True)
```

### 4.3 Agent监听

```python
# 启动Agent监听进程（接收TODO通知）
subprocess.Popen(
    ["oc-collab", "agent", "listen", "--daemon"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
```

### 4.4 跨项目信息查询（V1.2+）

```python
# 列出所有项目（需内部子系统权限）
result = subprocess.run([
    "oc-collab", "project", "list"
], capture_output=True, text=True)

# 查看某项目状态
result = subprocess.run([
    "oc-collab", "project", "金融法院卷宗系统", "status"
], capture_output=True, text=True)

# 查看某项目TODO
result = subprocess.run([
    "oc-collab", "project", "金融法院卷宗系统", "todos"
], capture_output=True, text=True)
```

**说明**: 跨项目查询能力计划在 oc-collab v2.3.3 中实现，PM-Agent v1.2 可用。

---

## 五、不需要调用oc-collab的功能

| 功能 | 说明 |
|------|------|
| 客户材料OCR/转写 | PM-Agent独立处理 |
| 问题分类（BUG vs 需求） | PM-Agent独立处理（调用dossierai） |
| 文件整合 | PM-Agent独立处理 |
| 前端界面 | PM-Agent独立 |

---

## 六、参考文档

- **oc-collab使用指南**: `docs/07-research/RESEARCH_oc-collab_capabilities_for_PM-Agent.md`
- **oc-collab核心架构**: `docs/00-architecture/CORE_ARCHITECTURE.md`

---

**有任何问题随时沟通**
