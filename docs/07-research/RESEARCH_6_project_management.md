# 3.x 项目管理层 & 4.x 协作层 & 5.x 统计层

## 目标
快速完成剩余研究点，形成完整方案。

---

## 3.1 项目创建流程

### 3.1.1 项目创建命令

```bash
# 创建新项目
pm-agent project create \
  --name "金融法院卷宗系统" \
  --customer "金融法院" \
  --priority "P0" \
  --deadline "2026-12-31"

# 添加团队成员
pm-agent project add-member \
  --project "金融法院卷宗系统" \
  --member "郭汉盟" \
  --role "后端" \
  --agents 2

# 分配Agent入组
pm-agent project assign-agents \
  --project "金融法院卷宗系统"
```

### 3.1.2 创建后自动生成

```
项目名/
├── PROJECT.md          # 项目概览
├── project.yaml        # 配置
├── agents.yaml        # Agent配置
├── repos.yaml         # 仓库配置
├── skills.yaml        # Skill配置
└── docs/
    ├── 01-requirements/
    ├── 02-design/
    ├── 03-test/
    └── 04-progress/
```

---

## 4.1 oc-collab集成

### 4.1.1 集成方式

- oc-collab读取项目的PROJECT.md获取任务
- Agent执行TODO，提交到项目仓库
- oc-collab更新TASKS.md

### 4.1.2 TODO分发流程

```
PM-Agent创建任务
    │
    ▼
写入项目TASKS.md
    │
    ▼
Agent读取TASKS.md
    │
    ▼
执行任务 → Git提交
    │
    ▼
更新TASKS.md状态
```

---

## 5.1 统计层设计

### 5.1.1 数据来源

| 统计项 | 数据来源 |
|--------|----------|
| 代码提交 | Gitee API |
| TODO完成 | TASKS.md |
| Bug数量 | Gitee Issue |
| 部署 | 部署记录 |

### 5.1.2 每日报告

```bash
# 生成每日报告
pm-agent report daily --project "金融法院卷宗系统"

# 输出:
# - 今日代码提交数
# - 今日TODO完成数
# - 新增Bug数
# - 部署次数
```

---

## 结论汇总

### 完整架构

```
用户(我)
    │
    ▼
PM-Agent
    │
    ├── 项目管理 (创建/成员/需求)
    ├── Agent资源池 (分配/状态)
    └── 统计 (日报/周报)
    │
    ▼ 项目建立时
分配Agent入组
    │
    ▼
oc-collab
    │
    ├── TODO分发
    ├── 任务执行
    └── Git提交
    │
    ▼
Gitee仓库
```

### 实施步骤

1. **第一周: 基础设施**
   - 创建projects目录结构
   - 初始化项目模板
   - 建立仓库

2. **第二周: Agent管理**
   - 实现Agent注册
   - 实现资源池
   - 实现自动分配

3. **第三周: 项目管理**
   - 实现项目创建
   - 实现成员管理
   - 实现需求管理

4. **第四周: 协作与统计**
   - oc-collab集成
   - 统计报告
   - 试运行
