# Agent注册与管理规范

**日期**: 2026-02-18  
**版本**: v1.0

---

## 一、三支Agent队伍规划

### 1.1 Agent ID 规则

```
agent{开发者编号}-{序号}

开发者编号：
- 1 = 李杨峰 (Python)
- 2 = 郭汉盟 (Java)  
- 3 = 陈伟 (Vue/JS)
```

| 开发者 | Agent数量 | ID范围 | 技术栈 |
|--------|-----------|--------|--------|
| 李杨峰 | 10 | agent1-001 ~ agent1-010 | Python |
| 郭汉盟 | 5 | agent2-001 ~ agent2-005 | Java |
| 陈伟 | 3 | agent3-001 ~ agent3-003 | Vue/JS |

### 1.2 Agent职责

| Agent类型 | 职责 | 技能要求 |
|-----------|------|----------|
| **agent1-*** | 需求分析、BUG分析、文档创建 | Agent1能力 |
| **agent2-*** | 代码开发、Bug修复、功能实现 | Agent2能力 |
| **agent3-*** | 前端开发、UI实现、样式调整 | Vue/JS能力 |

### 1.3 初始状态

- **无需注册**：Agent启动时自动注册到 `projects/agents_global.yaml`
- **无需分配**：Agent启动时检查TODO队列，处理积压任务

---

## 二、全局Agent注册表

### 2.1 agents_global.yaml

```yaml
# projects/agents_global.yaml
agents:
  - id: agent1-001
    owner: 李杨峰
    owner_id: 1
    skill: python
    status: idle  # idle | assigned | offline
    current_project: null
    registered_at: "2026-02-18T10:00:00Z"
    
  - id: agent1-002
    owner: 李杨峰
    owner_id: 1
    skill: python
    status: assigned
    current_project: 金融法院卷宗系统
    registered_at: "2026-02-18T10:00:00Z"
    
  # ... 共18个Agent

developers:
  - id: 1
    name: 李杨峰
    skill: python
    agent_count: 10
    agent_ids: [agent1-001, agent1-002, ..., agent1-010]
    
  - id: 2
    name: 郭汉盟
    skill: java
    agent_count: 5
    agent_ids: [agent2-001, ..., agent2-005]
    
  - id: 3
    name: 陈伟
    skill: vuejs
    agent_count: 3
    agent_ids: [agent3-001, agent3-002, agent3-003]
```

### 2.2 项目级 agents.yaml

```yaml
# projects/金融法院/agents.yaml
project: 金融法院卷宗系统
agents:
  - id: agent1-001
    role: backend_developer
    status: active
    assigned_at: "2026-02-18T10:00:00Z"
    
  - id: agent1-002
    role: backend_developer
    status: active
    assigned_at: "2026-02-18T10:00:00Z"

  - id: agent3-001
    role: frontend_developer
    status: active
    assigned_at: "2026-02-18T10:00:00Z"
```

---

## 三、Session重启指令

### 3.1 每个Agent的启动命令

```bash
# Agent1-001 (李杨峰的第1个Agent)
export OC_AGENT_ID=agent1-001
export OC_DEVELOPER_ID=1
oc-collab start --project 金融法院卷宗系统

# Agent1-002
export OC_AGENT_ID=agent1-002
export OC_DEVELOPER_ID=1
oc-collab start --project 金融法院卷宗系统

# Agent2-001 (郭汉盟的第1个Agent)
export OC_AGENT_ID=agent2-001
export OC_DEVELOPER_ID=2
oc-collab start --project 金融法院卷宗系统
```

### 3.2 批量启动脚本

```bash
#!/bin/bash
# 启动李杨峰的所有Agent
for i in $(seq -w 1 10); do
  export OC_AGENT_ID=agent1-$i
  export OC_DEVELOPER_ID=1
  oc-collab start --project 金融法院卷宗系统 &
done

# 启动郭汉盟的Agent
for i in $(seq -w 1 5); do
  export OC_AGENT_ID=agent2-$i
  export OC_DEVELOPER_ID=2
  oc-collab start --project 金融法院卷宗系统 &
done

# 启动陈伟的Agent
for i in $(seq -w 1 3); do
  export OC_AGENT_ID=agent3-$i
  export OC_DEVELOPER_ID=3
  oc-collab start --project 金融法院卷宗系统 &
done
```

---

## 四、agents.md 设计

### 4.1 设计决策

**采用方案B：每个项目统一 agents.yaml**

理由：
1. Agent加入项目后，由oc-collab在项目内协调
2. 全局Agent状态在 `agents_global.yaml` 中统一管理
3. 项目内只需知道哪些Agent在本项目
4. 避免每个Agent维护独立配置文件的复杂性

### 4.2 文件结构

```
projects/
├── agents_global.yaml          # 全局Agent注册表（所有Agent状态）
├── 金融法院/
│   ├── agents.yaml             # 项目内Agent列表
│   ├── PROJECT.md
│   └── ...
├── 上海市检察院/
│   ├── agents.yaml
│   └── ...
```

### 4.3 agents.yaml 内容

```yaml
# projects/金融法院/agents.yaml
project:
  name: 金融法院卷宗系统
  customer: 金融法院
  
agents:
  - id: agent1-001
    developer: 李杨峰
    skill: python
    role: backend_developer
    status: active
    joined_at: "2026-02-18T10:00:00Z"
    
  - id: agent1-002
    developer: 李杨峰
    skill: python
    role: backend_developer
    status: active
    joined_at: "2026-02-18T10:00:00Z"

  - id: agent3-001
    developer: 陈伟
    skill: vuejs
    role: frontend_developer
    status: active
    joined_at: "2026-02-18T10:00:00Z"
```

---

## 五、Agent启动流程

```
1. Agent启动
   │
   ▼
2. 读取环境变量 OC_AGENT_ID, OC_DEVELOPER_ID
   │
   ▼
3. 注册到 agents_global.yaml (如未注册)
   │
   ▼
4. 读取当前项目目录 (环境变量或参数)
   │
   ▼
5. 读取项目级 agents.yaml
   │
   ▼
6. 检查 TODO 队列 (TODO-1toX-xxx)
   │
   ▼
7. 处理积压任务 或 等待新任务
```

---

## 六、oc-collab 需要新增的命令

```bash
# Agent注册
oc-collab agent register --agent-id <ID> --developer-id <ID>

# Agent状态更新
oc-collab agent status --agent-id <ID> --project <项目>

# 项目内Agent列表
oc-collab project agents --project <项目>

# Agent上线通知 (Webhook)
oc-collab webhook register --event agent.online --url <URL>
```

---

**下一步**: 等待确认后更新ROADMAP_COORDINATION.md
