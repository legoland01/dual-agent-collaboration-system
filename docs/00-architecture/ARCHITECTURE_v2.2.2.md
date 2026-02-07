# oc-collab 系统架构分析文档

**版本**: v1
**创建日期**: 2026-02-07
**作者**: Agent 1 (产品经理)
**目的**: 系统功能结构梳理与规划

---

## 1. 系统概述

### 1.1 产品定位

**oc-collab** (opencode-collaboration) 是一个**双Agent协作框架**，实现产品经理(Agent1)与开发负责人(Agent2)的分离式协作工具。

### 1.2 核心价值

| 价值 | 说明 |
|------|------|
| 职责分离 | Agent1 专注需求，Agent2 专注实现 |
| 流程规范 | 4阶段工作流 + 签署机制 |
| 可观测性 | 所有操作有记录、可追溯 |

---

## 2. 系统分层架构

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Layer                            │
│                  (src/cli/main.py)                      │
│           oc-collab init/status/todo/review...          │
├─────────────────────────────────────────────────────────┤
│                   Core Layer                            │
│                   (src/core/)                           │
│  ┌─────────────┬─────────────┬─────────────┐          │
│  │   Workflow   │   Agent &   │  Signoff &  │          │
│  │ Management   │ Collaboration│   Review   │          │
│  ├─────────────┼─────────────┼─────────────┤          │
│  │   Workflow   │  Brain      │  Signoff    │          │
│  │   Engine     │  Engine     │  Engine     │          │
│  │   State      │  Agent      │  Checklist  │          │
│  │   Manager    │  Manager    │  Generator  │          │
│  │   Phase      │  Session    │  Extended   │          │
│  │   Advance    │  Manager    │  Checklist  │          │
│  └─────────────┴─────────────┴─────────────┤          │
│  ┌─────────────┬─────────────┬─────────────┤          │
│  │   Automation │   Git &     │  Validation │          │
│  │   Engine     │   Version   │  & Compliance│         │
│  ├─────────────┼─────────────┼─────────────┤          │
│  │   Auto       │  Git        │  Change     │          │
│  │   Engine     │  Workflow   │  Compliance │          │
│  │   Auto Git   │  Git Monitor│  Signoff    │          │
│  │   Sync       │  Enforcer   │  Record Mgr │          │
│  │   Auto Docs  │  Daemon      │  Cognitive   │          │
│  │              │             │  Immune      │          │
│  └─────────────┴─────────────┴─────────────┘          │
├─────────────────────────────────────────────────────────┤
│                  Utils Layer                            │
│               (src/utils/)                               │
│    yaml │ date │ file │ lock │ environment              │
├─────────────────────────────────────────────────────────┤
│                  Templates Layer                         │
│               (src/templates/)                           │
│              renderer.py                                  │
├─────────────────────────────────────────────────────────┤
│                    Skills Layer                          │
│               (skills/)                                   │
│    oc_collab_collaboration_guide/                       │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 模块分类与功能映射

### 3.1 Workflow & State Management (工作流与状态管理)

| 模块 | 职责 | 依赖 | 状态 |
|------|------|------|------|
| `workflow.py` | 定义阶段转换规则 | StateManager | ✅ 核心 |
| `state_manager.py` | 项目状态读写 | utils/yaml | ✅ 核心 |
| `state_machine.py` | 状态机实现 | 无 | ✅ 存在 |
| `phase_advance.py` | 自动阶段推进 | Workflow, StateManager | ✅ 存在 |
| `state_validator.py` | 状态验证 | StateManager | ⚠️ 待评估 |
| `state_migrator.py` | 状态迁移 | StateManager | ⚠️ 待评估 |
| `iteration_status_manager.py` | 迭代状态管理 | StateManager | ⚠️ 待评估 |

**职责边界分析**:
- `state_manager` 是唯一的状态读写入口
- `phase_advance` 负责阶段推进逻辑
- `workflow` 定义转换规则
- **问题**: `state_validator`, `state_migrator`, `iteration_status_manager` 与 `state_manager` 职责重叠

### 3.2 Agent & Collaboration (Agent 与协作)

