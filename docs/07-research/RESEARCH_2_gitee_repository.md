# 1.2 Gitee仓库规划

## 目标
规划所有项目的Gitee仓库，建立仓库与项目、人员的映射关系。

## 分析

### 现有仓库 (qushen-data企业)

| 仓库 | 语言 | 用途 | 状态 |
|------|------|------|------|
| dossierai | Python | 卷宗系统 | 活跃 |
| financialcasegeneratorsystem | Python | 测试数据 | 活跃 |
| financial-court-file-assistant | Java | 卷宗后端 | 活跃 |
| financial-court-file-assistant-frontend | Vue/JS | 卷宗前端 | 活跃 |
| xhtools | Python | AI工具 | 活跃 |
| wocheng-ai-service | Python | AI服务 | 活跃 |
| xuhui_law_enforcement | Vue/JS | 阳光执法 | 活跃 |
| lhjczs_java_backend | Java | 旧后端 | 旧版 |
| xuhui_lhjc_data | - | 空 | 待清理 |
| mindsageqa | - | 空 | 待清理 |
| hbtools | - | 空 | 待清理 |

### 15个需求与仓库映射

| 需求 | 需要仓库 | 现有/新建 |
|------|----------|-----------|
| 卷宗系统更新 | dossierai + financial-court-file-assistant + frontend | 现有 |
| 融资租赁分析 | dossierai | 现有 |
| 诉讼风险评估 | xhtools/wocheng-ai | 现有 |
| 阳光执法 | xuhui_law_enforcement | 现有 |
| 组织智能化 | proc_org_xxx | 新建 |
| 运维log分析 | proc_ops_xxx | 新建 |
| 视频项目管理 | proc_video_xxx | 新建 |
| 案件智能分析 | proc3_case_xxx | 新建 |
| 职务犯罪软件 | proc3_crime_xxx 或 lhjczs_java_backend | 迁移 |
| 环评审核 | env_impact_xxx | 新建 |
| 报告数据提取 | env_data_xxx | 新建 |
| 行政复议doc | xuhui_admin_xxx | 新建 |
| 代表人诉讼 | 可能复用dossierai | 待定 |

## 设计

### 1.2.1 仓库命名规范

```
{客户缩写}-{项目缩写}-{类型}

示例:
court-financial-dossier     # 金融法院-卷宗系统-后端
court-financial-frontend   # 金融法院-卷宗系统-前端
proc-org-service          # 检察院-组织智能化-服务
proc-video-management     # 检察院-视频-管理
```

### 1.2.2 仓库分组

```
qushen-data企业
│
├── court-                # 法院系统
│   ├── court-financial-dossier
│   ├── court-financial-backend
│   ├── court-financial-frontend
│   └── court-risk-assessment
│
├── proc-                # 检察院
│   ├── proc-org-service
│   ├── proc-ops-log
│   ├── proc-video-management
│   └── proc-gpu-server
│
├── proc3-               # 检察院三分院
│   ├── proc3-case-analysis
│   └── proc3-crime-software
│
├── mobile-              # 掌上公服
│   └── mobile-legal
│
├── env-                 # 生态环境
│   ├── env-impact-assessment
│   └── env-data-extract
│
└── xuhui-              # 徐汇司法
    ├── xuhui-sunshine
    └── xuhui-admin-doc
```

### 1.2.3 仓库与Agent绑定

每个仓库关联Agent：

```yaml
# config/repos.yaml
repositories:
  - name: court-financial-dossier
    path: qushen-data/court-financial-dossier
    language: Python
    agents:
      - agent3-001  # 李杨峰
    project: 金融法院卷宗

  - name: court-financial-backend
    path: qushen-data/court-financial-backend
    language: Java
    agents:
      - agent2-001  # 郭汉盟
    project: 金融法院卷宗

  - name: court-financial-frontend
    path: qushen-data/court-financial-frontend
    language: Vue/JS
    agents:
      - agent4-001  # 陈伟
    project: 金融法院卷宗
```

## 实施

### 需要创建的仓库

| 仓库名 | 用途 | 语言 | 优先级 |
|--------|------|------|--------|
| qushen-data/court-risk-assessment | 诉讼风险评估 | Python | P0 |
| qushen-data/proc-org-service | 组织智能化 | ? | P1 |
| qushen-data/proc-ops-log | 运维log | ? | P1 |
| qushen-data/proc-video-management | 视频管理 | ? | P1 |
| qushen-data/proc3-case-analysis | 案件分析 | ? | P1 |
| qushen-data/env-impact-assessment | 环评审核 | ? | P1 |
| qushen-data/env-data-extract | 数据提取 | Python | P1 |
| qushen-data/xuhui-admin-doc | 行政复议 | ? | P1 |

### 需要迁移的仓库

| 从 | 到 | 说明 |
|----|----|------|
| lhjczs_java_backend | proc3-crime-software | 重命名/迁移 |

### 需要清理的仓库

| 仓库 | 处理 |
|------|------|
| xuhui_lhjc_data | 删除或用作数据配置 |
| mindsageqa | 删除 |
| hbtools | 填充功能或删除 |

## 结论

### 仓库规划

- 现有活跃仓库: 7个
- 需要新建: 8个
- 需要迁移: 1个
- 需要清理: 3个

### 仓库与人员映射

| 人员 | 仓库 | 状态 |
|------|------|------|
| 李杨峰 | dossierai, xhtools, wocheng-ai | 现有 |
| 郭汉盟 | financial-court-file-assistant | 现有 |
| 陈伟 | financial-court-file-assistant-frontend, xuhui_law_enforcement | 现有 |

### 下一步

1. 创建需要的仓库
2. 迁移旧仓库
3. 清理空仓库
4. 建立仓库配置

---

**结论**: Gitee仓库规划完成，共需新建8个仓库。
