# PROPOSAL-2026-02-008: 问题追踪系统增强与规范整合

**提案编号**: PROPOSAL-2026-02-008  
**提案人**: Agent 1  
**日期**: 2026-02-14  
**目标版本**: v2.2.11  
**优先级**: P1  
**状态**: READY

---

## 1. 背景与问题

### 1.1 当前状态

**问题追踪系统现状**：

| 组件 | 状态 | 说明 |
|------|------|------|
| `oc_collab_issue_tracker` Skill | ✅ 存在 | v1.0，定义完整 |
| `issue_tracker.py` 代码 | ❌ 不存在 | 只有Skill定义，无实现 |
| `state/ISSUE_INDEX.md` | ❌ 不存在 | Skill定义的输出文件 |
| `docs/issues/` 归档目录 | ❌ 不存在 | 已关闭问题的归档位置 |
| BUG记录方式 | ⚠️ 手动 | 使用 `docs/00-memos/` 临时目录 |

### 1.2 问题描述

```
问题1：Skill与代码脱节
├── oc_collab_issue_tracker Skill定义完整
└── 无对应的Python实现代码

问题2：文档结构混乱
├── BUG记录在 docs/00-memos/
├── 缺少统一索引 state/ISSUE_INDEX.md
└── 没有规范化的归档流程

问题3：流程不完整
├── 发现问题 → 记录memos（手动）
├── 修复 → 关闭memos（手动）
└── 无自动化跟踪和状态管理
```

### 1.3 当前BUG记录统计

| 类型 | 数量 | 位置 |
|------|------|------|
| 2026-02-10 BUGs | 5个 | `BUG-20260210-001` ~ `BUG-20260210-005` |
| 2026-02-13 BUGs | 7个 | `BUG-20260213-001` ~ `BUG-20260213-007` |
| 2026-02-14 BUGs | 9个 | `BUG-20260214-001` ~ `BUG-20260214-009` |
| **总计** | **21个** | 大部分在 `docs/00-memos/` |

---

## 2. 解决方案

### 2.1 核心思路

**整合现有资源 + 补充缺失环节**：

```
现有资源                    缺失环节
    │                          │
    ▼                          ▼
┌─────────────────┐    ┌─────────────────────┐
│ Skill定义        │    │ Python实现代码       │
│ oc_collab_issue │    │ issue_tracker.py     │
│ _tracker        │    └─────────────────────┘
└─────────────────┘           │
                               ▼
                        ┌─────────────────────┐
                        │ 规范化文档结构       │
                        │ state/ISSUE_INDEX.md │
                        │ docs/issues/         │
                        └─────────────────────┘
                               │
                               ▼
                        ┌─────────────────────┐
                        │ 完整的问题追踪闭环   │
                        └─────────────────────┘
```

### 2.2 实现方案

#### 2.2.1 Python代码实现 (`issue_tracker.py`)

**位置**: `src/core/issue_tracker.py`

**功能模块**：

| 模块 | 功能 | 工时 |
|------|------|------|
| `IssueTracker` | 主类，问题跟踪 | 2h |
| `IssueStateMachine` | 状态机管理 | 1h |
| `IssueIndexManager` | 索引文件管理 | 1h |
| `CLI Commands` | `oc-collab issue` 命令组 | 2h |

**状态流转**：

```
OPEN → IN_PROGRESS → RESOLVED → VERIFIED → CLOSED
   │         │              │           │
   │         │              │           └── 验收通过
   │         │              └────────────── 修复完成
   │         └────────────────────────────── 正在修复
   └──────────────────────────────────────── 发现问题
```

#### 2.2.2 文档结构规范

**索引文件**: `state/ISSUE_INDEX.md`

```markdown
# 问题索引

## 统计

| 类型 | 数量 |
|------|------|
| 总问题数 | 21 |
| 已关闭 | 15 |
| 待处理 | 6 |

## 按严重度

| 严重度 | 数量 | 列表 |
|--------|------|------|
| P0 | 3 | BUG-001, BUG-003, BUG-008 |
| P1 | 12 | ... |
| P2 | 6 | ... |

## 按版本

| 版本 | 数量 | 状态 |
|------|------|------|
| v2.2.10 | 9 | 已全部关闭 |
| v2.2.11 | 3 | 待处理 |

## 按状态

| 状态 | 数量 |
|------|------|
| OPEN | 2 |
| IN_PROGRESS | 1 |
| RESOLVED | 1 |
| VERIFIED | 2 |
| CLOSED | 15 |
```

**归档目录**: `docs/issues/{bug_id}/`

```
docs/issues/
├── BUG-20260214-001/
│   ├── issue.yaml        # 问题定义
│   ├── analysis.md       # 分析报告
│   └── fix_report.md     # 修复报告
├── BUG-20260214-002/
└── ...
```