| 模块 | 职责 | 依赖 | 状态 |
|------|------|------|------|
| `brain_engine.py` | Agent 规则引擎 | StateManager | ✅ 核心 |
| `agent_manager.py` | Agent 生命周期管理 | 无 | ⚠️ 待评估 |
| `session_manager.py` | Session 管理 | StateManager | ✅ 存在 |
| `supervisor.py` | 监督器 | BrainEngine | ⚠️ 待评估 |
| `detector.py` | 项目类型检测 | 无 | ✅ CLI 依赖 |
| `task_executor.py` | 任务执行器 | BrainEngine | ✅ 存在 |
| `resource_lock.py` | 资源锁 | StateManager | ⚠️ 待评估 |
| `meeting_manager.py` | 会议记录 | 无 | ⚠️ 待评估 |
| `story_manager.py` | 故事管理 | 无 | ⚠️ 待评估 |
| `project_manager.py` | 项目管理 | StateManager | ⚠️ 待评估 |
| `config_reloader.py` | 配置重载 | 无 | ⚠️ 待评估 |

**职责边界分析**:
- `brain_engine` 是 Agent 决策核心
- `session_manager` 负责 Session 生命周期
- **问题**: 大量模块(`agent_manager`, `project_manager`, `meeting_manager`, `story_manager`)与核心职责边界不清

### 3.3 Signoff & Review (签署与评审)

| 模块 | 职责 | 版本 | 状态 |
|------|------|------|------|
| `signoff.py` | 签署引擎 | v2.2.0 | ✅ 核心 |
| `signoff_record_manager.py` | 签署记录管理 | v2.2.1 | ✅ M3 |
| `checklist_generator.py` | 基础 Checklist 生成 | v2.2.0 | ✅ 存在 |
| `extended_checklist.py` | 动态 Checklist | v2.2.1 | ✅ M4 |
| `design_review_notifier.py` | 设计评审通知 | v2.2.0 | ⚠️ 待评估 |

**职责边界分析**:
- `signoff` 负责签署逻辑
- `checklist_generator` + `extended_checklist` 负责评审辅助
- `design_review_notifier` 负责通知
- **问题**: `design_review_notifier` 可能被 `extended_checklist` 包含

### 3.4 Automation (自动化引擎)

| 模块 | 职责 | 版本 | 状态 |
|------|------|------|------|
| `auto_engine.py` | 自动化引擎核心 | v2.2.0 | ✅ 核心 |
| `auto_git_sync.py` | Git 自动同步 | v2.2.1 | ✅ M1 |
| `auto_doc_git.py` | 文档 Git 同步 | v2.2.0 | ✅ 存在 |
| `auto_docs.py` | 自动化文档 | v2.2.0 | ✅ 存在 |
| `auto_retry.py` | 自动重试 | v2.2.0 | ✅ 存在 |
| `doc_generator.py` | 文档生成器 | v2.2.0 | ⚠️ 待评估 |

**职责边界分析**:
- `auto_engine` 是自动化入口
- `auto_git_sync`, `auto_doc_git`, `auto_docs` 是具体自动化实现
- **问题**: `doc_generator` 与 `auto_docs` 可能重叠

### 3.5 Git & Version Control (Git 与版本控制)

| 模块 | 职责 | 版本 | 状态 |
|------|------|------|------|
| `git.py` | Git 操作封装 | v2.2.0 | ✅ 核心 |
| `git_workflow_enforcer.py` | Git 工作流强制 | v2.2.0 | ✅ 存在 |
| `git_monitor.py` | Git 监控 | v2.2.0 | ⚠️ 待评估 |

**职责边界分析**:
- `git.py` 是唯一 Git 操作入口
- `git_workflow_enforcer` 强制 Git 规范
- `git_monitor` 可能与 `auto_git_sync` 重叠

### 3.6 Validation & Compliance (验证与合规)

| 模块 | 职责 | 版本 | 状态 |
|------|------|------|------|
| `change_compliance.py` | 变更合规检查 | v2.2.1 | ✅ M2 |
| `exception_handler.py` | 异常处理 | v2.2.0 | ✅ 存在 |
| `error_templates.py` | 错误模板 | v2.2.0 | ⚠️ 待评估 |

**职责边界分析**:
- `change_compliance` 负责变更验证
- `exception_handler` 负责异常捕获
- `error_templates` 负责错误信息

