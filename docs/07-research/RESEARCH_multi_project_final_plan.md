# 多项目管理体系 - 最终实施方案

**日期**: 2026-02-17  
**目标**: 一周内建立可运行的PM-Agent + oc-collab多项目管理体系

---

## 一、整体架构

```
用户(我) → PM-Agent → 项目组建立 → Agent入组 → oc-collab协调
                              ↓
                         Gitee仓库
```

---

## 二、实施计划 (4周)

### 第一周: 基础设施 (Day 1-7)

#### 2.1 创建目录结构

```bash
# 在本地创建
mkdir -p projects/{_templates,_shared}
mkdir -p projects/_templates/project_template/{docs/{01-requirements,02-design,03-test,04-progress},src,config,data,tests}

# 复制到Gitee
git clone qushen-data/projects
```

#### 2.2 创建项目模板文件

| 文件 | 位置 | 用途 |
|------|------|------|
| PROJECT.md | 项目根目录 | 项目概览 |
| project.yaml | 项目根目录 | 机器可读配置 |
| agents.yaml | 项目根目录 | Agent配置 |
| repos.yaml | 项目根目录 | 仓库配置 |
| TASKS.md | 项目根目录 | 当前任务 |

#### 2.3 Gitee仓库

需要创建的仓库 (8个):

| 仓库名 | 用途 | 语言 |
|--------|------|------|
| court-risk-assessment | 诉讼风险评估 | Python |
| proc-org-service | 组织智能化 | ? |
| proc-ops-log | 运维log | ? |
| proc-video-management | 视频管理 | ? |
| proc3-case-analysis | 案件分析 | ? |
| env-impact-assessment | 环评审核 | ? |
| env-data-extract | 数据提取 | Python |
| xuhui-admin-doc | 行政复议 | ? |

---

### 第二周: Agent管理 (Day 8-14)

#### 2.4 Agent注册

```bash
# 注册Agent (示例: 给李杨峰注册10个)
oc-collab agent register --owner "李杨峰" --skills "Python,FastAPI" --count 10

# 给郭汉盟注册
oc-collab agent register --owner "郭汉盟" --skills "Java,Spring" --count 5

# 给陈伟注册
oc-collab agent register --owner "陈伟" --skills "Vue,TypeScript" --count 3
```

#### 2.5 Agent池状态

```yaml
# projects/agents_global.yaml
pools:
  李杨峰:
    total: 10
    available: 10
  郭汉盟:
    total: 5
    available: 5
  陈伟:
    total: 3
    available: 3
```

---

### 第三周: 项目管理 (Day 15-21)

#### 2.6 创建第一个项目

```bash
# 创建金融法院卷宗项目
pm-agent project create \
  --name "金融法院卷宗系统" \
  --customer "金融法院" \
  --priority "P0"

# 添加成员并自动分配Agent
pm-agent project add-member "金融法院卷宗系统" --member "郭汉盟" --role "后端" --agents 2
pm-agent project add-member "金融法院卷宗系统" --member "李杨峰" --role "AI" --agents 3
pm-agent project add-member "金融法院卷宗系统" --member "陈伟" --role "前端" --agents 1
```

#### 2.7 项目结构

```
金融法院卷宗系统/
├── PROJECT.md              # 项目概览
├── project.yaml          # 配置
├── agents.yaml           # Agent配置 (6个Agent)
├── repos.yaml            # 仓库配置 (4个仓库)
├── skills.yaml           # Skill配置
└── docs/
    ├── 01-requirements/
    ├── 02-design/
    ├── 03-test/
    └── 04-progress/
```

---

### 第四周: 协作与统计 (Day 22-28)

#### 2.8 oc-collab集成

- Agent入组后，读取TASKS.md获取任务
- 执行完成后更新状态
- Git提交同步到仓库

#### 2.9 统计报告

