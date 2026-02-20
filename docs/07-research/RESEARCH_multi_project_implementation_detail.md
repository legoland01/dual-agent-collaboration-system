# 多项目管理体系 - 详细实施计划

**日期**: 2026-02-18  
**计划类型**: 执行前细化  
**版本**: v1.1

---

## 一、Week 1 详细任务分解

### 1.1 目录结构创建

```
projects/
├── _templates/                    # 项目模板
│   ├── PROJECT.md                # 项目概述模板
│   ├── project.yaml               # 项目配置模板
│   ├── agents.yaml                # Agent分配模板
│   ├── repos.yaml                 # 仓库配置模板
│   └── TASKS.md                   # 任务看板模板
│
├── _shared/                       # 共享资源
│   ├── clients.yaml               # 客户信息
│   └── developers.yaml            # 开发人员信息
│
├── registry.yaml                  # 项目注册表 (全局)
├── agents_global.yaml             # 全局Agent注册表
└── {客户名}/                     # 按客户分类
    └── {项目名}/
        ├── PROJECT.md
        ├── project.yaml
        ├── agents.yaml
        ├── repos.yaml
        └── docs/
```

### 1.2 8个新仓库规划

| 仓库名 | 用途 | 技术栈 | 归属 |
|--------|------|--------|------|
| financial-case-manager | 案件管理系统 | Java | 金融法院 |
| court-document-ai | 文书智能生成 | Python | 金融法院 |
| enforcement-tracker | 执行线索追踪 | Vue/JS | 上海市检察院 |
| case-evidence-cloud | 案证云存储 | Java | 上海市检察院第三分院 |
| public-service-mobile | 掌上公服小程序 | Vue/JS | 掌上公服 |
| env-monitoring-dashboard | 环境监测看板 | Vue/JS | 上海市生态环境局 |
| env-research-platform | 环境研究平台 | Python | 上海市环境科学研究院 |
| legal-aid-system | 法律援助系统 | Java | 徐汇区司法局 |

### 1.3 数据同步方案

| 数据类型 | 来源 | 同步方式 | 优先级 |
|----------|------|----------|--------|
| 项目信息 | CODING | 手动导入到 registry.yaml | P0 |
| 仓库信息 | Gitee API | oc-collab project sync | P0 |
| 需求文档 | 各项目 | Git clone + 复制 | P1 |
| 代码 | Gitee | Git clone | P1 |

### 1.4 Gitee API 使用

```bash
# 获取仓库列表
curl -H "Authorization: token 3b424cb90b1490149e4b0ad1827e8a74" \
  https://gitee.com/api/v5/user/repos?access_token=3b424cb90b1490149e4b0ad1827e8a74

# 创建仓库
curl -X POST https://gitee.com/api/v5/user/repos \
  -d "access_token=xxx" \
  -d "name=仓库名" \
  -d "private=true"
```

---

## 二、v2.3.3 自动流程触发 - 实施计划

### 2.1 场景分析结论

| 场景类型 | 数量 | 处理方式 |
|----------|------|----------|
| 可自动继续 | 14 | 直接执行 |
| 需用户确认 | 18 | 等待输入 |
| 需人工介入 | 5 | 标记并通知 |

### 2.2 优先实现功能

| 功能 | 说明 | 工时 | 优先级 |
|------|------|------|--------|
| FlowEngine | 流程引擎基础 | 6h | P0 |
| ScenarioMatcher | 场景匹配器 | 4h | P0 |
| AutoContinueHandler | 自动继续处理器 | 3h | P0 |
| ConfirmPromptHandler | 确认提示处理器 | 3h | P1 |
| WarningHandler | 警告处理器 | 3h | P1 |

### 2.3 配置文件设计

```yaml
# flow_automation.yaml
scenarios:
  - name: "agent1_create_todo"
    auto_proceed: true
    
  - name: "agent2_fix_bug"
    auto_proceed: true
    
  - name: "agent1_create_memo"
    confirm_required: true
    options: ["yes", "no", "skip"]
    
  - name: "git_conflict"
    warning_only: true
    require_human: true
```

---

## 三、v2.3.5 PM-Agent 核心功能设计

### 3.1 Agent Pool 管理

```bash
# 命令设计
oc-collab agent pool list              # 查看空闲Agent
oc-collab agent pool add --agent ID   # 添加到池
oc-collab agent pool remove --agent ID # 从池移除

# 数据结构
pool:
  available: [agent3-001, agent3-002, ...]  # 空闲
  assigned: {projectA: [agent3-001], ...}    # 已分配
  offline: [agent3-005, ...]                 # 离线
```

### 3.2 Agent 自动分配算法

```python
def assign_agents(project, developer_count):
    needed = developer_count
    available = get_available_agents()
    
    # 按技能匹配
    for dev in project.developers:
        required_skills = dev.required_skills
        matched = find_matched_agents(available, required_skills)
        
        if matched >= dev.agent_count:
            assign(matched[:dev.agent_count], dev)
        else:
            # 不足时部分分配
            assign(matched, dev)
            log_warning(f"{dev.name} 缺少 {dev.agent_count - len(matched)} 个Agent")
```

### 3.3 Project Create 流程

```
用户输入: 项目名称、客户、成员列表
    ↓
PM-Agent 验证输入
    ↓
创建 projects/{客户}/{项目}/ 目录
    ↓
生成 project.yaml, agents.yaml, repos.yaml
    ↓
初始化 Git 仓库（如需要）
    ↓
返回项目信息
```

---

## 四、验收标准

### Week 1 验收

- [ ] projects/ 目录结构完整
- [ ] 模板文件可用
- [ ] 8个新仓库创建命令就绪
- [ ] registry.yaml 可编辑
- [ ] agents_global.yaml 格式正确

### v2.3.3 验收

- [ ] FlowEngine 可运行
- [ ] 14个自动场景可触发
- [ ] 确认提示可显示选项
- [ ] 警告可记录日志

### v2.3.5 验收

- [ ] agent pool 命令可用
- [ ] agent assign 自动分配
- [ ] project create 可创建项目
- [ ] gitee sync 可同步

---

**下一步**: 等待用户确认后展开执行