### 3.7 Observability (可观测性)

| 模块 | 职责 | 版本 | 状态 |
|------|------|------|------|
| `monitor.py` | 监控器 | v2.2.0 | ⚠️ 待评估 |

**职责边界分析**:
- `monitor.py` 是唯一监控模块
- 职责清晰

### 3.8 Cognitive Immunity (认知免疫)

| 模块 | 职责 | 版本 | 状态 |
|------|------|------|------|
| `cognitive_immune.py` | 认知免疫系统 | v2.2.1 | ✅ M5 |

**职责边界分析**:
- `cognitive_immune` 负责上下文混同检测
- 独立模块，职责清晰

### 3.9 CLI Layer (命令行接口)

| 模块 | 职责 | 状态 |
|------|------|------|
| `cli/main.py` | CLI 入口 | ✅ 核心 |
| `cli/agent.py` | Agent 命令 | ⚠️ 待评估 |

---

## 4. 模块依赖关系图

### 4.1 核心依赖链

```
CLI (main.py)
    │
    ├── StateManager ◄── 所有需要状态的模块依赖
    │       │
    │       ├── WorkflowEngine ◄── 阶段转换
    │       │       │
    │       │       ├── SignoffEngine ◄── 签署
    │       │       │       │
    │       │       │       ├── ChecklistGenerator
    │       │       │       └── ExtendedChecklist
    │       │       │
    │       │       └── PhaseAdvanceEngine ◄── 阶段推进
    │       │
    │       ├── BrainEngine ◄── Agent 规则
    │       │       │
    │       │       └── CognitiveImmuneSystem ◄── 认知免疫
    │       │
    │       ├── SessionManager
    │       │
    │       └── AutoEngine ◄── 自动化
    │               │
    │               ├── AutoGitSync
    │               ├── AutoDocGit
    │               └── AutoDocs
    │
    └── GitHelper ◄── Git 操作
```

### 4.2 模块职责矩阵

| 模块 | 读状态 | 写状态 | Git 操作 | Agent 决策 | 文件操作 |
|------|--------|--------|----------|------------|----------|
| StateManager | ✅ | ✅ | ❌ | ❌ | ❌ |
| WorkflowEngine | ✅ | ❌ | ❌ | ❌ | ❌ |
| SignoffEngine | ✅ | ✅ | ❌ | ❌ | ❌ |
| BrainEngine | ✅ | ❌ | ❌ | ✅ | ❌ |
| AutoEngine | ✅ | ❌ | ✅ | ❌ | ❌ |
| GitHelper | ❌ | ❌ | ✅ | ❌ | ❌ |
| CognitiveImmune | ✅ | ❌ | ❌ | ✅ | ❌ |

---

## 5. 问题识别

### 5.1 功能重叠模块

| 模块 A | 模块 B | 重叠内容 | 建议 |
|--------|--------|----------|------|
| `state_validator.py` | `state_manager.py` | 状态验证 | 合并到 StateManager |
| `state_migrator.py` | `state_manager.py` | 状态迁移 | 合并到 StateManager |
| `doc_generator.py` | `auto_docs.py` | 文档生成 | 合并到 AutoDocs |
| `git_monitor.py` | `auto_git_sync.py` | Git 监控 | 合并或删除 |
| `design_review_notifier.py` | `extended_checklist.py` | 评审通知 | 合并或删除 |
| `iteration_status_manager.py` | `state_manager.py` | 状态管理 | 合并到 StateManager |
| `error_templates.py` | `exception_handler.py` | 错误处理 | 合并到 ExceptionHandler |
| `meeting_manager.py` | `story_manager.py` | 文档管理 | 重构或删除 |

### 5.2 职责边界不清模块

| 模块 | 问题 | 建议 |
|------|------|------|
| `agent_manager.py` | 与 BrainEngine 职责不清 | 明确分工或合并 |
| `project_manager.py` | 职责过于宽泛 | 拆分为具体功能 |
| `supervisor.py` | 与 BrainEngine 重叠 | 合并或删除 |
| `resource_lock.py` | 使用场景不明确 | 明确使用场景 |
| `config_reloader.py` | 与 StateManager 关系不清 | 合并或删除 |

### 5.3 缺失功能（根据 F-PROC-001）

