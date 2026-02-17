# 2.2 Agent资源池与分配机制

## 目标
设计Agent资源池管理和自动分配机制。

## 设计

### 2.2.1 人员配置

用户给每个人分配Agent数量：

```yaml
# 用户(我)的配置
agent_allocation:
  郭汉盟:
    count: 5        # 分配5个Agent
    role: "后端开发"
    
  李杨峰:
    count: 10       # 分配10个Agent
    role: "AI开发"
    
  陈伟:
    count: 3        # 分配3个Agent
    role: "前端开发"
```

### 2.2.2 PM-Agent分配流程

```
用户选择执行人员 (如: 李杨峰)
    │
    ▼
PM-Agent获取该人员Agent池
    │
    ▼
检查空闲Agent
    │
    ├─ 有空闲 → 分配给项目组
    │
    └─ 无空闲 → 提示用户
```

### 2.2.3 自动分配算法

```python
def auto_assign(owner: str, project: str, count: int = 1) -> List[str]:
    """
    自动分配Agent
    
    策略:
    1. 优先分配idle状态久的
    2. 同一项目尽量分配不同的Agent
    3. 考虑Agent的skills匹配
    """
    
    agents = get_agents_by_owner(owner)
    
    # 过滤idle的
    idle_agents = [a for a in agents if a.status == 'idle']
    
    # 按idle时长排序（久的优先）
    idle_agents.sort(key=lambda a: a.idle_since)
    
    # 分配
    assigned = []
    for agent in idle_agents[:count]:
        agent.status = 'assigned'
        agent.current_project = project
        agent.assigned_at = now()
        assigned.append(agent.id)
        
    return assigned
```

### 2.2.4 项目组建立时分配

```yaml
# PM-Agent操作
project_creation:
  name: "金融法院卷宗系统"
  team:
    - member: "郭汉盟"
      role: "后端"
      agents_needed: 2
      
    - member: "李杨峰"
      role: "AI"
      agents_needed: 2
      
    - member: "陈伟"
      role: "前端"
      agents_needed: 1
  
  # 自动分配结果
  allocation:
    郭汉盟:
      - agent2-001
      - agent2-002
      
    李杨峰:
      - agent3-001
      - agent3-002
      
    陈伟:
      - agent4-001
```

### 2.2.5 Agent入组后状态

```yaml
# 项目内的agents.yaml
agents:
  - id: "agent2-001"
    owner: "郭汉盟"
    project: "金融法院卷宗系统"
    status: "assigned"
    joined_at: "2026-02-10T10:00:00Z"
    tasks:
      - TODO-2-001  # 当前任务
      - TODO-2-002  # 队列中
      
  # 项目外的Agent状态
  pool_status:
    idle: 3
    busy: 2
```

## 结论

### Agent分配机制

1. **用户分配**: 每个人分配固定数量Agent
2. **自动分配**: PM-Agent根据忙闲自动分配
3. **入组后**: Agent交给oc-collab管理

### 分配流程

```
用户 → 选择执行人员 → PM-Agent分配 → Agent入组 → oc-collab接管
```

### 状态管理

- PM-Agent管理: idle/busy
- oc-collab管理: working/completed

---

**结论**: Agent资源池和分配机制设计完成。
