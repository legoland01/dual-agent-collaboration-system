# Agent Welcome 提示词机制

**日期**: 2026-02-18  
**版本**: v1.0

---

## 一、机制设计

### 1.1 功能说明

每个Agent加入项目后，PM-Agent生成一条"Welcome提示词"，包含：
- 项目当前状态
- 待处理任务
- 协作注意事项

Agent每次session重启时，第一句输入自动读取这条提示词。

### 1.2 数据结构

```yaml
# PM-Agent 数据库: agent_welcome 表
agent_welcome:
  - agent_id: agent1-001
    project_id: 1
    welcome_message: |
      欢迎加入金融法院卷宗系统项目！
      
      当前状态：
      - 待处理BUG: 3个
      - 待处理需求: 2个
      
      你的任务：
      - 修复 TODO-1to2-001
      
    created_at: "2026-02-18T10:00:00Z"
    updated_at: "2026-02-18T10:00:00Z"
```

### 1.3 API设计

```bash
# Agent获取Welcome提示词
GET /api/agents/{agent_id}/welcome?project_id={project_id}

# PM-Agent更新Welcome提示词
PUT /api/agents/{agent_id}/welcome
{
  "project_id": 1,
  "welcome_message": "..."
}

# 生成Welcome提示词（PM-Agent调用）
POST /api/agents/{agent_id}/welcome/generate
{
  "project_id": 1,
  "include": ["tasks", "context", "notices"]
}
```

### 1.4 Welcome提示词模板

```markdown
欢迎加入{项目名}项目！

## 当前状态
{项目状态摘要}

## 你的任务
{待处理TODO列表}

## 注意事项
{项目协作规则}

## 上次进度
{上次session完成的工作}
```

---

## 二、Agent获取流程

```
1. Agent启动
   │
   ▼
2. 读取环境变量 OC_AGENT_ID, OC_PROJECT_ID
   │
   ▼
3. 调用 PM-Agent API 获取Welcome
   curl http://localhost:8000/api/agents/${OC_AGENT_ID}/welcome?project_id=${OC_PROJECT_ID}
   │
   ▼
4. 如果有Welcome，显示并作为第一条输入
   │
   ▼
5. 继续处理TODO队列
```

---

## 三、PM-Agent生成逻辑

```python
async def generate_welcome(agent_id: str, project_id: int) -> str:
    """生成Welcome提示词"""
    
    # 1. 获取项目状态
    project = get_project(project_id)
    todos = get_project_todos(project_id)
    my_todos = [t for t in todos if t.assignee == agent_id]
    
    # 2. 获取最近活动
    recent_commits = get_recent_commits(project_id, limit=5)
    
    # 3. 组装Welcome
    welcome = f"""欢迎加入{project.name}项目！

## 当前状态
- 项目进度: {project.progress}%
- 待处理BUG: {bug_count}
- 待处理需求: {req_count}

## 你的任务
{my_todos_list}

## 注意事项
{get_project_notices(project_id)}

## 上次进度
{recent_commits_summary}
"""
    return welcome
```

---

## 四、集成到Agent启动脚本

```bash
#!/bin/bash
# Agent启动脚本

export OC_AGENT_ID=${1:-agent1-001}
export OC_PROJECT_ID=${2:-1}

# 获取Welcome提示词
WELCOME=$(curl -s "http://localhost:8000/api/agents/${OC_AGENT_ID}/welcome?project_id=${OC_PROJECT_ID}")

# 显示Welcome
echo "$WELCOME"

# 启动oc-collab
oc-collab start --agent $OC_AGENT_ID --project-id $OC_PROJECT_ID
```

---

## 五、存储位置

| 数据 | 存储位置 |
|------|----------|
| Welcome提示词 | PM-Agent SQLite: `agent_welcome`表 |
| 项目状态 | PM-Agent SQLite: `projects`表 |
| 待处理TODO | oc-collab: `state/agent_adhoc_todos.yaml` |

---

## 六、同步机制

```
oc-collab TODO变更
    │
    ▼
触发Webhook到PM-Agent
    │
    ▼
PM-Agent更新Welcome提示词
    │
    ▼
Agent下次重启获取最新Welcome
```