| 功能 | 对应模块 | 建议 |
|------|----------|------|
| 角色边界检查 | 新增 `role_validator.py` | 创建 |
| 文档状态绑定 | 扩展 `workflow.py` | 扩展 |
| 完整性门禁 | 新增 `completeness_guard.py` | 创建 |
| todowrite 持久化 | 扩展 `auto_engine.py` | 修复 |

---

## 6. 架构优化建议

### 6.1 模块整合方案

#### 6.1.1 State Management 整合

```
建议合并到 StateManager:
├── state_validator.py
├── state_migrator.py
├── iteration_status_manager.py
└── config_reloader.py (可选)
```

#### 6.1.2 Automation 整合

```
建议合并到 AutoEngine:
├── auto_git_sync.py (已存在)
├── auto_doc_git.py (已存在)
├── auto_docs.py (已存在)
├── doc_generator.py → 合并
└── git_monitor.py → 合并
```

#### 6.1.3 Error Handling 整合

```
建议合并到 ExceptionHandler:
├── error_templates.py → 合并
└── design_review_notifier.py → 合并(如果涉及异常通知)
```

### 6.2 新增模块设计

#### 6.2.1 RoleValidator (角色验证器)

```python
# oc_collab/core/role_validator.py

class RoleValidator:
    """Agent 角色权限验证器"""
    
    RULES = {
        "agent1": {
            "allow": ["docs/01-requirements/*", "docs/04-memos/*"],
            "deny": ["docs/02-design/*", "src/*", "tests/*"]
        },
        "agent2": {
            "allow": ["docs/02-design/*", "src/*", "tests/*"],
            "deny": ["docs/01-requirements/*"]  # 除了评审
        }
    }
    
    @staticmethod
    def check_permission(agent_id: str, file_path: str) -> bool:
        """检查 Agent 是否有权限操作文件"""
        pass
```

#### 6.2.2 CompletenessGuard (完整性门禁)

```python
# oc_collab/core/completeness_guard.py

class CompletenessGuard:
    """需求/设计文档完整性门禁"""
    
    @staticmethod
    def validate_review_target(doc_path: str, options: dict) -> bool:
        """验证评审目标是否完整"""
        pass
    
    @staticmethod
    def validate_doc_status(doc_path: str, action: str) -> bool:
        """验证文档状态是否允许该操作"""
        pass
```

---

## 7. v2.2.2 功能规划

### 7.1 功能分类

| 类型 | 功能 | 模块 | 优先级 |
|------|------|------|--------|
| **流程规范** | F-PROC-001.1 角色边界检查 | 新增 role_validator.py | P0 |
| **流程规范** | F-PROC-001.2 文档状态绑定 | 扩展 workflow.py | P0 |
| **流程规范** | F-PROC-001.3 完整性门禁 | 新增 completeness_guard.py | P0 |
| **Bug 修复** | F-PROC-001.4 todowrite 持久化 | 扩展 auto_engine.py | P0 |
| **自动化** | F-AUTO-001 部署发布自动化 | 新增 deployment.py | P1 |
| **自动化** | F-AUTO-002 任务状态自动同步 | 扩展 auto_engine.py | P1 |
| **自动化** | F-AUTO-003 测试覆盖率门禁 | 新增 coverage.py | P2 |
| **协作** | F-REVIEW-001 动态评审 Checklist | 扩展 checklist_generator.py | P1 |
| **协作** | F-IDENTITY-001 Agent 身份自动识别 | 扩展 cognitive_immune.py | P2 |
| **工具** | F-AUTO-004 文档版本管理 | 新增 doc_version_manager.py | P2 |

### 7.2 开发顺序建议

| 顺序 | 功能 | 理由 |
|------|------|------|
| 1 | F-PROC-001.4 todowrite 持久化 | 依赖其他功能的基础 |
| 2 | F-PROC-001.1 角色边界检查 | 防止越权操作 |
| 3 | F-PROC-001.2 文档状态绑定 | 防止 DRAFT 被评审 |
| 4 | F-PROC-001.3 完整性门禁 | 防止部分评审 |
| 5 | F-AUTO-002 任务状态自动同步 | 基于 todowrite 修复 |
| 6 | F-REVIEW-001 动态评审 Checklist | 复用现有架构 |
| 7 | F-AUTO-001 部署发布自动化 | 配置驱动，实现简单 |
| 8 | F-AUTO-003 测试覆盖率门禁 | CI/CD 集成 |
| 9 | F-IDENTITY-001 Agent 身份自动识别 | 涉及多模块改造 |
| 10 | F-AUTO-004 文档版本管理 | 工具性质，放在最后 |

