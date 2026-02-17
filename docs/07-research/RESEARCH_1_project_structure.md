# 1.1 目录结构设计

## 目标
设计每个项目的标准目录结构，便于PM-Agent和oc-collab管理。

## 分析

### 现有结构参考

#### oc-collab项目结构
```
dual-agent-collaboration-system/
├── docs/           # 文档
├── skills/         # Skill
├── src/           # 源代码
├── state/         # 状态
├── tests/         # 测试
├── config/        # 配置
└── scripts/      # 脚本
```

#### 金融法院项目现有结构
```
dossierai/
├── app/
├── configs/
├── docs/
├── examples/
├── scripts/
└── tests/

financial-court-file-assistant/
├── jshyall/
├── script/
├── pom.xml
└── README.md
```

## 设计

### 1.1.1 多项目根目录结构

```
projects/                              # 所有项目根目录
├── _templates/                       # 项目模板
│   └── project_template/
│       ├── docs/
│       │   ├── 01-requirements/
│       │   ├── 02-design/
│       │   ├── 03-test/
│       │   └── 04-progress/
│       ├── src/
│       ├── config/
│       ├── data/
│       ├── tests/
│       ├── README.md
│       ├── PROJECT.md
│       └── .gitignore
│
├── _shared/                          # 共享资源
│   ├── skills/                      # 通用Skill
│   ├── scripts/                     # 通用脚本
│   └── config/                      # 通用配置
│
├── registry.yaml                      # 项目注册表
└── agents.yaml                       # Agent注册表
```

### 1.1.2 单项目标准结构

```
项目名/
├── docs/                             # 项目文档
│   ├── 01-requirements/           # 需求文档
│   │   ├── REQ_001.md
│   │   └── index.yaml              # 需求清单
│   ├── 02-design/                  # 设计文档
│   ├── 03-test/                   # 测试文档
│   └── 04-progress/                # 进度文档
│       └── daily_*.md             # 每日进度
│
├── src/                             # 源代码
├── config/                          # 配置
│   ├── repos.yaml                  # 关联仓库
│   ├── agents.yaml                 # 项目Agent
│   └── env.yaml                    # 环境配置
│
├── data/                           # 数据文件
├── tests/                          # 测试代码
│
├── .gitignore
├── README.md                        # 项目说明
├── PROJECT.md                      # 项目概览(PM-Agent用)
└── TASKS.md                       # 当前任务(Agent用)
```

### 1.1.3 项目概览文件 (PROJECT.md)

```markdown
# 项目名称

## 基本信息
- 项目编号: PJ-001
- 客户:
- 优先级:
- 截止日期:
- 项目经理:

## 团队
| 角色 | 人员 | Agent ID |
|------|------|-----------|
| 后端 | 郭汉盟 | agent2-001 |
| 前端 | 陈伟 | agent4-001 |
| AI | 李杨峰 | agent3-001 |

## 仓库
| 仓库 | 用途 |
|------|------|
| qushen-data/xxx | 后端 |
| qushen-data/xxx | 前端 |

## 需求清单
| ID | 需求 | 状态 | 进度 |
|----|------|------|------|
| REQ-001 | xxx | 进行中 | 60% |

## 进度
- 本周: 完成xxx
- 下周: 计划xxx
```

### 1.1.4 当前任务文件 (TASKS.md)

```markdown
# 当前任务

## 进行中
| ID | 任务 | Agent | 状态 |
|----|------|--------|------|
| TODO-2-001 | xxx | agent2-001 | 进行中 |

## 待处理
| ID | 任务 | Agent |
|----|------|--------|
| TODO-2-002 | xxx | - |

## 已完成
| ID | 任务 | Agent |
|----|------|--------|
```

## 结论

### 目录结构
```
projects/
├── _templates/project_template/  # 项目模板
├── _shared/                    # 共享资源
├── registry.yaml                # 项目注册表
├── agents.yaml                 # Agent注册表
└── 项目名/                     # 各个项目
    ├── docs/
    ├── src/
    ├── config/
    ├── PROJECT.md             # 项目概览
    └── TASKS.md              # 当前任务
```

### 核心文件
- PROJECT.md - 项目概览，供PM-Agent读取
- TASKS.md - 当前任务，供Agent读取
- registry.yaml - 项目注册表
- agents.yaml - Agent注册表

---

**结论**: 目录结构设计完成，采用标准项目模板结构。