#### 2.2.3 CLI命令设计

```bash
# 问题列表
oc-collab issue list              # 所有问题
oc-collab issue list --status OPEN # 按状态筛选
oc-collab issue list --severity P0 # 按严重度筛选

# 问题详情
oc-collab issue show BUG-001      # 显示问题详情

# 状态更新
oc-collab issue start BUG-001     # 开始处理
oc-collab issue resolve BUG-001   # 标记已修复
oc-collab issue verify BUG-001     # 验收通过
oc-collab issue close BUG-001     # 关闭问题

# 问题创建
oc-collab issue create --title "问题标题" --severity P1 --description "描述"
```

---

## 3. 现有BUG迁移

### 3.1 迁移范围

将 `docs/00-memos/` 中的BUG迁移到 `docs/issues/`

| BUG组 | 数量 | 目标状态 |
|-------|------|----------|
| BUG-20260210-xxx | 5 | 全部关闭 |
| BUG-20260213-xxx | 7 | 全部关闭 |
| BUG-20260214-xxx | 9 | 6关闭，3待处理 |

### 3.2 迁移脚本

```python
# migrate_issues.py

def migrate_bug_report(bug_file: str) -> dict:
    """将BUG报告迁移到标准化格式"""
    # 1. 解析现有BUG报告
    # 2. 提取关键信息
    # 3. 生成标准issue.yaml
    # 4. 移动到docs/issues/
```

---

## 4. 实施计划

### 4.1 阶段划分

| 阶段 | 内容 | 产出 |
|------|------|------|
| **Phase 1** | 实现 `issue_tracker.py` | `src/core/issue_tracker.py` |
| **Phase 2** | 实现CLI命令 | `src/cli/issue_commands.py` |
| **Phase 3** | 迁移现有BUG | `docs/issues/` |
| **Phase 4** | 创建索引 | `state/ISSUE_INDEX.md` |
| **Phase 5** | 测试验收 | 测试报告 |

### 4.2 详细任务

| 任务ID | 任务描述 | 负责人 | 工时 |
|--------|----------|--------|------|
| TASK-001 | IssueTracker主类实现 | Agent2 | 2h |
| TASK-002 | IssueStateMachine实现 | Agent2 | 1h |
| TASK-003 | IssueIndexManager实现 | Agent2 | 1h |
| TASK-004 | issue list命令 | Agent2 | 1h |
| TASK-005 | issue show命令 | Agent2 | 0.5h |
| TASK-006 | issue状态更新命令 | Agent2 | 1.5h |
| TASK-007 | issue create命令 | Agent2 | 1h |
| TASK-008 | BUG迁移脚本 | Agent1 | 2h |
| TASK-009 | 执行BUG迁移 | Agent1 | 1h |
| TASK-010 | 创建ISSUE_INDEX | Agent1 | 0.5h |
| TASK-011 | 测试验收 | Agent1 | 1h |

### 4.3 工时估算

| 类型 | 工时 |
|------|------|
| 代码开发 | 8h |
| 文档迁移 | 4.5h |
| 测试验收 | 1h |
| **总计** | **13.5h** |

---

## 5. 与其他版本的关系

| 版本 | 关系 |
|------|------|
| v2.2.10 | 迁移9个已关闭BUG |
| v2.2.11 | 新BUG使用新系统 |
| v2.2.12 | 增强功能（自动检测、通知） |

---

## 6. 风险与应对

| 风险 | 可能性 | 影响 | 应对 |
|------|--------|------|------|
| 迁移丢失数据 | 低 | 高 | 备份后迁移 |
| CLI命令冲突 | 低 | 中 | 检查现有命令 |
| 用户习惯改变 | 中 | 中 | 提供迁移培训 |

---

## 7. 验收标准

- [ ] `issue_tracker.py` 实现完成
- [ ] CLI命令 `oc-collab issue` 可用
- [ ] 21个历史BUG迁移完成
- [ ] `state/ISSUE_INDEX.md` 生成
- [ ] 新BUG使用新系统记录

---

## 8. 关联文档

| 文档 | 说明 |
|------|------|
| `skills/oc_collab_issue_tracker/` | Skill定义 |
| `docs/00-memos/` | 当前BUG记录位置 |
| `docs/04-proposals/PROPOSAL-2026-02-006` | Agent独立TODO编号 |
| `docs/04-proposals/PROPOSAL-2026-02-007` | Skill强制执行 |

---

## 9. 签署记录

| 角色 | 签署人 | 日期 | 状态 |
|------|--------|------|------|
| Agent 1 | | 2026-02-14 | ✅ |
| Agent 2 | | | ☐ |

---

**提案人**: Agent 1  
**日期**: 2026-02-14  
**状态**: READY