---

## 8. 结论

### 8.1 系统现状

- **核心模块** (`workflow.py`, `state_manager.py`, `signoff.py`, `brain_engine.py`): 职责清晰，运作良好
- **扩展模块** (`auto_engine.py`, `cognitive_immune.py`): v2.2.1 新增，职责基本清晰
- **遗留模块** (约 15 个): 存在职责重叠或边界不清问题

### 8.2 改进方向

1. **短期** (v2.2.2): 新增 F-PROC-001 系列功能，解决协作流程问题
2. **中期**: 整合重叠模块，减少维护成本
3. **长期**: 建立模块职责边界文档，防止功能蔓延

### 8.3 下一步行动

1. ✅ 完成系统架构分析（本文档）
2. ⏳ Agent2 评审 F-PROC-001 需求
3. ⏳ Agent2 创建 F-PROC-001 设计文档
4. ⏳ Agent2 实现 F-PROC-001 代码
5. ⏳ 启动模块整合规划（v2.3.0）

---

## 附录

### A. 模块清单

| 序号 | 模块名 | 分类 | 状态 |
|------|--------|------|------|
| 1 | workflow.py | Workflow | ✅ 核心 |
| 2 | state_manager.py | State | ✅ 核心 |
| 3 | phase_advance.py | Workflow | ✅ 存在 |
| 4 | brain_engine.py | Agent | ✅ 核心 |
| 5 | signoff.py | Review | ✅ 核心 |
| 6 | auto_engine.py | Automation | ✅ 核心 |
| 7 | cognitive_immune.py | Immunity | ✅ M5 |
| 8 | extended_checklist.py | Review | ✅ M4 |
| 9 | change_compliance.py | Validation | ✅ M2 |
| 10 | signoff_record_manager.py | Review | ✅ M3 |
| 11 | auto_git_sync.py | Automation | ✅ M1 |
| 12 | session_manager.py | Agent | ✅ 存在 |
| 13 | git.py | Version | ✅ 核心 |
| 14 | detector.py | CLI | ✅ 依赖 |
| 15 | task_executor.py | Agent | ✅ 存在 |
| 16 | exception_handler.py | Error | ✅ 存在 |
| 17 | error_templates.py | Error | ⚠️ 待评估 |
| 18 | doc_generator.py | Automation | ⚠️ 待评估 |
| 19 | auto_doc_git.py | Automation | ✅ 存在 |
| 20 | auto_docs.py | Automation | ✅ 存在 |
| 21 | auto_retry.py | Automation | ✅ 存在 |
| 22 | git_workflow_enforcer.py | Version | ✅ 存在 |
| 23 | git_monitor.py | Version | ⚠️ 待评估 |
| 24 | design_review_notifier.py | Review | ⚠️ 待评估 |
| 25 | state_machine.py | State | ✅ 存在 |
| 26 | state_validator.py | State | ⚠️ 待评估 |
| 27 | state_migrator.py | State | ⚠️ 待评估 |
| 28 | config_reloader.py | Config | ⚠️ 待评估 |
| 29 | monitor.py | Observability | ⚠️ 待评估 |
| 30 | supervisor.py | Agent | ⚠️ 待评估 |
| 31 | agent_manager.py | Agent | ⚠️ 待评估 |
| 32 | project_manager.py | Management | ⚠️ 待评估 |
| 33 | meeting_manager.py | Management | ⚠️ 待评估 |
| 34 | story_manager.py | Management | ⚠️ 待评估 |
| 35 | resource_lock.py | Lock | ⚠️ 待评估 |
| 36 | checklist_generator.py | Review | ✅ 存在 |
| 37 | daemon.py | System | ✅ 存在 |

### B. 版本历史

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| v1 | 2026-02-07 | 初始版本 |

---

**文档版本**: v1
**创建日期**: 2026-02-07
**状态**: DRAFT
