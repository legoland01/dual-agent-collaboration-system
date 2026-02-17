# 1.3 项目配置模板

## 目标
设计每个项目的标准配置模板，便于PM-Agent和oc-collab读取。

## 设计

### 1.3.1 项目配置文件

每个项目根目录需要以下配置文件：

```
项目名/
├── PROJECT.md              # 项目概览(人可读)
├── project.yaml           # 项目配置(机器可读)
├── agents.yaml            # 项目Agent配置
├── repos.yaml             # 项目仓库配置
└── skills.yaml            # 项目Skill配置
```

### 1.3.2 project.yaml

```yaml
# 项目配置
project:
  id: "PJ-001"
  name: "金融法院卷宗系统"
  short_name: "court-financial"
  
  # 基本信息
  customer: "金融法院"
  priority: "P0"
  deadline: "2026-12-31"
  
  # 团队成员
  team:
    - role: "后端负责"
      name: "郭汉盟"
      agent: "agent2-001"
      
    - role: "前端负责"
      name: "陈伟"
      agent: "agent4-001"
      
    - role: "AI负责"
      name: "李杨峰"
      agent: "agent3-001"
  
  # 时间线
  timeline:
    start: "2026-01-01"
    end: "2026-12-31"
    milestones:
      - name: "MVP完成"
        date: "2026-06-30"
      - name: "上线"
        date: "2026-12-31"
  
  # 状态
  status: "进行中"
  progress: 45
  
# 需求
requirements:
  total: 4
  completed: 1
  in_progress: 2
  pending: 1

# 代码统计
code:
  commits_today: 12
  commits_total: 156
  lines_added: 5000
  lines_deleted: 2000

# 问题统计
issues:
  open: 5
  closed: 18
  critical: 1

# 部署
deployments:
  count: 8
  last: "2026-02-15"
  status: "success"
```

### 1.3.3 agents.yaml

```yaml
# 项目Agent配置
agents:
  # Agent池配置
  pool:
    - agent_id: "agent2-001"
      owner: "郭汉盟"
      role: "后端开发"
      status: "busy"
      skills:
        - Java
        - Spring Boot
      
    - agent_id: "agent2-002"
      owner: "郭汉盟"
      role: "后端开发"
      status: "idle"
      skills:
        - Java
        - Spring Boot
      
    - agent_id: "agent4-001"
      owner: "陈伟"
      role: "前端开发"
      status: "busy"
      skills:
        - Vue
        - TypeScript
      
    - agent_id: "agent3-001"
      owner: "李杨峰"
      role: "AI开发"
      status: "idle"
      skills:
        - Python
        - FastAPI
        - RAG

  # Agent分配规则
  allocation:
    strategy: "busy_first"  # 优先分配忙碌的(已完成当前任务)
    max_per_agent: 3        # 单个Agent最多同时3个任务
    auto_assign: true       # 是否自动分配

  # 忙闲状态
  status:
    idle: 2
    busy: 2
    total: 4
```

### 1.3.4 repos.yaml

```yaml
# 项目仓库配置
repositories:
  - name: "dossierai"
    path: "qushen-data/dossierai"
    full_path: "https://gitee.com/qushen-data/dossierai"
    language: "Python"
    purpose: "卷宗处理核心"
    primary: true
    
    # 关联Agent
    agents:
      - agent3-001
      - agent3-002
      
    # 分支保护
    branches:
      - name: "main"
        protected: true
        require_review: true
        
  - name: "financial-court-file-assistant"
    path: "qushen-data/financial-court-file-assistant"
    language: "Java"
    purpose: "后端服务"
    
    agents:
      - agent2-001
      
  - name: "financial-court-file-assistant-frontend"
    path: "qushen-data/financial-court-file-assistant-frontend"
    language: "Vue/JS"
    purpose: "前端"
    
    agents:
      - agent4-001
```

### 1.3.5 skills.yaml

```yaml
# 项目Skill配置
skills:
  # 项目特定Skill
  project:
    - name: "court_financial_rules"
      description: "金融法院业务规则"
      path: "skills/court_financial_rules.md"
      
    - name: "court_dossier_flow"
      description: "卷宗处理流程"
      path: "skills/court_dossier_flow.md"
      
  # 通用Skill(从共享目录引用)
  shared:
    - "oc_collab_development_guide"
    - "oc_collab_test_acceptance_guide"
    
  # Skill更新检测
  auto_update: true
  last_check: "2026-02-17T12:00:00Z"
```

### 1.3.6 全局注册表

在projects/目录下：

```yaml
# projects/registry.yaml
projects:
  - id: "PJ-001"
    name: "金融法院卷宗系统"
    path: "./court-financial"
    status: "active"
    
  - id: "PJ-002"
    name: "徐汇司法阳光执法"
    path: "./xuhui-sunshine"
    status: "planning"

# projects/agents.yaml  
agents_global:
  # 全局Agent注册
  - agent_id: "agent2-001"
    owner: "郭汉盟"
    email: "guo@company.com"
    skills:
      - Java
      - Spring Boot
    status: "assigned"
    project: "PJ-001"
    
  - agent_id: "agent3-001"
    owner: "李杨峰"
    email: "li@company.com"
    skills:
      - Python
      - FastAPI
    status: "idle"
    
# Agent资源池(按人员)
agent_pools:
  郭汉盟:
    - agent2-001 (busy)
    - agent2-002 (idle)
    
  李杨峰:
    - agent3-001 (idle)
    - agent3-002 (idle)
    - agent3-003 (idle)
    # ... 共10个
    
  陈伟:
    - agent4-001 (busy)
    - agent4-002 (idle)
```

## 结论

### 配置文件清单

| 文件 | 用途 | 位置 |
|------|------|------|
| PROJECT.md | 项目概览(人读) | 项目根目录 |
| project.yaml | 项目配置(机器读) | 项目根目录 |
| agents.yaml | Agent配置 | 项目根目录 |
| repos.yaml | 仓库配置 | 项目根目录 |
| skills.yaml | Skill配置 | 项目根目录 |
| registry.yaml | 全局项目注册表 | projects/ |
| agents_global.yaml | 全局Agent注册表 | projects/ |

### 配置文件关系

```
projects/
├── registry.yaml          # 指向各项目
├── agents_global.yaml    # 全局Agent池
└── 项目名/
    ├── project.yaml     # 项目配置
    ├── agents.yaml     # 项目Agent
    ├── repos.yaml     # 仓库配置
    └── skills.yaml    # Skill配置
```

---

**结论**: 项目配置模板设计完成，涵盖项目、Agent、仓库、Skill四个维度。