```bash
# 每日报告
pm-agent report daily

# 输出:
# - 今日代码提交: 12
# - 今日TODO完成: 5
# - 新增Bug: 2
# - 部署: 1
```

---

## 三、核心文件

### 3.1 项目配置

```yaml
# project.yaml
project:
  id: "PJ-001"
  name: "金融法院卷宗系统"
  customer: "金融法院"
  priority: "P0"
  deadline: "2026-12-31"
  
team:
  - name: "郭汉盟"
    role: "后端"
    agents: ["agent2-001", "agent2-002"]
  - name: "李杨峰"
    role: "AI"
    agents: ["agent3-001", "agent3-002", "agent3-003"]
  - name: "陈伟"
    role: "前端"
    agents: ["agent4-001"]
```

### 3.2 Agent配置

```yaml
# agents.yaml
agents:
  - id: "agent2-001"
    owner: "郭汉盟"
    project: "金融法院卷宗系统"
    status: "assigned"
    skills: ["Java", "Spring Boot"]
```

### 3.3 仓库配置

```yaml
# repos.yaml
repositories:
  - name: "dossierai"
    path: "qushen-data/dossierai"
    agents: ["agent3-001"]
  - name: "financial-court-file-assistant"
    path: "qushen-data/financial-court-file-assistant"
    agents: ["agent2-001"]
```

---

## 四、立即执行清单

### Day 1-2: 目录与模板

- [ ] 创建 projects/ 目录结构
- [ ] 创建项目模板文件
- [ ] 初始化全局配置 (registry.yaml, agents_global.yaml)

### Day 3-4: Gitee仓库

- [ ] 创建 8个新仓库
- [ ] 迁移 lhjczs_java_backend
- [ ] 清理空仓库

### Day 5-7: Agent注册

- [ ] 实现 agent register 命令
- [ ] 给3人注册Agent
- [ ] 验证Agent池状态

### Day 8-14: 项目管理

- [ ] 实现 project create 命令
- [ ] 实现 project add-member 命令
- [ ] 创建第一个项目

### Day 15-21: oc-collab集成

- [ ] Agent读取TASKS.md
- [ ] Agent执行任务
- [ ] Git提交同步

### Day 22-28: 统计

- [ ] 实现代码提交统计
- [ ] 实现TODO完成统计
- [ ] 生成每日报告

---

## 五、关键文件位置

```
本地项目根目录/
│
├── projects/                          # 所有项目
│   ├── _templates/                    # 项目模板
│   ├── _shared/                      # 共享资源
│   ├── registry.yaml                  # 项目注册表
│   ├── agents_global.yaml             # 全局Agent注册表
│   │
│   └── 金融法院卷宗系统/              # 项目1
│       ├── PROJECT.md
│       ├── project.yaml
│       ├── agents.yaml
│       ├── repos.yaml
│       └── docs/
│
└── oc-collab/                        # oc-collab项目
    └── (现有结构)
```

---

## 六、PM-Agent命令清单

```bash
# Agent管理
oc-collab agent register --owner "姓名" --skills "技能" --count N
oc-collab agent list
oc-collab agent status --agent ID
oc-collab agent unregister --agent ID

# 项目管理
pm-agent project create --name "项目名" --customer "客户"
pm-agent project add-member --project "项目" --member "姓名" --role "角色"
pm-agent project list

# 统计
pm-agent report daily --project "项目"
pm-agent report weekly --project "项目"
```

---

## 七、成功标准

- [ ] 目录结构创建完成
- [ ] 8个新仓库创建完成
- [ ] 18个Agent注册完成 (李10+郭5+陈3)
- [ ] 第一个项目创建成功
- [ ] Agent能读取TASKS.md执行任务
- [ ] 每日报告能生成

---

**结论**: 本方案可在4周内建立完整的多项目管理体系，实现PM-Agent管理项目、oc-collab协调Agent的目标。

**下一步**: 确认后开始执行第一周任务。
