# 2.1 Agent注册机制

## 目标
设计如何注册Agent，建立Agent与开发人员的绑定关系。

## 设计

### 2.1.1 Agent ID规范

```
agent{人员编号}-{Agent序号}

示例:
agent2-001  # 郭汉盟的第1个Agent
agent2-002  # 郭汉盟的第2个Agent
agent3-001  # 李杨峰的第1个Agent
```

### 2.1.2 Agent注册流程

```
用户(我)
  │
  ▼
创建Agent → 分配ID → 绑定人员 → 设置配置 → 注册到全局表
```

### 2.1.3 注册命令

```bash
# 注册新Agent
oc-collab agent register --owner "郭汉盟" --skills "Java,Spring" --count 5

# 查看Agent列表
oc-collab agent list

# 查看Agent状态
oc-collab agent status --agent agent2-001

# 注销Agent
oc-collab agent unregister --agent agent2-001
```

### 2.1.4 Agent配置文件

```yaml
# agent.yaml (全局)
agents:
  - id: "agent2-001"
    owner: "郭汉盟"
    email: "guo@company.com"
    
    # 技术信息
    tech:
      language: "Java"
      framework: "Spring Boot"
      ide: "IntelliJ IDEA"
      
    # 能力
    skills:
      - name: "Java开发"
        level: "expert"
      - name: "Spring Boot"
        level: "expert"
      - name: "MySQL"
        level: "advanced"
        
    # 状态
    status: "idle"  # idle/busy/assigned/offline
    current_project: null
    
    # Git配置
    git:
      name: "郭汉盟"
      email: "guo@company.com"
      ssh_key: "~/.ssh/gitee_rsa"
      
    # 可访问仓库
    repositories:
      - "qushen-data/financial-court-file-assistant"
      - "qushen-data/lhjczs_java_backend"
      
    # 创建时间
    created_at: "2026-01-15T10:00:00Z"
    last_active: "2026-02-17T14:30:00Z"
```

### 2.1.5 Agent注册表

```yaml
# projects/agents_global.yaml
version: "1.0"
updated: "2026-02-17T14:30:00Z"

# 按人员分组
pools:
  郭汉盟:
    total: 5
    available: 3
    agents:
      - id: "agent2-001"
        status: "busy"
        project: "金融法院卷宗"
        since: "2026-02-10"
        
      - id: "agent2-002"
        status: "idle"
        
      - id: "agent2-003"
        status: "idle"
        
  李杨峰:
    total: 10
    available: 8
    agents:
      - id: "agent3-001"
        status: "idle"
      # ... 共10个
      
  陈伟:
    total: 3
    available: 2
    agents:
      - id: "agent4-001"
        status: "busy"
        project: "金融法院卷宗"
      - id: "agent4-002"
        status: "idle"

# 统计
stats:
  total_agents: 18
  idle: 13
  busy: 5
  offline: 0
```

### 2.1.6 Agent状态机

```
     ┌─────────────────────────────────────┐
     │                                     │
     ▼                                     │
 idle ──▶ busy ──▶ idle                    │
   │        │                             │
   │        ▼                             │
   │      offline ◀──── idle              │
   │                                     │
   └─────────────────────────────────────┘

状态说明:
- idle: 空闲，可分配新任务
- busy: 工作中，有任务在执行
- offline: 离线，不可用
```

### 2.1.7 Agent分配逻辑

```python
def allocate_agent(owner: str, project: str, skills_needed: List[str]) -> str:
    """
    分配Agent
    
    1. 获取该人员的所有Agent
    2. 过滤掉busy的
    3. 匹配skills
    4. 返回第一个空闲的
    """
    
    # 伪代码
    agents = get_agents_by_owner(owner)
    available = [a for a in agents if a.status == 'idle']
    
    if not available:
        # 需要创建新Agent
        return create_new_agent(owner)
    
    # 分配第一个可用的
    agent = available[0]
    agent.status = 'assigned'
    agent.current_project = project
    agent.assigned_at = now()
    
    return agent.id
```

## 实施

### 注册命令实现

```python
# oc-collab/agent_commands.py

@agent.command()
def register(owner: str, skills: List[str], count: int = 1):
    """注册新Agent"""
    
    # 1. 确定人员编号
    owner_id = get_owner_id(owner)  # 郭汉盟 → 2
    
    # 2. 分配Agent ID
    for i in range(1, count + 1):
        agent_id = f"agent{owner_id}-{i:03d}"
        
        # 3. 创建配置
        config = {
            'id': agent_id,
            'owner': owner,
            'skills': skills,
            'status': 'idle',
            'created_at': now()
        }
        
        # 4. 保存到全局注册表
        save_agent_config(config)
        
    print(f"已注册 {count} 个Agent")
```

## 结论

### Agent注册机制

1. **ID规范**: agent{人员编号}-{序号}
2. **注册命令**: oc-collab agent register
3. **状态管理**: idle/busy/assigned/offline
4. **全局注册表**: projects/agents_global.yaml
5. **自动分配**: PM-Agent根据忙闲自动分配

### 关键功能

- 按人员创建Agent池
- Agent状态自动管理
- 自动分配空闲Agent
- 与项目绑定

---

**结论**: Agent注册机制设计完成，支持按人员创建Agent池，自动分配。
