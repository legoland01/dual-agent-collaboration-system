# 多项目基础设施准备

**日期**: 2026-02-17  
**角色**: Consultant (架构规划)

---

## 一、任务目标

为15个跨客户项目准备好：
1. 项目目录结构
2. Gitee仓库
3. 需求文档模板
4. PM-Agent管理维度

---

## 二、15个项目清单

| # | 客户 | 项目名 | 备注 |
|---|------|--------|------|
| 1 | 金融法院 | court_financial | 卷宗系统更新 |
| 2 | 金融法院 | court_financial_rental | 融资租赁纠纷分析 |
| 3 | 金融法院 | court_risk_assessment | 诉讼风险评估 |
| 4 | 金融法院 | court_representative | 代表人诉讼 |
| 5 | 上海市检察院 | proc_org智能化 | 组织架构+徽章 |
| 6 | 上海市检察院 | proc_ops_log | 运维日志分析 |
| 7 | 上海市检察院 | proc_video | 视频项目进度 |
| 8 | 上海市检察院 | proc_gpu | GPU服务器 |
| 9 | 上海市检察院第三分院 | proc3_case_analysis | 自侦案件分析 |
| 10 | 上海市检察院第三分院 | proc3_crime_software | 职务犯罪软件 |
| 11 | 掌上公服 | mobile_legal | 法律咨询+风险评估 |
| 12 | 上海市生态环境局 | env_impact_assessment | 环评智能审核 |
| 13 | 上海市环境科学研究院 | env_data_extract | 报告数据提取 |
| 14 | 徐汇区司法局 | xuhui_sunshine | 阳光执法 |
| 15 | 徐汇区司法局 | xuhui_admin_doc | 行政复议文件 |

---

## 三、目录结构设计

### 3.1 项目根目录

```
projects/
├── court/                      # 法院系统项目组
│   ├── court_financial/       # 项目1: 卷宗系统
│   ├── court_financial_rental/ # 项目2: 融资租赁
│   ├── court_risk_assessment/ # 项目3: 诉讼风险
│   └── court_representative/   # 项目4: 代表人诉讼
│
├── proc/                       # 检察院项目组
│   ├── proc_org智能化/        # 项目5
│   ├── proc_ops_log/          # 项目6
│   ├── proc_video/            # 项目7
│   └── proc_gpu/              # 项目8
│
├── proc3/                      # 检察院三分院
│   ├── proc3_case_analysis/   # 项目9
│   └── proc3_crime_software/ # 项目10
│
├── mobile/                     # 掌上公服
│   └── mobile_legal/          # 项目11
│
├── env/                        # 生态环境
│   ├── env_impact_assessment/ # 项目12
│   └── env_data_extract/      # 项目13
│
└── xuhui/                     # 徐汇司法局
    ├── xuhui_sunshine/       # 项目14
    └── xuhui_admin_doc/      # 项目15
```

### 3.2 单项目标准目录结构

每个项目包含：
```
项目名/
├── docs/
│   ├── 01-requirements/    # 需求文档
│   ├── 02-design/          # 设计文档
│   ├── 03-test/            # 测试文档
│   └── 04-progress/        # 进度文档
│
├── src/                     # 源代码
├── config/                  # 配置文件
├── data/                    # 数据文件
├── tests/                   # 测试代码
├── README.md                # 项目说明
├── PROJECT.md              # 项目概览
└── .gitignore
```

### 3.3 聚合目录

```
projects/
├── all_projects.yaml        # 所有项目汇总
├── progress.yaml           # 全局进度
└── README.md               # 项目索引
```

---

## 四、Gitee仓库设计

### 4.1 仓库命名规范

```
court-financial-v2        # 金融法院-卷宗系统v2
proc-video-management     # 检察院-视频项目
env-impact-assessment    # 生态环境局-环评
```

### 4.2 仓库分组

| 组名 | 项目 |
|------|------|
| court | 4个项目 |
| proc | 4个项目 |
| proc3 | 2个项目 |
| mobile | 1个项目 |
| env | 2个项目 |
| xuhui | 2个项目 |

---

## 五、需求文档模板

### 5.1 项目概览 (PROJECT.md)

```markdown
# 项目名称

## 基本信息
- 客户:
- 优先级:
- 截止日期:
- 项目经理:

## 需求清单
| # | 需求 | 状态 | 负责人 |
|---|------|------|--------|

## 进度跟踪
| 周次 | 日期 | 内容 | 状态 |
|------|------|------|------|
```

### 5.2 需求详情 (01-requirements/)

```
requirements/
├── REQ_001_需求名称.md
├── REQ_002_需求名称.md
└── README.md
```

---

## 六、PM-Agent管理维度

PM-Agent需要管理这些维度：

| 维度 | 数据来源 | 说明 |
|------|----------|------|
| 客户 | projects/*/PROJECT.md | 每个客户独立 |
| 项目 | projects/*/PROJECT.md | 15个项目 |
| 需求 | docs/01-requirements/ | 每个需求文档 |
| 进度 | docs/04-progress/ | 周进度更新 |
| 截止 | PROJECT.md | 截止日期 |
| 状态 | PROJECT.md | 进行中/已完成 |

---

## 七、实施计划

### 7.1 第一步：创建项目目录结构

```
projects/
├── court/
│   ├── court_financial/
│   │   └── (标准目录)
│   └── ...
├── proc/
├── proc3/
├── mobile/
├── env/
└── xuhui/
```

### 7.2 第二步：初始化Gitee仓库

- 创建6个仓库组
- 初始化15个项目仓库

### 7.3 第三步：生成PROJECT.md模板

- 为每个项目生成概览文档

### 7.4 第四步：PM-Agent集成

- PM-Agent读取projects/目录
- 自动聚合进度

---

## 八、下一步

1. 确认15个项目名称
2. 确认项目分组
3. 确认优先级（你决定）
4. 开始创建目录结构

---

**作者**: Consultant  
**日期**: 2026-02-17
