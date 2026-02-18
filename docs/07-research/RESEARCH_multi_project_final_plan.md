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

## 三、实施计划 (4周)

### 第一周: 基础设施 + 数据同步 (Day 1-7)

#### 1.1 创建目录结构

- [ ] 创建 projects/ 目录结构
- [ ] 创建项目模板文件

#### 1.2 Gitee仓库

- [ ] 创建 8个新仓库
- [ ] 迁移 lhjczs_java_backend
- [ ] 清理空仓库

#### 1.3 数据同步 (关键!)

| 数据 | 来源 | 同步方式 |
|------|------|----------|
| 项目信息 | CODING | 手动导入到 projects/registry.yaml |
| 仓库信息 | Gitee API | 自动同步 |
| 需求文档 | 现有项目 | 复制到 projects/项目名/docs/ |
| 代码 | 各仓库 | Git clone到对应目录 |

```bash
# 数据同步命令
pm-agent sync repos           # 同步Gitee仓库
pm-agent sync projects        # 同步CODING项目
pm-agent import requirements   # 导入需求
```
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

## 七、oc-collab能力分析与Roadmap调整

### 7.1 当前oc-collab已支持

| 功能 | 命令 | 状态 |
|------|------|------|
| Agent管理 | agent register/list/status | ✅ 已有 |
| 项目管理 | project list/update | ✅ 已有 |
| 需求管理 | requirements | ✅ 已有 |
| Git同步 | git push/pull | ✅ 已有 |
| 部署 | deploy | ✅ 已有 |
| 通知 | notify | ✅ 已有 |
| TODO管理 | todo create/show/ack | ✅ 已有 |

### 7.2 oc-collab需要新增的功能

| 功能 | 说明 | 优先级 |
|------|------|--------|
| **agent pool** | Agent资源池管理 | P0 |
| **agent assign** | Agent自动分配到项目 | P0 |
| **project create** | 创建新项目 | P0 |
| **project sync** | 同步Gitee仓库 | P1 |
| **project import** | 导入现有需求 | P1 |
| **gitee stats** | 代码提交统计 | P2 |

### 7.3 Roadmap调整

**新增版本 v2.3.5**:

| 版本 | 目标 | 说明 |
|------|------|------|
| v2.3.2 | TODO存储+通知 | POC完成 |
| v2.3.3 | 自动流程触发 | 待开发 |
| v2.3.4 | 配置管理 | 设计完成 |
| **v2.3.5** | **多项目管理体系** | **Agent pool + project管理** |

### 7.4 v2.3.5需要开发的功能

```python
# 新增CLI命令
oc-collab agent pool          # Agent资源池管理
oc-collab agent assign       # 分配Agent到项目
oc-collab project create    # 创建项目
oc-collab project sync     # 同步Gitee仓库
oc-collab gitee            # Gitee集成
```

---

## 八、成功标准

- [ ] 目录结构创建完成
- [ ] 8个新仓库创建完成
- [ ] 18个Agent注册完成 (李10+郭5+陈3)
- [ ] 第一个项目创建成功
- [ ] Agent能读取TASKS.md执行任务
- [ ] 每日报告能生成
- [ ] **v2.3.5 CLI命令开发完成**

---

**结论**: 本方案可在4周内建立完整的多项目管理体系，实现PM-Agent管理项目、oc-collab协调Agent的目标。

**下一步**: 确认后开始执行第一周任务。
